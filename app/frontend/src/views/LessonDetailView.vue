<template>
  <div v-loading="loading" class="lesson-detail-page">
    <el-card shadow="never" class="data-card">
      <template #header>
        <div class="card-header">
          <div>
            <strong>{{ lesson?.class_name || '课程详情' }}</strong>
            <p>{{ lessonSubtitle }}</p>
          </div>
          <div class="toolbar">
            <el-button v-if="route.query.from" @click="backToSource">返回上课页</el-button>
            <el-button @click="backToLessons">返回课次</el-button>
            <el-button @click="goAttendance">进入签到</el-button>
            <el-button v-if="canManage" type="primary" :loading="saving" @click="saveDetail">保存详情</el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="4" border class="lesson-detail-meta">
        <el-descriptions-item label="上课日期">{{ lesson?.lesson_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ lessonTime }}</el-descriptions-item>
        <el-descriptions-item label="教师">{{ lesson?.teacher_name || '未指定' }}</el-descriptions-item>
        <el-descriptions-item label="课程类型">{{ lesson?.type_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="课程主题" :span="2">{{ lesson?.lesson_topic || '未设置主题' }}</el-descriptions-item>
        <el-descriptions-item label="教室">{{ lesson?.classroom || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ detailMeta }}</el-descriptions-item>
      </el-descriptions>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="lesson-detail-form">
        <el-form-item label="本节课内容" prop="teaching_content" class="form-wide">
          <el-input v-model="form.teaching_content" type="textarea" :autosize="{ minRows: 5, maxRows: 10 }" :disabled="!canManage" />
        </el-form-item>
        <el-form-item label="教学目标" prop="learning_goal">
          <el-input v-model="form.learning_goal" type="textarea" :autosize="{ minRows: 4, maxRows: 8 }" :disabled="!canManage" />
        </el-form-item>
        <el-form-item label="课堂表现">
          <el-input v-model="form.class_performance" type="textarea" :autosize="{ minRows: 4, maxRows: 8 }" :disabled="!canManage" />
        </el-form-item>
        <el-form-item label="课后作业">
          <el-input v-model="form.homework" type="textarea" :autosize="{ minRows: 4, maxRows: 8 }" :disabled="!canManage" />
        </el-form-item>
        <el-form-item label="下节安排">
          <el-input v-model="form.next_plan" type="textarea" :autosize="{ minRows: 4, maxRows: 8 }" :disabled="!canManage" />
        </el-form-item>
        <el-form-item label="资料与备注" class="form-wide">
          <el-input v-model="form.materials" type="textarea" :autosize="{ minRows: 3, maxRows: 7 }" :disabled="!canManage" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="data-card classroom-resource-card">
      <template #header>
        <div class="card-header">
          <div>
            <strong>课件与 Scratch 预设模板</strong>
            <p>当前课堂只维护老师上课需要的课件和预设代码模板，学生端只看到自己班级课次相关内容。</p>
          </div>
          <el-button type="primary" :disabled="!canManageScratch" @click="resetTemplateForm">新建模板</el-button>
        </div>
      </template>

      <div class="resource-workspace">
        <section class="resource-panel">
          <div class="table-title">
            <span>课件上传</span>
            <span>{{ coursewareAssets.length }} 个</span>
          </div>
          <el-form :model="assetForm" label-position="top" class="compact-form">
            <el-form-item label="课件名称">
              <el-input v-model="assetForm.title" placeholder="例如：变量计分课件" :disabled="!canManageCourseware" />
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="assetForm.note" placeholder="展示给学生的补充说明" :disabled="!canManageCourseware" />
            </el-form-item>
            <div class="scratch-upload-row">
              <label>
                <span>课件文件</span>
                <input type="file" :disabled="!canManageCourseware" @change="onCoursewareFileChange">
              </label>
              <el-button type="primary" :loading="assetSaving" :disabled="!canManageCourseware" @click="uploadCourseware">上传课件</el-button>
            </div>
          </el-form>

          <el-table :data="coursewareAssets" size="small" empty-text="暂无课件">
            <el-table-column label="课件" min-width="180">
              <template #default="{ row }">
                <strong>{{ row.title || row.original_filename }}</strong>
                <p class="muted-inline">{{ row.note || row.original_filename }}</p>
              </template>
            </el-table-column>
            <el-table-column prop="bound_at" label="上传时间" width="160" />
            <el-table-column label="操作" width="170">
              <template #default="{ row }">
                <el-button size="small" @click="openBackend(row.public_path)">打开</el-button>
                <el-button size="small" type="danger" :disabled="!canManageCourseware" @click="deleteCourseware(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>

        <section class="resource-panel">
          <div class="table-title">
            <span>Scratch 预设模板</span>
            <span>{{ scratchAssignments.length }} 个</span>
          </div>
          <el-form :model="templateForm" label-position="top" class="compact-form">
            <div class="scratch-form-grid">
              <el-form-item label="模板名称">
                <el-input v-model="templateForm.title" placeholder="例如：变量计分小游戏模板" :disabled="!canManageScratch" />
              </el-form-item>
              <el-form-item label="已有模板">
                <el-select v-model="templateForm.template_id" clearable filterable :disabled="!canManageScratch">
                  <el-option v-for="item in scratchTemplates" :key="item.id" :label="item.title" :value="item.id" />
                </el-select>
              </el-form-item>
            </div>
            <el-form-item label="给学生的说明">
              <el-input v-model="templateForm.description" type="textarea" :autosize="{ minRows: 3, maxRows: 6 }" :disabled="!canManageScratch" />
            </el-form-item>
            <div class="scratch-upload-row">
              <label>
                <span>.sb3 代码模板</span>
                <input type="file" accept=".sb3,.sb2" :disabled="!canManageScratch" @change="onTemplateFileChange">
              </label>
              <label>
                <span>缩略图</span>
                <input type="file" accept="image/*" :disabled="!canManageScratch" @change="onThumbnailFileChange">
              </label>
            </div>
            <div class="toolbar scratch-actions">
              <el-button :disabled="!canManageScratch" @click="resetTemplateForm">清空</el-button>
              <el-button type="primary" :loading="templateSaving" :disabled="!canManageScratch" @click="saveTemplate">保存模板</el-button>
            </div>
          </el-form>

          <el-table :data="scratchAssignments" size="small" empty-text="暂无 Scratch 模板">
            <el-table-column label="模板" min-width="180">
              <template #default="{ row }">
                <strong>{{ row.assignment_title || row.title }}</strong>
                <p class="muted-inline">{{ row.statement_md || row.description || '无说明' }}</p>
              </template>
            </el-table-column>
            <el-table-column label="作品" width="96">
              <template #default="{ row }">{{ Number(row.submitted_count || 0) }}/{{ Number(row.work_count || 0) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="280">
              <template #default="{ row }">
                <el-button size="small" @click="editTemplate(row)">编辑</el-button>
                <el-button size="small" type="primary" @click="openTemplateEditor(row)">进入编程</el-button>
                <el-button v-if="row.asset_url" size="small" @click="openBackend(row.asset_url)">打开</el-button>
                <el-button size="small" type="danger" :disabled="!canManageScratch" @click="unbindTemplate(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </div>

      <div class="scratch-works-section">
        <div class="table-title">
          <span>学生作品与点评</span>
          <span>{{ scratchWorks.length }} 份</span>
        </div>
        <el-table :data="scratchWorks" size="small" empty-text="学生开始模板并提交后会出现在这里">
          <el-table-column prop="student_name" label="学生" width="100" />
          <el-table-column prop="title" label="作品" min-width="180" />
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-tag size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="点评" min-width="280">
            <template #default="{ row }">
              <div v-if="workDrafts[row.id]" class="review-inline">
                <el-input-number v-model="workDrafts[row.id].score" :min="0" :max="100" size="small" controls-position="right" />
                <el-input v-model="workDrafts[row.id].review_comment" size="small" placeholder="老师点评" />
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="190">
            <template #default="{ row }">
              <el-button size="small" @click="openEditor(row)">打开</el-button>
              <el-button size="small" type="primary" :loading="reviewingId === row.id" :disabled="!canReviewScratch" @click="saveReview(row)">保存点评</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api/http'
import { requiredRule, validateForm } from '../utils/validators'
import { hasPermission } from '../utils/permissions'

const route = useRoute()
const router = useRouter()
const backendOrigin = import.meta.env.VITE_BACKEND_ORIGIN || 'http://127.0.0.1:8000'
const loading = ref(false)
const saving = ref(false)
const assetSaving = ref(false)
const templateSaving = ref(false)
const reviewingId = ref(null)
const lesson = ref(null)
const user = ref(null)
const formRef = ref(null)
const form = reactive(blankDetail())
const detail = ref(blankDetail())
const coursewareAssets = ref([])
const scratchAssignments = ref([])
const scratchWorks = ref([])
const scratchTemplates = ref([])
const workDrafts = reactive({})
const assetForm = reactive(blankAsset())
const templateForm = reactive(blankTemplate())
const rules = {
  teaching_content: [requiredRule('请填写本节课内容')],
  learning_goal: [requiredRule('请填写教学目标')]
}

const lessonSubtitle = computed(() => {
  if (!lesson.value) return '记录本节课内容、课堂表现、作业和下节安排'
  const teacher = lesson.value.teacher_name || '未指定教师'
  const topic = lesson.value.lesson_topic || '未设置主题'
  return `${lesson.value.lesson_date} ${lessonTime.value} / ${teacher} / ${topic}`
})

const lessonTime = computed(() => {
  const start = lesson.value?.start_time || '-'
  const end = lesson.value?.end_time || '-'
  return `${start}-${end}`
})

const detailMeta = computed(() => {
  if (!detail.value.updated_at) return '尚未保存'
  return `${detail.value.updated_at} / ${detail.value.updated_by || '未记录'}`
})

const canManage = computed(() => hasPermission(user.value, 'lesson_detail.manage'))
const canManageCourseware = computed(() => hasPermission(user.value, 'uploads.manage'))
const canManageScratch = computed(() => hasPermission(user.value, 'scratch.templates.manage'))
const canReviewScratch = computed(() => hasPermission(user.value, 'scratch.works.review'))

onMounted(async () => {
  await Promise.all([loadCurrentUser(), loadData()])
})

async function loadCurrentUser() {
  const data = await api.me()
  user.value = data.user
}

function blankDetail() {
  return {
    teaching_content: '',
    learning_goal: '',
    class_performance: '',
    homework: '',
    next_plan: '',
    materials: '',
    updated_by: '',
    updated_at: ''
  }
}

function blankAsset() {
  return {
    title: '',
    note: '',
    file: null
  }
}

function blankTemplate() {
  return {
    template_id: null,
    title: '',
    description: '',
    file: null,
    thumbnail: null,
    editing_template_id: null
  }
}

function applyDetail(nextDetail = {}) {
  Object.assign(form, blankDetail(), nextDetail)
  detail.value = { ...blankDetail(), ...nextDetail }
}

function applyClassroomData(data) {
  coursewareAssets.value = data.courseware_assets || []
  scratchAssignments.value = data.scratch_assignments || []
  scratchWorks.value = data.scratch_works || []
  scratchTemplates.value = data.scratch_templates || []
  for (const work of scratchWorks.value) {
    workDrafts[work.id] = {
      score: work.score ?? null,
      review_comment: work.review_comment || ''
    }
  }
}

async function loadData() {
  loading.value = true
  try {
    const data = await api.lessonDetail(route.params.id)
    lesson.value = data.lesson
    applyDetail(data.detail)
    applyClassroomData(data)
  } finally {
    loading.value = false
  }
}

async function saveDetail() {
  if (!canManage.value) return
  const valid = await validateForm(formRef)
  if (!valid) return
  saving.value = true
  try {
    const data = await api.saveLessonDetail(route.params.id, {
      teaching_content: form.teaching_content,
      learning_goal: form.learning_goal,
      class_performance: form.class_performance,
      homework: form.homework,
      next_plan: form.next_plan,
      materials: form.materials
    })
    applyDetail(data.detail)
    ElMessage.success('课程详情已保存')
  } finally {
    saving.value = false
  }
}

function onCoursewareFileChange(event) {
  assetForm.file = event.target.files?.[0] || null
}

async function uploadCourseware() {
  if (!canManageCourseware.value) return
  if (!assetForm.file) {
    ElMessage.warning('请先选择课件文件')
    return
  }
  assetSaving.value = true
  try {
    const formData = new FormData()
    formData.append('title', assetForm.title)
    formData.append('note', assetForm.note)
    formData.append('file', assetForm.file)
    await api.uploadLessonAsset(route.params.id, formData)
    Object.assign(assetForm, blankAsset())
    ElMessage.success('课件已上传')
    await loadData()
  } finally {
    assetSaving.value = false
  }
}

async function deleteCourseware(row) {
  await ElMessageBox.confirm(`确认移除「${row.title || row.original_filename}」？`, '移除课件', { type: 'warning' })
  await api.deleteLessonAsset(route.params.id, row.lesson_asset_id)
  ElMessage.success('课件已移除')
  await loadData()
}

function onTemplateFileChange(event) {
  templateForm.file = event.target.files?.[0] || null
}

function onThumbnailFileChange(event) {
  templateForm.thumbnail = event.target.files?.[0] || null
}

function resetTemplateForm() {
  Object.assign(templateForm, blankTemplate())
}

function editTemplate(row) {
  Object.assign(templateForm, blankTemplate(), {
    template_id: row.template_id,
    title: row.assignment_title || row.title || '',
    description: row.statement_md || row.description || '',
    editing_template_id: row.template_id
  })
}

async function saveTemplate() {
  if (!canManageScratch.value) return
  if (!templateForm.template_id && !templateForm.file) {
    ElMessage.warning('请选择已有模板或上传 .sb3 模板')
    return
  }
  templateSaving.value = true
  try {
    if (templateForm.editing_template_id && !templateForm.file) {
      await api.updateLessonScratchAssignment(route.params.id, templateForm.editing_template_id, buildTemplatePayload())
    } else {
      const formData = new FormData()
      const payload = buildTemplatePayload()
      for (const [key, value] of Object.entries(payload)) {
        formData.append(key, value ?? '')
      }
      if (templateForm.template_id) formData.append('template_id', templateForm.template_id)
      if (templateForm.file) formData.append('file', templateForm.file)
      if (templateForm.thumbnail) formData.append('thumbnail', templateForm.thumbnail)
      await api.createLessonScratchAssignment(route.params.id, formData)
    }
    ElMessage.success('Scratch 模板已保存')
    resetTemplateForm()
    await loadData()
  } finally {
    templateSaving.value = false
  }
}

function buildTemplatePayload() {
  return {
    title: templateForm.title,
    assignment_title: templateForm.title,
    description: templateForm.description,
    statement_md: templateForm.description,
    bind_note: templateForm.description,
    auto_judge: false,
    max_score: 100,
    judge_config_json: '',
    test_point_spec_json: ''
  }
}

async function unbindTemplate(row) {
  await ElMessageBox.confirm(`确认移除「${row.assignment_title || row.title}」？`, '移除模板', { type: 'warning' })
  await api.unbindLessonScratchTemplate(route.params.id, row.template_id)
  ElMessage.success('模板已移除')
  await loadData()
}

function openBackend(path) {
  if (!path) return
  const url = path.startsWith('http') ? path : `${backendOrigin}${path}`
  window.open(url, '_blank', 'noopener,noreferrer')
}

function openTemplateEditor(row) {
  openBackend(`/scratch/editor?template_id=${row.template_id}&return_url=${encodeURIComponent(returnUrl())}`)
}

function openEditor(work) {
  openBackend(`/scratch/editor?work_id=${work.id}&return_url=${encodeURIComponent(returnUrl())}`)
}

async function saveReview(work) {
  reviewingId.value = work.id
  try {
    const draft = workDrafts[work.id]
    await api.reviewScratchWork(work.id, {
      score: draft.score,
      review_comment: draft.review_comment
    })
    ElMessage.success('点评已保存')
    await loadData()
  } finally {
    reviewingId.value = null
  }
}

function backToLessons() {
  router.push({
    path: '/lessons',
    query: lesson.value?.lesson_date ? { date: lesson.value.lesson_date } : {}
  })
}

function backToSource() {
  router.push(safeReturnPath(route.query.from) || '/classroom')
}

function goAttendance() {
  router.push({ path: `/lessons/${route.params.id}/attendance`, query: route.query.from ? { from: route.query.from } : {} })
}

function returnUrl() {
  return safeReturnPath(route.query.from) || `/lessons/${route.params.id}/detail?from=/classroom`
}

function safeReturnPath(value) {
  const text = Array.isArray(value) ? value[0] : value
  if (!text || typeof text !== 'string') return ''
  if (!text.startsWith('/') || text.startsWith('//')) return ''
  return text
}
</script>
