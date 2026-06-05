<template>
  <el-card shadow="never" class="data-card">
    <template #header>
      <div class="card-header">
        <div>
          <strong>课程类型</strong>
          <p>设置默认课时和是否计入统计</p>
        </div>
        <div class="toolbar">
          <el-button v-if="canManage" @click="openCreate"><el-icon><Plus /></el-icon>新增</el-button>
          <el-button type="primary" @click="loadData"><el-icon><Refresh /></el-icon>刷新</el-button>
        </div>
      </div>
    </template>
    <el-table v-loading="loading" :data="items" class="pretty-table">
      <el-table-column prop="type_name" label="类型名称" min-width="160" />
      <el-table-column prop="default_hours" label="默认课时" width="110" />
      <el-table-column label="计入统计" width="120">
        <template #default="{ row }">
          <el-tag :type="row.count_in_statistics ? 'success' : 'warning'" effect="light" round>
            {{ row.count_in_statistics ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="220" />
      <el-table-column v-if="canManage" label="操作" width="90" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="editingId ? '编辑课程类型' : '新增课程类型'" width="520px">
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="dialog-form two-col">
      <el-form-item label="类型名称" prop="type_name"><el-input v-model="form.type_name" /></el-form-item>
      <el-form-item label="默认课时" prop="default_hours"><el-input-number v-model="form.default_hours" :min="0" :step="0.5" controls-position="right" /></el-form-item>
      <el-form-item label="计入统计"><el-switch v-model="form.count_in_statistics" /></el-form-item>
      <el-form-item label="备注" class="form-wide"><el-input v-model="form.remark" type="textarea" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="saveType">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'
import { requiredRule, validateForm, validatePositiveHours } from '../utils/validators'
import { hasPermission } from '../utils/permissions'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const user = ref(null)
const items = ref([])
const form = reactive(defaultForm())
const rules = {
  type_name: [requiredRule('请填写类型名称')],
  default_hours: [{ validator: validatePositiveHours, trigger: 'change' }]
}

const canManage = computed(() => hasPermission(user.value, 'lesson_types.manage'))

onMounted(async () => {
  await Promise.all([loadCurrentUser(), loadData()])
})

async function loadCurrentUser() {
  const data = await api.me()
  user.value = data.user
}

function defaultForm() {
  return { type_name: '', default_hours: 1, count_in_statistics: true, remark: '' }
}

function resetForm(row = null) {
  Object.assign(form, defaultForm(), row ? { ...row, count_in_statistics: Boolean(row.count_in_statistics) } : {})
}

async function loadData() {
  loading.value = true
  try {
    const data = await api.lessonTypes()
    items.value = data.items
  } finally {
    loading.value = false
  }
}

function openCreate() {
  if (!canManage.value) return
  editingId.value = null
  resetForm()
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

function openEdit(row) {
  if (!canManage.value) return
  editingId.value = row.id
  resetForm(row)
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

async function saveType() {
  if (!canManage.value) return
  const valid = await validateForm(formRef)
  if (!valid) return
  saving.value = true
  try {
    if (editingId.value) await api.updateLessonType(editingId.value, form)
    else await api.createLessonType(form)
    ElMessage.success('课程类型已保存')
    dialogVisible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}
</script>
