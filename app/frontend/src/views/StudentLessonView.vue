<template>
  <main class="portal-page">
    <header class="portal-hero">
      <div>
        <span>课程详情</span>
        <h1>{{ courseTitle }}</h1>
        <p>{{ lessonSubtitle }}</p>
      </div>
      <div class="portal-actions">
        <el-button @click="router.replace('/student')">返回我的上课页</el-button>
        <el-button type="primary" @click="loadLesson">刷新</el-button>
      </div>
    </header>

    <section class="portal-metrics">
      <article class="portal-metric">
        <span>课件</span>
        <strong>{{ coursewareAssets.length }}</strong>
        <small>本节课可查看资料</small>
      </article>
      <article class="portal-metric">
        <span>作品</span>
        <strong>{{ scratchTasks.length }}</strong>
        <small>老师绑定的图形化任务</small>
      </article>
      <article class="portal-metric">
        <span>状态</span>
        <strong>{{ lesson?.status === 'completed' ? '完成' : '进行' }}</strong>
        <small>{{ lesson?.class_name || '班级课程' }}</small>
      </article>
      <article class="portal-metric">
        <span>老师</span>
        <strong>{{ lesson?.teacher_name || '-' }}</strong>
        <small>{{ lesson?.classroom || '课堂' }}</small>
      </article>
    </section>

    <el-card v-loading="loading" shadow="never" class="portal-card classroom-focus-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="课件" name="courseware">
          <div class="portal-list">
            <div v-for="asset in coursewareAssets" :key="asset.lesson_asset_id" class="portal-list-item">
              <div>
                <strong>{{ asset.title || asset.original_filename }}</strong>
                <span>{{ asset.note || asset.original_filename }}</span>
              </div>
              <el-button size="small" type="primary" @click="openBackend(asset.public_path)">打开课件</el-button>
            </div>
            <el-empty v-if="!coursewareAssets.length" description="本节课暂无课件" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="知识点" name="knowledge">
          <div class="lesson-note-grid">
            <section class="lesson-note-card">
              <span>学习目标</span>
              <p>{{ detail.learning_goal || '老师暂未填写学习目标。' }}</p>
            </section>
            <section class="lesson-note-card">
              <span>本节内容</span>
              <p>{{ detail.teaching_content || '老师暂未填写本节内容。' }}</p>
            </section>
          </div>
        </el-tab-pane>

        <el-tab-pane label="详情" name="detail">
          <div class="lesson-note-grid">
            <section class="lesson-note-card">
              <span>课堂资料</span>
              <p>{{ detail.materials || '暂无补充资料。' }}</p>
            </section>
            <section class="lesson-note-card">
              <span>课后作业</span>
              <p>{{ detail.homework || '暂无课后作业。' }}</p>
            </section>
            <section class="lesson-note-card">
              <span>下节安排</span>
              <p>{{ detail.next_plan || '暂无下节安排。' }}</p>
            </section>
          </div>
        </el-tab-pane>

        <el-tab-pane label="我的作品" name="works">
          <el-table :data="scratchTasks" size="small" empty-text="老师绑定 Scratch 模板后会显示在这里">
            <el-table-column label="作品/模板" min-width="220">
              <template #default="{ row }">
                <strong>{{ row.title }}</strong>
                <p class="muted-inline">{{ row.description || row.bind_note || '进入作品后可保存进度，也可提交给老师' }}</p>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag size="small" :type="row.work_status === 'submitted' || row.work_status === 'reviewed' ? 'success' : 'info'">
                  {{ scratchStatusText(row.work_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="点评" min-width="180">
              <template #default="{ row }">{{ row.review_comment || '-' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="260">
              <template #default="{ row }">
                <el-button size="small" @click="openTemplate(row)">查看模板</el-button>
                <el-button v-if="row.work_id" size="small" type="primary" @click="openEditor(row.work_id)">编辑/提交</el-button>
                <el-button v-else size="small" type="primary" :loading="startingKey === `${row.lesson_id}-${row.template_id}`" @click="startWork(row)">开始作品</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'

const route = useRoute()
const router = useRouter()
const backendOrigin = import.meta.env.VITE_BACKEND_ORIGIN || 'http://127.0.0.1:8000'
const activeTab = ref('courseware')
const loading = ref(false)
const startingKey = ref('')
const payload = ref(null)

const lesson = computed(() => payload.value?.lesson || null)
const detail = computed(() => payload.value?.detail || {})
const coursewareAssets = computed(() => payload.value?.courseware_assets || [])
const scratchTasks = computed(() => payload.value?.scratch_tasks || [])
const courseTitle = computed(() =>
  lesson.value?.preset_course_name || lesson.value?.lesson_topic || lesson.value?.course_name || '课程详情'
)
const lessonSubtitle = computed(() => {
  if (!lesson.value) return '查看本节课课件、知识点和自己的作品'
  return `${lesson.value.lesson_date} ${lesson.value.start_time || ''}-${lesson.value.end_time || ''} / ${lesson.value.class_name}`
})

onMounted(loadLesson)

async function loadLesson() {
  loading.value = true
  try {
    payload.value = await api.studentLesson(route.params.id)
  } finally {
    loading.value = false
  }
}

async function startWork(row) {
  startingKey.value = `${row.lesson_id}-${row.template_id}`
  try {
    const data = await api.createScratchWork(row.lesson_id, row.template_id)
    ElMessage.success('作品已创建')
    openEditor(data.work.id)
    await loadLesson()
  } finally {
    startingKey.value = ''
  }
}

function returnUrl() {
  return `/student/lessons/${route.params.id}`
}

function openBackend(path) {
  if (!path) return
  window.open(path.startsWith('http') ? path : `${backendOrigin}${path}`, '_blank', 'noopener,noreferrer')
}

function openTemplate(row) {
  openBackend(`/scratch/editor?template_id=${row.template_id}&return_url=${encodeURIComponent(returnUrl())}`)
}

function openEditor(workId) {
  openBackend(`/scratch/editor?work_id=${workId}&return_url=${encodeURIComponent(returnUrl())}`)
}

function scratchStatusText(status) {
  return {
    draft: '已暂存',
    submitted: '已交老师',
    reviewed: '已点评'
  }[status] || '未开始'
}
</script>
