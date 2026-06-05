<template>
  <el-card shadow="never" class="data-card">
    <template #header>
      <div class="card-header">
        <div>
          <strong>学生列表</strong>
          <p>快速查看联系方式、所在班级和课时余额</p>
        </div>
        <div class="toolbar">
          <el-input v-model="filters.q" clearable placeholder="搜索姓名或电话" class="search-input" @keyup.enter="loadData">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button v-if="canManage" @click="openCreate">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button type="primary" @click="loadData">
            <el-icon><Refresh /></el-icon>
            查询
          </el-button>
        </div>
      </div>
    </template>
    <el-table v-loading="loading" :data="items" empty-text="暂无学生" class="pretty-table">
      <el-table-column prop="name" label="姓名" min-width="120" />
      <el-table-column prop="parent_phone" label="家长电话" min-width="130" />
      <el-table-column prop="class_names" label="班级" min-width="180" />
      <el-table-column label="课时余额" width="110">
        <template #default="{ row }">
          <el-tag :type="remainingHours(row) <= 2 ? 'danger' : 'success'" effect="light" round>
            {{ remainingHours(row).toFixed(1) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'warning'" effect="light" round>
            {{ row.status === 'active' ? '在读' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="canManage" label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button v-if="row.status === 'active'" link type="danger" @click="deactivateStudent(row)">停用</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="editingId ? '编辑学生' : '新增学生'" width="720px">
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="dialog-form">
      <el-form-item label="姓名" prop="name"><el-input v-model="form.name" /></el-form-item>
      <el-form-item label="性别"><el-input v-model="form.gender" /></el-form-item>
      <el-form-item label="年龄"><el-input-number v-model="form.age" :min="0" controls-position="right" /></el-form-item>
      <el-form-item label="联系电话" prop="phone"><el-input v-model="form.phone" /></el-form-item>
      <el-form-item label="家长姓名"><el-input v-model="form.parent_name" /></el-form-item>
      <el-form-item label="家长电话" prop="parent_phone"><el-input v-model="form.parent_phone" /></el-form-item>
      <el-form-item label="学校"><el-input v-model="form.school" /></el-form-item>
      <el-form-item label="购买课时" prop="purchased_hours"><el-input-number v-model="form.purchased_hours" :min="0" :step="0.5" controls-position="right" /></el-form-item>
      <el-form-item label="赠送课时" prop="gift_hours"><el-input-number v-model="form.gift_hours" :min="0" :step="0.5" controls-position="right" /></el-form-item>
      <el-form-item label="状态">
        <el-select v-model="form.status">
          <el-option label="在读" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注" class="form-wide"><el-input v-model="form.remark" type="textarea" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="saveStudent">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'
import { requiredRule, validateForm, validateNonNegativeNumber, validatePhone } from '../utils/validators'
import { confirmDanger } from '../utils/confirm'
import { hasPermission } from '../utils/permissions'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const originalStatus = ref('')
const user = ref(null)
const items = ref([])
const filters = reactive({ q: '', status: 'active' })
const form = reactive(defaultForm())
const rules = {
  name: [requiredRule('请填写学生姓名')],
  phone: [{ validator: validatePhone, trigger: 'blur' }],
  parent_phone: [requiredRule('请填写家长电话'), { validator: validatePhone, trigger: 'blur' }],
  purchased_hours: [{ validator: validateNonNegativeNumber, trigger: 'change' }],
  gift_hours: [{ validator: validateNonNegativeNumber, trigger: 'change' }]
}

const canManage = computed(() => hasPermission(user.value, 'students.manage'))

onMounted(async () => {
  await Promise.all([loadCurrentUser(), loadData()])
})

async function loadCurrentUser() {
  const data = await api.me()
  user.value = data.user
}

async function loadData() {
  loading.value = true
  try {
    const data = await api.students(filters)
    items.value = data.items
  } finally {
    loading.value = false
  }
}

function remainingHours(row) {
  return Number(row.purchased_hours + row.gift_hours - row.consumed_hours)
}

function defaultForm() {
  return {
    name: '',
    gender: '',
    age: null,
    phone: '',
    parent_name: '',
    parent_phone: '',
    school: '',
    purchased_hours: 0,
    gift_hours: 0,
    status: 'active',
    remark: ''
  }
}

function resetForm(row = null) {
  Object.assign(form, defaultForm(), row || {})
}

function openCreate() {
  if (!canManage.value) return
  editingId.value = null
  originalStatus.value = ''
  resetForm()
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

function openEdit(row) {
  if (!canManage.value) return
  editingId.value = row.id
  originalStatus.value = row.status
  resetForm(row)
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

async function saveStudent() {
  if (!canManage.value) return
  const valid = await validateForm(formRef)
  if (!valid) return
  if (editingId.value && originalStatus.value === 'active' && form.status === 'inactive') {
    try {
      await confirmDanger('停用后该学生不会出现在默认在读列表中，历史签到和课时记录会保留。确认停用？', '停用学生')
    } catch {
      return
    }
  }
  saving.value = true
  try {
    if (editingId.value) {
      await api.updateStudent(editingId.value, form)
    } else {
      await api.createStudent(form)
    }
    ElMessage.success('学生信息已保存')
    dialogVisible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function deactivateStudent(row) {
  if (!canManage.value) return
  try {
    await confirmDanger(`确认停用学生“${row.name}”？历史记录会保留。`, '停用学生')
  } catch {
    return
  }
  await api.deactivateStudent(row.id)
  ElMessage.success('学生已停用')
  await loadData()
}
</script>
