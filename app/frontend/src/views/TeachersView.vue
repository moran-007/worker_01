<template>
  <el-card shadow="never" class="data-card">
    <template #header>
      <div class="card-header">
        <div>
          <strong>教师列表</strong>
          <p>维护教师资料、授课方向和状态</p>
        </div>
        <div class="toolbar">
          <el-input v-model="filters.q" clearable placeholder="搜索姓名、电话、方向" class="search-input" @keyup.enter="loadData" />
          <el-button v-if="canManage" @click="openCreate"><el-icon><Plus /></el-icon>新增</el-button>
          <el-button type="primary" @click="loadData"><el-icon><Refresh /></el-icon>查询</el-button>
        </div>
      </div>
    </template>

    <el-table v-loading="loading" :data="items" class="pretty-table" empty-text="暂无教师">
      <el-table-column prop="name" label="教师" min-width="120" />
      <el-table-column prop="phone" label="手机号" min-width="130" />
      <el-table-column prop="subject" label="任教方向" min-width="140" />
      <el-table-column prop="lesson_count" label="课次" width="90" />
      <el-table-column prop="lesson_hours" label="课时" width="90" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'warning'" effect="light" round>
            {{ row.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="canManage" label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button v-if="row.status === 'active'" link type="danger" @click="deactivateTeacher(row)">停用</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="editingId ? '编辑教师' : '新增教师'" width="560px">
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="dialog-form two-col">
      <el-form-item label="教师姓名" prop="name"><el-input v-model="form.name" /></el-form-item>
      <el-form-item label="手机号" prop="phone"><el-input v-model="form.phone" /></el-form-item>
      <el-form-item label="任教方向"><el-input v-model="form.subject" /></el-form-item>
      <el-form-item label="状态">
        <el-select v-model="form.status">
          <el-option label="启用" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注" class="form-wide"><el-input v-model="form.remark" type="textarea" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="saveTeacher">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'
import { requiredRule, validateForm, validatePhone } from '../utils/validators'
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
  name: [requiredRule('请填写教师姓名')],
  phone: [requiredRule('请填写手机号'), { validator: validatePhone, trigger: 'blur' }]
}

const canManage = computed(() => hasPermission(user.value, 'teachers.manage'))

onMounted(async () => {
  await Promise.all([loadCurrentUser(), loadData()])
})

async function loadCurrentUser() {
  const data = await api.me()
  user.value = data.user
}

function defaultForm() {
  return { name: '', phone: '', subject: '', status: 'active', remark: '' }
}

function resetForm(row = null) {
  Object.assign(form, defaultForm(), row || {})
}

async function loadData() {
  loading.value = true
  try {
    const data = await api.teachers(filters)
    items.value = data.items
  } finally {
    loading.value = false
  }
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

async function saveTeacher() {
  if (!canManage.value) return
  const valid = await validateForm(formRef)
  if (!valid) return
  if (editingId.value && originalStatus.value === 'active' && form.status === 'inactive') {
    try {
      await confirmDanger('停用后该教师不会出现在默认启用教师列表中，历史课次会保留。确认停用？', '停用教师')
    } catch {
      return
    }
  }
  saving.value = true
  try {
    if (editingId.value) await api.updateTeacher(editingId.value, form)
    else await api.createTeacher(form)
    ElMessage.success('教师信息已保存')
    dialogVisible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function deactivateTeacher(row) {
  if (!canManage.value) return
  try {
    await confirmDanger(`确认停用教师“${row.name}”？历史课次会保留。`, '停用教师')
  } catch {
    return
  }
  await api.deactivateTeacher(row.id)
  ElMessage.success('教师已停用')
  await loadData()
}
</script>
