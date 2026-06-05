<template>
  <el-card shadow="never" class="data-card">
    <template #header>
      <div class="card-header">
        <div>
          <strong>预设课程</strong>
          <p>维护课程大类、阶段、节次和具体课程名称</p>
        </div>
        <div class="toolbar">
          <el-input v-model="filters.q" class="search-input" clearable placeholder="搜索课程" @keyup.enter="loadData" />
          <el-button @click="loadData">
            <el-icon><Refresh /></el-icon>
            查询
          </el-button>
          <el-button v-if="canManage" @click="downloadTemplate">下载模板</el-button>
          <el-button v-if="canManage" :loading="importing" @click="triggerImport">批量导入</el-button>
          <el-button v-if="canManage" type="primary" @click="openDialog()">新增预设</el-button>
          <input ref="fileInput" class="hidden-file" type="file" accept=".xlsx,.xlsm,.csv" @change="handleImportFile" />
        </div>
      </div>
    </template>

    <el-table v-loading="loading" :data="items" empty-text="暂无预设课程" class="pretty-table">
      <el-table-column prop="category" label="课程大类" width="130" />
      <el-table-column prop="stage" label="阶段" width="130" />
      <el-table-column label="节次" width="90">
        <template #default="{ row }">第 {{ row.lesson_no }} 节</template>
      </el-table-column>
      <el-table-column prop="course_name" label="具体课程名称" min-width="180" />
      <el-table-column prop="lesson_type_name" label="默认类型" width="120" />
      <el-table-column prop="default_hours" label="课时" width="90" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" effect="light" round>
            {{ row.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="canManage" label="操作" width="90" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑预设课程' : '新增预设课程'" width="720px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="dialog-form two-col">
        <el-form-item label="课程大类" prop="category"><el-input v-model="form.category" placeholder="Scratch / Python / C++" /></el-form-item>
        <el-form-item label="阶段" prop="stage"><el-input v-model="form.stage" placeholder="入门阶段 / 进阶阶段" /></el-form-item>
        <el-form-item label="第几节课" prop="lesson_no">
          <el-input-number v-model="form.lesson_no" :min="1" :step="1" controls-position="right" />
        </el-form-item>
        <el-form-item label="具体课程名称" prop="course_name"><el-input v-model="form.course_name" /></el-form-item>
        <el-form-item label="默认课程类型">
          <el-select v-model="form.lesson_type_id" clearable placeholder="不指定">
            <el-option v-for="type in lessonTypes" :key="type.id" :label="type.type_name" :value="type.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="默认课时" prop="default_hours">
          <el-input-number v-model="form.default_hours" :min="0" :step="0.5" controls-position="right" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" class="form-wide">
          <el-input v-model="form.remark" type="textarea" :autosize="{ minRows: 3, maxRows: 6 }" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="savePreset">保存</el-button>
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
const importing = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const fileInput = ref(null)
const formRef = ref(null)
const originalStatus = ref('')
const user = ref(null)
const items = ref([])
const lessonTypes = ref([])
const filters = reactive({ q: '', status: 'active' })
const form = reactive(blankForm())
const rules = {
  category: [requiredRule('请填写课程大类')],
  stage: [requiredRule('请填写阶段')],
  lesson_no: [requiredRule('请填写第几节课')],
  course_name: [requiredRule('请填写具体课程名称')],
  default_hours: [{ validator: validatePositiveHours, trigger: 'change' }]
}
const canManage = computed(() => hasPermission(user.value, 'course_presets.manage'))

onMounted(async () => {
  await Promise.all([loadCurrentUser(), loadData(), loadLessonTypes()])
})

async function loadCurrentUser() {
  const data = await api.me()
  user.value = data.user
}

function blankForm() {
  return {
    category: '',
    stage: '',
    lesson_no: 1,
    course_name: '',
    lesson_type_id: null,
    default_hours: 1,
    status: 'active',
    remark: ''
  }
}

async function loadData() {
  loading.value = true
  try {
    const data = await api.coursePresets(filters)
    items.value = data.items
  } finally {
    loading.value = false
  }
}

async function loadLessonTypes() {
  const data = await api.lessonTypes()
  lessonTypes.value = data.items
}

function triggerImport() {
  if (!canManage.value) return
  fileInput.value?.click()
}

function downloadTemplate() {
  window.location.href = api.coursePresetImportTemplateUrl
}

async function handleImportFile(event) {
  if (!canManage.value) return
  const file = event.target.files?.[0]
  if (!file) return
  importing.value = true
  try {
    const result = await api.importCoursePresets(file)
    ElMessage.success(`导入完成：新增 ${result.created} 条，更新 ${result.updated} 条，跳过 ${result.skipped} 条`)
    await loadData()
  } finally {
    importing.value = false
    event.target.value = ''
  }
}

function openDialog(row) {
  if (!canManage.value) return
  editingId.value = row?.id || null
  originalStatus.value = row?.status || ''
  Object.assign(form, blankForm(), row || {})
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

async function savePreset() {
  if (!canManage.value) return
  const valid = await validateForm(formRef)
  if (!valid) return
  if (editingId.value && originalStatus.value === 'active' && form.status === 'inactive') {
    try {
      await confirmDanger('停用后排课时默认不会再选择该预设课程，历史课次不受影响。确认停用？', '停用预设课程')
    } catch {
      return
    }
  }
  saving.value = true
  try {
    if (editingId.value) await api.updateCoursePreset(editingId.value, form)
    else await api.createCoursePreset(form)
    ElMessage.success('预设课程已保存')
    dialogVisible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}
</script>
