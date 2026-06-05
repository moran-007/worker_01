<template>
  <el-card shadow="never" class="data-card">
    <template #header>
      <div class="card-header">
        <div>
          <strong>班级列表</strong>
          <p>维护班级资料、默认老师和学生名单</p>
        </div>
        <div class="toolbar">
          <el-input v-model="filters.q" clearable placeholder="搜索班级、课程、类型" class="search-input" @keyup.enter="loadData" />
          <el-button v-if="canManageClasses" @click="openCreate"><el-icon><Plus /></el-icon>新增</el-button>
          <el-button type="primary" @click="loadData"><el-icon><Refresh /></el-icon>查询</el-button>
        </div>
      </div>
    </template>

    <el-table v-loading="loading" :data="items" class="pretty-table" empty-text="暂无班级">
      <el-table-column prop="class_name" label="班级" min-width="150" />
      <el-table-column prop="course_name" label="课程" min-width="120" />
      <el-table-column prop="class_type" label="类型" width="110" />
      <el-table-column prop="teacher_name" label="默认老师" width="120" />
      <el-table-column prop="student_count" label="学生" width="90" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag effect="light" round>{{ classStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button v-if="canManageClasses" link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="openRoster(row)">学生</el-button>
          <el-button v-if="canGenerateLessons" link type="primary" @click="openGenerate(row)">排课</el-button>
          <el-button v-if="canManageClasses && row.status !== 'archived'" link type="danger" @click="archiveClass(row)">归档</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="editingId ? '编辑班级' : '新增班级'" width="820px">
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="dialog-form">
      <el-form-item label="班级名称" prop="class_name"><el-input v-model="form.class_name" /></el-form-item>
      <el-form-item label="课程方向" prop="course_name"><el-input v-model="form.course_name" /></el-form-item>
      <el-form-item label="班级类型"><el-input v-model="form.class_type" /></el-form-item>
      <el-form-item label="默认老师">
        <el-select v-model="form.teacher_id" clearable>
          <el-option v-for="teacher in teachers" :key="teacher.id" :label="teacher.name" :value="teacher.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="默认星期">
        <el-select v-model="form.default_weekday" clearable>
          <el-option v-for="item in weekdays" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="开始时间" prop="default_start_time"><el-time-picker v-model="form.default_start_time" value-format="HH:mm" format="HH:mm" /></el-form-item>
      <el-form-item label="结束时间" prop="default_end_time"><el-time-picker v-model="form.default_end_time" value-format="HH:mm" format="HH:mm" /></el-form-item>
      <el-form-item label="容量" prop="capacity"><el-input-number v-model="form.capacity" :min="0" controls-position="right" /></el-form-item>
      <el-form-item label="开班日期" prop="start_date"><el-date-picker v-model="form.start_date" value-format="YYYY-MM-DD" type="date" /></el-form-item>
      <el-form-item label="结课日期" prop="end_date"><el-date-picker v-model="form.end_date" value-format="YYYY-MM-DD" type="date" /></el-form-item>
      <el-form-item label="状态">
        <el-select v-model="form.status">
          <el-option label="上课中" value="active" />
          <el-option label="未开班" value="pending" />
          <el-option label="暂停" value="paused" />
          <el-option label="已结课" value="closed" />
          <el-option label="已归档" value="archived" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注" class="form-wide"><el-input v-model="form.remark" type="textarea" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="saveClass">保存</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="rosterVisible" :title="`${currentClass?.class_name || ''} 学生名单`" width="780px">
    <div v-if="canManageRoster" class="toolbar roster-toolbar">
      <el-select v-model="studentToAdd" filterable placeholder="选择学生加入班级">
        <el-option v-for="student in availableStudents" :key="student.id" :label="student.name" :value="student.id" />
      </el-select>
      <el-button type="primary" @click="addStudent">加入</el-button>
    </div>
    <el-table :data="members" class="pretty-table" empty-text="暂无学生">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="parent_phone" label="家长电话" />
      <el-table-column prop="school" label="学校" />
      <el-table-column prop="join_date" label="加入日期" width="120" />
      <el-table-column v-if="canManageRoster" label="操作" width="90">
        <template #default="{ row }">
          <el-button link type="danger" @click="removeStudent(row.student_id)">移出</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'
import { requiredRule, validateForm, validateNonNegativeNumber } from '../utils/validators'
import { confirmDanger } from '../utils/confirm'
import { hasPermission } from '../utils/permissions'

const weekdays = [
  { value: 1, label: '周一' },
  { value: 2, label: '周二' },
  { value: 3, label: '周三' },
  { value: 4, label: '周四' },
  { value: 5, label: '周五' },
  { value: 6, label: '周六' },
  { value: 7, label: '周日' }
]

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const rosterVisible = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const originalStatus = ref('')
const user = ref(null)
const currentClass = ref(null)
const studentToAdd = ref(null)
const items = ref([])
const teachers = ref([])
const students = ref([])
const members = ref([])
const filters = reactive({ q: '', status: 'active' })
const form = reactive(defaultForm())
const rules = {
  class_name: [requiredRule('请填写班级名称')],
  course_name: [requiredRule('请填写课程方向')],
  capacity: [{ validator: validateNonNegativeNumber, trigger: 'change' }],
  default_start_time: [{ validator: validateClassTimeRange, trigger: 'change' }],
  default_end_time: [{ validator: validateClassTimeRange, trigger: 'change' }],
  start_date: [{ validator: validateClassDateRange, trigger: 'change' }],
  end_date: [{ validator: validateClassDateRange, trigger: 'change' }]
}

const availableStudents = computed(() => {
  const memberIds = new Set(members.value.map((item) => item.student_id))
  return students.value.filter((student) => !memberIds.has(student.id))
})
const canManageClasses = computed(() => hasPermission(user.value, 'classes.manage'))
const canManageRoster = computed(() => hasPermission(user.value, 'class_roster.manage'))
const canGenerateLessons = computed(() => hasPermission(user.value, 'lessons.generate'))

onMounted(async () => {
  await Promise.all([loadCurrentUser(), loadTeachers(), loadStudents()])
  await loadData()
})

async function loadCurrentUser() {
  const data = await api.me()
  user.value = data.user
}

function defaultForm() {
  return {
    class_name: '',
    course_name: '',
    class_type: '',
    teacher_id: null,
    default_weekday: null,
    default_start_time: '',
    default_end_time: '',
    capacity: null,
    start_date: '',
    end_date: '',
    status: 'active',
    remark: ''
  }
}

function resetForm(row = null) {
  Object.assign(form, defaultForm(), row || {})
}

async function loadData() {
  loading.value = true
  try {
    const data = await api.classes(filters)
    items.value = data.items
  } finally {
    loading.value = false
  }
}

async function loadTeachers() {
  const data = await api.teachers({ status: 'active' })
  teachers.value = data.items
}

async function loadStudents() {
  const data = await api.students({ status: 'active' })
  students.value = data.items
}

function openCreate() {
  if (!canManageClasses.value) return
  editingId.value = null
  originalStatus.value = ''
  resetForm()
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

function openEdit(row) {
  if (!canManageClasses.value) return
  editingId.value = row.id
  originalStatus.value = row.status
  resetForm(row)
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

async function saveClass() {
  if (!canManageClasses.value) return
  const valid = await validateForm(formRef)
  if (!valid) return
  if (editingId.value && originalStatus.value !== 'archived' && form.status === 'archived') {
    try {
      await confirmDanger('归档后该班级不会出现在默认班级列表中，历史课次和学生记录会保留。确认归档？', '归档班级')
    } catch {
      return
    }
  }
  saving.value = true
  try {
    if (editingId.value) await api.updateClass(editingId.value, form)
    else await api.createClass(form)
    ElMessage.success('班级信息已保存')
    dialogVisible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function openRoster(row) {
  currentClass.value = row
  studentToAdd.value = null
  rosterVisible.value = true
  await loadMembers()
}

async function loadMembers() {
  const data = await api.classStudents(currentClass.value.id)
  members.value = data.items
}

async function addStudent() {
  if (!canManageRoster.value) return
  if (!studentToAdd.value) return
  await api.addClassStudent(currentClass.value.id, { student_id: studentToAdd.value })
  ElMessage.success('学生已加入班级')
  studentToAdd.value = null
  await loadMembers()
  await loadData()
}

async function removeStudent(studentId) {
  if (!canManageRoster.value) return
  try {
    await confirmDanger('确认将该学生移出班级？历史签到和课时记录会保留。', '移出学生')
  } catch {
    return
  }
  await api.removeClassStudent(currentClass.value.id, studentId)
  ElMessage.success('学生已移出班级')
  await loadMembers()
  await loadData()
}

function openGenerate(row) {
  if (!canGenerateLessons.value) return
  router.push({ path: '/lessons/generate', query: { class_id: row.id } })
}

async function archiveClass(row) {
  if (!canManageClasses.value) return
  try {
    await confirmDanger(`确认归档班级“${row.class_name}”？历史记录会保留。`, '归档班级')
  } catch {
    return
  }
  await api.archiveClass(row.id)
  ElMessage.success('班级已归档')
  await loadData()
}

function classStatusText(status) {
  return {
    active: '上课中',
    pending: '未开班',
    paused: '暂停',
    closed: '已结课',
    archived: '已归档'
  }[status] || status
}

function validateClassDateRange(_rule, _value, callback) {
  if (form.start_date && form.end_date && form.end_date < form.start_date) {
    callback(new Error('结课日期不能早于开班日期'))
    return
  }
  callback()
}

function validateClassTimeRange(_rule, _value, callback) {
  if (form.default_start_time && form.default_end_time && form.default_end_time <= form.default_start_time) {
    callback(new Error('结束时间必须晚于开始时间'))
    return
  }
  callback()
}
</script>
