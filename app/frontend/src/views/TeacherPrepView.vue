<template>
  <div v-loading="loading" class="workbench-page">
    <aside class="workbench-side">
      <section class="workbench-panel hero">
        <span>教师备课</span>
        <strong>{{ lessons.length }}</strong>
        <small>当前筛选范围内的课次</small>
      </section>
      <section class="workbench-panel">
        <div class="workbench-stat">
          <span>待补课件</span>
          <strong>{{ pendingCourseware }}</strong>
        </div>
        <div class="workbench-stat">
          <span>待绑模板</span>
          <strong>{{ pendingTemplate }}</strong>
        </div>
        <div class="workbench-stat">
          <span>有学生作品</span>
          <strong>{{ lessonsWithWorks }}</strong>
        </div>
      </section>
      <section class="workbench-panel">
        <el-button type="primary" @click="router.push('/lessons')">查看全部课次</el-button>
        <el-button plain @click="router.push('/lessons/generate')">批量排课</el-button>
      </section>
    </aside>

    <el-card shadow="never" class="data-card workbench-main">
      <template #header>
        <div class="card-header">
          <div>
            <strong>备课课次</strong>
            <p>上传课件、绑定 Scratch 预设模板、检查学生作品。</p>
          </div>
          <div class="toolbar">
            <el-radio-group v-model="filters.scope" @change="loadData">
              <el-radio-button label="day">今日</el-radio-button>
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
            </el-radio-group>
            <el-date-picker
              v-if="filters.scope !== 'month'"
              v-model="filters.date"
              value-format="YYYY-MM-DD"
              type="date"
              placeholder="选择日期"
              @change="loadData"
            />
            <el-date-picker
              v-else
              v-model="filters.month"
              value-format="YYYY-MM"
              type="month"
              placeholder="选择月份"
              @change="loadData"
            />
            <el-button type="primary" @click="loadData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="lessons" empty-text="当前范围暂无课次" class="pretty-table">
        <el-table-column label="课程信息" min-width="260">
          <template #default="{ row }">
            <strong>{{ courseText(row) }}</strong>
            <p class="muted-inline">{{ row.lesson_date }} {{ row.start_time || '' }}-{{ row.end_time || '' }} / {{ row.class_name }}</p>
          </template>
        </el-table-column>
        <el-table-column prop="teacher_name" label="教师" width="120" />
        <el-table-column label="课件" width="90">
          <template #default="{ row }">
            <el-tag :type="row.courseware_count ? 'success' : 'info'" effect="light" round>{{ row.courseware_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="模板" width="90">
          <template #default="{ row }">
            <el-tag :type="row.template_count ? 'success' : 'warning'" effect="light" round>{{ row.template_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="作品" width="110">
          <template #default="{ row }">
            {{ row.submitted_count || 0 }}/{{ row.work_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="详情" width="110">
          <template #default="{ row }">
            <el-tag :type="row.has_lesson_detail ? 'success' : 'info'" effect="light" round>
              {{ row.has_lesson_detail ? '已填写' : '待填写' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openDetail(row)">备课详情</el-button>
            <el-button v-if="row.first_template_id" size="small" @click="openTemplate(row)">打开模板</el-button>
            <el-button v-else size="small" plain @click="openDetail(row)">上传模板</el-button>
          </template>
        </el-table-column>
      </el-table>
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
const filters = reactive({ scope: 'week', date: today, month: today.slice(0, 7) })

const pendingCourseware = computed(() => lessons.value.filter((item) => !item.courseware_count).length)
const pendingTemplate = computed(() => lessons.value.filter((item) => !item.template_count).length)
const lessonsWithWorks = computed(() => lessons.value.filter((item) => Number(item.work_count || 0) > 0).length)

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const data = await api.lessons(buildQuery())
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
      return {
        ...lesson,
        courseware_count: (detail.courseware_assets || []).length,
        template_count: assignments.length,
        work_count: (detail.scratch_works || []).length,
        submitted_count: assignments.reduce((total, item) => total + Number(item.submitted_count || 0), 0),
        first_template_id: assignments[0]?.template_id || null
      }
    } catch {
      return lesson
    }
  }))
}

function buildQuery() {
  if (filters.scope === 'month') return { scope: 'month', month: filters.month || today.slice(0, 7) }
  return { scope: filters.scope, date: filters.date || today }
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

function formatDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
</script>
