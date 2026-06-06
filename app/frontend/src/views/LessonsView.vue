<template>
  <el-card shadow="never" class="data-card">
    <template #header>
      <div class="card-header">
        <div>
          <strong>课次列表</strong>
          <p>按日期查看班级课程、教师和签到状态</p>
        </div>
        <div class="toolbar">
          <el-radio-group v-model="filters.scope" @change="handleScopeChange">
            <el-radio-button label="day">当日</el-radio-button>
            <el-radio-button label="week">本周</el-radio-button>
            <el-radio-button label="month">本月</el-radio-button>
            <el-radio-button label="custom">自定义</el-radio-button>
          </el-radio-group>
          <el-date-picker
            v-if="filters.scope === 'day' || filters.scope === 'week'"
            v-model="filters.date"
            value-format="YYYY-MM-DD"
            type="date"
            :placeholder="filters.scope === 'week' ? '选择周内日期' : '选择日期'"
          />
          <el-date-picker
            v-else-if="filters.scope === 'month'"
            v-model="filters.month"
            value-format="YYYY-MM"
            type="month"
            placeholder="选择月份"
          />
          <template v-else>
            <el-date-picker v-model="filters.start_date" value-format="YYYY-MM-DD" type="date" placeholder="开始日期" />
            <el-date-picker v-model="filters.end_date" value-format="YYYY-MM-DD" type="date" placeholder="结束日期" />
          </template>
          <el-button type="primary" @click="loadData">
            <el-icon><Refresh /></el-icon>
            查询
          </el-button>
          <el-button v-if="canGenerateLessons" @click="$router.push('/lessons/generate')">批量生成</el-button>
          <el-button v-if="canManageLessons" type="primary" plain @click="openCreateDialog">新增课次</el-button>
        </div>
      </div>
    </template>
    <el-table v-loading="loading" :data="items" empty-text="暂无课次" class="pretty-table">
      <el-table-column prop="lesson_date" label="日期" width="120" />
      <el-table-column prop="start_time" label="开始" width="90" />
      <el-table-column prop="end_time" label="结束" width="90" />
      <el-table-column prop="class_name" label="班级" min-width="160" />
      <el-table-column prop="teacher_name" label="教师" width="120" />
      <el-table-column prop="type_name" label="类型" width="120" />
      <el-table-column label="课程" min-width="190">
        <template #default="{ row }">
          <span>{{ courseText(row) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="应到/实到" width="120">
        <template #default="{ row }">
          <span class="ratio-text">{{ row.arrived_count }}/{{ row.expected_count }}</span>
        </template>
      </el-table-column>
      <el-table-column label="课程详情" width="110">
        <template #default="{ row }">
          <el-tag :type="row.has_lesson_detail ? 'success' : 'info'" effect="light" round>
            {{ row.has_lesson_detail ? '已填写' : '待填写' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="lessonStatusType(row.status)" effect="light" round>
            {{ lessonStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="210" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="$router.push(`/lessons/${row.id}/detail`)">备课</el-button>
          <el-button link type="success" @click="$router.push(`/lessons/${row.id}/detail`)">上课</el-button>
          <el-button link type="primary" @click="$router.push(`/lessons/${row.id}/attendance`)">签到</el-button>
          <el-button v-if="canManageLessons && row.status !== 'cancelled'" link type="danger" @click="cancelLesson(row)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="新增课次" width="760px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="dialog-form two-col">
        <el-form-item label="班级" prop="class_id">
          <el-select v-model="form.class_id" filterable placeholder="请选择班级">
            <el-option v-for="item in classes" :key="item.id" :label="item.class_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课日期" prop="lesson_date">
          <el-date-picker v-model="form.lesson_date" value-format="YYYY-MM-DD" type="date" />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time"><el-time-picker v-model="form.start_time" value-format="HH:mm" format="HH:mm" /></el-form-item>
        <el-form-item label="结束时间" prop="end_time"><el-time-picker v-model="form.end_time" value-format="HH:mm" format="HH:mm" /></el-form-item>
        <el-form-item label="上课老师" prop="teacher_id">
          <el-select v-model="form.teacher_id" clearable filterable placeholder="未指定">
            <el-option v-for="item in teachers" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程类型">
          <el-select v-model="form.lesson_type_id" clearable>
            <el-option v-for="item in lessonTypes" :key="item.id" :label="item.type_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程大类">
          <el-select v-model="presetSelection.category" clearable filterable placeholder="选择某某课" @change="handlePresetCategoryChange">
            <el-option v-for="item in presetCategories" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="阶段">
          <el-select v-model="presetSelection.stage" clearable filterable placeholder="选择阶段" :disabled="!presetSelection.category" @change="handlePresetStageChange">
            <el-option v-for="item in presetStages" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容/标题" class="form-wide">
          <el-select v-model="form.course_preset_id" clearable filterable placeholder="选择第几节课和具体课程标题" :disabled="!presetSelection.stage" @change="handlePresetChange">
            <el-option v-for="item in filteredCoursePresets" :key="item.id" :label="presetTitleLabel(item)" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程主题" prop="lesson_topic" class="form-wide"><el-input v-model="form.lesson_topic" /></el-form-item>
        <el-form-item label="课时数量" prop="lesson_hours">
          <el-input-number v-model="form.lesson_hours" :min="0" :step="0.5" controls-position="right" />
        </el-form-item>
        <el-form-item label="教室"><el-input v-model="form.classroom" /></el-form-item>
        <el-form-item label="备注" class="form-wide">
          <el-input v-model="form.remark" type="textarea" :autosize="{ minRows: 3, maxRows: 6 }" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveLesson">保存课次</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'
import { requiredRule, validateForm, validatePositiveHours } from '../utils/validators'
import { confirmDanger } from '../utils/confirm'
import { hasPermission } from '../utils/permissions'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const items = ref([])
const classes = ref([])
const teachers = ref([])
const lessonTypes = ref([])
const coursePresets = ref([])
const user = ref(null)
const today = formatDate(new Date())
const filters = reactive({ scope: 'week', date: today, month: today.slice(0, 7), start_date: '', end_date: '' })
const form = reactive(blankForm())
const rules = {
  class_id: [requiredRule('请选择班级')],
  lesson_date: [requiredRule('请选择上课日期')],
  start_time: [requiredRule('请选择开始时间'), { validator: validateLessonTimeRange, trigger: 'change' }],
  end_time: [requiredRule('请选择结束时间'), { validator: validateLessonTimeRange, trigger: 'change' }],
  teacher_id: [requiredRule('请选择上课老师')],
  lesson_topic: [requiredRule('请选择预设课程或填写课程主题')],
  lesson_hours: [{ validator: validatePositiveHours, trigger: 'change' }]
}
const presetSelection = reactive({ category: '', stage: '' })
const presetCategories = computed(() => uniqueValues(coursePresets.value.map((item) => item.category)))
const presetStages = computed(() =>
  uniqueValues(
    coursePresets.value
      .filter((item) => !presetSelection.category || item.category === presetSelection.category)
      .map((item) => item.stage)
  )
)
const filteredCoursePresets = computed(() =>
  coursePresets.value.filter(
    (item) =>
      (!presetSelection.category || item.category === presetSelection.category) &&
      (!presetSelection.stage || item.stage === presetSelection.stage)
  )
)
const canManageLessons = computed(() => hasPermission(user.value, 'lessons.manage'))
const canGenerateLessons = computed(() => hasPermission(user.value, 'lessons.generate'))

onMounted(async () => {
  await Promise.all([loadCurrentUser(), loadData(), loadOptions()])
})

function blankForm() {
  return {
    class_id: null,
    lesson_date: filters.date || today,
    start_time: '',
    end_time: '',
    teacher_id: null,
    lesson_type_id: null,
    course_preset_id: null,
    lesson_topic: '',
    lesson_hours: 1,
    classroom: '',
    remark: ''
  }
}

async function loadData() {
  if (filters.scope === 'custom' && filters.start_date && filters.end_date && filters.end_date < filters.start_date) {
    ElMessage.error('结束日期不能早于开始日期')
    return
  }
  loading.value = true
  try {
    const data = await api.lessons(lessonQueryParams())
    items.value = data.items
  } finally {
    loading.value = false
  }
}

async function loadCurrentUser() {
  const data = await api.me()
  user.value = data.user
}

async function loadOptions() {
  const [classesData, teachersData, lessonTypesData, presetsData] = await Promise.all([
    api.classes({ status: 'active' }),
    api.teachers({ status: 'active' }),
    api.lessonTypes(),
    api.coursePresets({ status: 'active' })
  ])
  classes.value = classesData.items
  teachers.value = teachersData.items
  lessonTypes.value = lessonTypesData.items
  coursePresets.value = presetsData.items
  fillDefaultTeacher()
}

function openCreateDialog() {
  if (!canManageLessons.value) return
  Object.assign(form, blankForm(), { lesson_date: filters.date || today })
  Object.assign(presetSelection, { category: '', stage: '' })
  fillDefaultTeacher()
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

function handlePresetCategoryChange() {
  presetSelection.stage = ''
  form.course_preset_id = null
  form.lesson_topic = ''
}

function handlePresetStageChange() {
  form.course_preset_id = null
  form.lesson_topic = ''
}

function handlePresetChange(presetId) {
  const preset = coursePresets.value.find((item) => item.id === presetId)
  if (!preset) return
  form.lesson_topic = preset.course_name
  if (preset.lesson_type_id) form.lesson_type_id = preset.lesson_type_id
  form.lesson_hours = Number(preset.default_hours || 1)
}

async function saveLesson() {
  if (!canManageLessons.value) return
  const valid = await validateForm(formRef)
  if (!valid) return
  saving.value = true
  try {
    await api.createLesson(form)
    ElMessage.success('课次已保存')
    dialogVisible.value = false
    filters.scope = 'week'
    filters.date = form.lesson_date
    await loadData()
  } finally {
    saving.value = false
  }
}

function presetLabel(item) {
  return `${item.category} / ${item.stage} / 第${item.lesson_no}节 / ${item.course_name}`
}

function presetTitleLabel(item) {
  return `第${item.lesson_no}节 / ${item.course_name}`
}

function courseText(row) {
  if (row.preset_course_name) {
    return `${row.course_category} / ${row.course_stage} / 第${row.course_lesson_no}节 / ${row.preset_course_name}`
  }
  return row.lesson_topic || '-'
}

function uniqueValues(values) {
  return [...new Set(values.filter(Boolean))]
}

function fillDefaultTeacher() {
  if (!form.teacher_id && teachers.value.length === 1) {
    form.teacher_id = teachers.value[0].id
  }
}

function lessonStatusText(status) {
  return {
    planned: '待签到',
    completed: '已完成',
    cancelled: '已取消'
  }[status] || status
}

function lessonStatusType(status) {
  return {
    planned: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }[status] || 'info'
}

async function cancelLesson(row) {
  if (!canManageLessons.value) return
  try {
    await confirmDanger(`确认取消 ${row.lesson_date} ${row.class_name} 的课次？`, '取消课次')
  } catch {
    return
  }
  await api.cancelLesson(row.id)
  ElMessage.success('课次已取消')
  await loadData()
}

function handleScopeChange() {
  if (filters.scope === 'custom' && (!filters.start_date || !filters.end_date)) {
    const { start, end } = weekRange(new Date())
    filters.start_date = start
    filters.end_date = end
  }
}

function lessonQueryParams() {
  const params = { scope: filters.scope }
  if (filters.scope === 'month') {
    params.month = filters.month || today.slice(0, 7)
  } else if (filters.scope === 'custom') {
    params.start_date = filters.start_date
    params.end_date = filters.end_date
  } else {
    params.date = filters.date || today
  }
  return params
}

function weekRange(baseDate) {
  const start = new Date(baseDate)
  start.setDate(baseDate.getDate() - ((baseDate.getDay() + 6) % 7))
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  return { start: formatDate(start), end: formatDate(end) }
}

function formatDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function validateLessonTimeRange(_rule, _value, callback) {
  if (form.start_time && form.end_time && form.end_time <= form.start_time) {
    callback(new Error('结束时间必须晚于开始时间'))
    return
  }
  callback()
}
</script>
