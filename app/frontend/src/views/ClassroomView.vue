<template>
  <div v-loading="loading" class="workbench-page">
    <aside class="workbench-side">
      <section class="workbench-panel hero blue">
        <span>上课入口</span>
        <strong>{{ todayLessonCount }}</strong>
        <small>今日课次</small>
      </section>
      <section class="workbench-panel">
        <div class="workbench-stat">
          <span>待签到</span>
          <strong>{{ plannedCount }}</strong>
        </div>
        <div class="workbench-stat">
          <span>已完成</span>
          <strong>{{ completedCount }}</strong>
        </div>
        <div class="workbench-stat">
          <span>待点评作品</span>
          <strong>{{ pendingReviewCount }}</strong>
        </div>
      </section>
      <section class="workbench-panel">
        <el-button type="primary" @click="router.push('/teacher/prep')">进入备课</el-button>
        <el-button plain @click="router.push('/lessons')">课次列表</el-button>
      </section>
    </aside>

    <el-card shadow="never" class="data-card workbench-main">
      <template #header>
        <div class="card-header">
          <div>
            <strong>课堂控制台</strong>
            <p>按日期进入课堂、签到、预览模板并处理学生作品。</p>
          </div>
          <div class="toolbar">
            <el-radio-group v-model="filters.scope" @change="loadData">
              <el-radio-button label="day">今日</el-radio-button>
              <el-radio-button label="week">本周</el-radio-button>
            </el-radio-group>
            <el-date-picker
              v-model="filters.date"
              value-format="YYYY-MM-DD"
              type="date"
              placeholder="选择日期"
              @change="loadData"
            />
            <el-button type="primary" @click="loadData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <div class="classroom-card-grid">
        <article v-for="lesson in lessons" :key="lesson.id" class="classroom-card">
          <div class="classroom-card-title">
            <div>
              <strong>{{ courseText(lesson) }}</strong>
              <span>{{ lesson.lesson_date }} {{ lesson.start_time || '' }}-{{ lesson.end_time || '' }}</span>
            </div>
            <el-tag :type="lessonStatusType(lesson.status)" effect="light" round>{{ lessonStatusText(lesson.status) }}</el-tag>
          </div>
          <div class="classroom-card-meta">
            <span>{{ lesson.class_name }}</span>
            <span>{{ lesson.teacher_name || '未指定教师' }}</span>
            <span>应到 {{ lesson.expected_count || 0 }} / 实到 {{ lesson.arrived_count || 0 }}</span>
          </div>
          <div class="classroom-resource-row">
            <el-tag effect="plain">课件 {{ lesson.courseware_count || 0 }}</el-tag>
            <el-tag effect="plain">模板 {{ lesson.template_count || 0 }}</el-tag>
            <el-tag effect="plain">作品 {{ lesson.work_count || 0 }}</el-tag>
          </div>
          <div class="classroom-card-actions">
            <el-button type="primary" @click="openDetail(lesson)">进入课堂</el-button>
            <el-button @click="router.push(`/lessons/${lesson.id}/attendance`)">签到</el-button>
            <el-button v-if="lesson.first_template_id" plain @click="openTemplate(lesson)">打开模板</el-button>
            <el-button plain @click="openDetail(lesson)">作品点评</el-button>
          </div>
        </article>
        <el-empty v-if="!lessons.length" description="当前范围暂无课次" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/http'

const router = useRouter()
const backendOrigin = import.meta.env.VITE_BACKEND_ORIGIN || 'http://127.0.0.1:8000'
const today = formatDate(new Date())
const loading = ref(false)
const lessons = ref([])
const filters = reactive({ scope: 'day', date: today })

const todayLessonCount = computed(() => lessons.value.filter((item) => item.lesson_date === today).length)
const plannedCount = computed(() => lessons.value.filter((item) => item.status === 'planned').length)
const completedCount = computed(() => lessons.value.filter((item) => item.status === 'completed').length)
const pendingReviewCount = computed(() =>
  lessons.value.reduce((total, item) => total + Math.max(0, Number(item.submitted_work_count || 0)), 0)
)

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const data = await api.lessons({ scope: filters.scope, date: filters.date || today })
    lessons.value = await enrichLessons(data.items || [])
  } finally {
    loading.value = false
  }
}

async function enrichLessons(items) {
  return Promise.all(items.map(async (lesson) => {
    try {
      const detail = await api.lessonDetail(lesson.id)
      const assignments = detail.scratch_assignments || []
      const works = detail.scratch_works || []
      return {
        ...lesson,
        courseware_count: (detail.courseware_assets || []).length,
        template_count: assignments.length,
        work_count: works.length,
        submitted_work_count: works.filter((work) => ['submitted', 'reviewed'].includes(work.status)).length,
        first_template_id: assignments[0]?.template_id || null
      }
    } catch {
      return lesson
    }
  }))
}

function openDetail(row) {
  router.push(`/lessons/${row.id}/detail`)
}

function openTemplate(row) {
  window.open(`${backendOrigin}/scratch/editor?template_id=${row.first_template_id}`, '_blank', 'noopener,noreferrer')
}

function courseText(row) {
  if (row.preset_course_name) {
    return `${row.course_category || ''} ${row.course_stage || ''} 第${row.course_lesson_no || '-'}节 / ${row.preset_course_name}`
  }
  return row.lesson_topic || row.course_name || '未命名课程'
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

function formatDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
</script>
