<template>
  <main class="portal-page">
    <header class="portal-hero">
      <div>
        <span>学生端</span>
        <h1>{{ studentName }}</h1>
        <p>查看自己的课程、课件和 Scratch 课堂作品。</p>
      </div>
      <div class="portal-actions">
        <el-button type="primary" @click="scrollToClassroom">进入上课</el-button>
        <el-button @click="loadPortal">刷新</el-button>
        <el-button type="primary" plain @click="logout">退出登录</el-button>
      </div>
    </header>

    <section class="portal-metrics">
      <article v-for="item in features" :key="item.title" class="portal-metric">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.hint }}</small>
      </article>
    </section>

    <section id="student-classroom" class="student-classroom-section">
      <el-card shadow="never" class="portal-card classroom-focus-card">
        <template #header>
          <div class="table-title">
            <span>我的上课任务</span>
            <span>{{ scratchTasks.length }} 个</span>
          </div>
        </template>
        <el-table :data="scratchTasks" size="small" empty-text="老师绑定 Scratch 模板后会显示在这里">
          <el-table-column label="模板/作品" min-width="210">
            <template #default="{ row }">
              <strong>{{ row.title }}</strong>
              <p class="muted-inline">{{ row.description || row.bind_note || '进入作品后可保存进度，也可提交给老师' }}</p>
            </template>
          </el-table-column>
          <el-table-column prop="class_name" label="班级" width="140" />
          <el-table-column prop="lesson_date" label="课次日期" width="120" />
          <el-table-column label="状态" width="110">
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
              <el-button v-if="row.work_id" size="small" type="primary" @click="openEditor(row.work_id)">继续编辑/提交</el-button>
              <el-button v-else size="small" type="primary" :loading="startingKey === `${row.lesson_id}-${row.template_id}`" @click="startWork(row)">开始上课</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </section>

    <section class="portal-grid">
      <el-card shadow="never" class="portal-card">
        <template #header>
          <div class="table-title">
            <span>近期课程</span>
            <span>{{ upcomingLessons.length }} 节</span>
          </div>
        </template>
        <div class="portal-list">
          <div v-for="lesson in upcomingLessons" :key="lesson.id" class="portal-list-item">
            <div>
              <strong>{{ lesson.preset_course_name || lesson.lesson_topic || lesson.course_name || '课程安排' }}</strong>
              <span>{{ lesson.lesson_date }} {{ lesson.start_time || '' }}-{{ lesson.end_time || '' }}</span>
            </div>
            <small>{{ lesson.class_name }}</small>
          </div>
          <el-empty v-if="!upcomingLessons.length" description="暂无近期课程" />
        </div>
      </el-card>

      <el-card shadow="never" class="portal-card">
        <template #header>
          <div class="table-title">
            <span>我的课件</span>
            <span>{{ coursewareAssets.length }} 个</span>
          </div>
        </template>
        <div class="portal-list">
          <div v-for="asset in coursewareAssets" :key="asset.lesson_asset_id" class="portal-list-item">
            <div>
              <strong>{{ asset.title || asset.original_filename }}</strong>
              <span>{{ asset.lesson_date }} · {{ asset.class_name }}</span>
            </div>
            <el-button size="small" @click="openBackend(asset.public_path)">下载</el-button>
          </div>
          <el-empty v-if="!coursewareAssets.length" description="暂无可下载课件" />
        </div>
      </el-card>

    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'

const router = useRouter()
const backendOrigin = import.meta.env.VITE_BACKEND_ORIGIN || 'http://127.0.0.1:8000'
const portal = ref(null)
const startingKey = ref('')

const studentName = computed(() => portal.value?.student?.student_name || portal.value?.student?.name || '学生账号')
const features = computed(() => portal.value?.student_features || [])
const upcomingLessons = computed(() => portal.value?.upcoming_lessons || [])
const coursewareAssets = computed(() => portal.value?.courseware_assets || [])
const scratchTasks = computed(() => portal.value?.scratch_tasks || [])

onMounted(loadPortal)

async function loadPortal() {
  const data = await api.studentMe()
  portal.value = data.portal
}

async function startWork(row) {
  startingKey.value = `${row.lesson_id}-${row.template_id}`
  try {
    const data = await api.createScratchWork(row.lesson_id, row.template_id)
    ElMessage.success('作品已创建')
    openEditor(data.work.id)
    await loadPortal()
  } finally {
    startingKey.value = ''
  }
}

function openBackend(path) {
  if (!path) return
  window.open(path.startsWith('http') ? path : `${backendOrigin}${path}`, '_blank', 'noopener,noreferrer')
}

function openTemplate(row) {
  openBackend(`/scratch/editor?template_id=${row.template_id}`)
}

function openEditor(workId) {
  openBackend(`/scratch/editor?work_id=${workId}`)
}

function scrollToClassroom() {
  document.getElementById('student-classroom')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function scratchStatusText(status) {
  return {
    draft: '已保存',
    submitted: '已交老师',
    reviewed: '已点评'
  }[status] || '未开始'
}

async function logout() {
  await api.logout()
  router.replace('/login')
}
</script>
