<template>
  <main class="portal-page">
    <header class="portal-hero">
      <div>
        <span>家长端</span>
        <h1>{{ studentName }}</h1>
        <p>只读查看孩子本人的班级、近期排课和学习记录。</p>
      </div>
      <div class="portal-actions">
        <el-button @click="loadPortal">刷新</el-button>
        <el-button type="primary" plain @click="logout">退出登录</el-button>
      </div>
    </header>

    <section class="portal-metrics">
      <article v-for="item in reportCards" :key="item.title" class="portal-metric">
        <span>{{ item.title }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.hint }}</small>
      </article>
    </section>

    <section class="portal-grid">
      <el-card shadow="never" class="portal-card">
        <template #header>
          <div class="table-title">
            <span>孩子班级</span>
            <span>{{ classes.length }} 个</span>
          </div>
        </template>
        <div class="portal-list">
          <div v-for="item in classes" :key="item.id" class="portal-list-item">
            <div>
              <strong>{{ item.class_name }}</strong>
              <span>{{ item.course_name || '课程' }} · {{ item.teacher_name || '未分配老师' }}</span>
            </div>
            <small>{{ item.class_type || '班课' }}</small>
          </div>
          <el-empty v-if="!classes.length" description="暂无班级" />
        </div>
      </el-card>

      <el-card shadow="never" class="portal-card">
        <template #header>
          <div class="table-title">
            <span>近期排课</span>
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
          <el-empty v-if="!upcomingLessons.length" description="暂无近期排课" />
        </div>
      </el-card>

      <el-card shadow="never" class="portal-card portal-wide">
        <template #header>
          <div class="table-title">
            <span>学习记录</span>
            <span>{{ recentAttendance.length }} 条</span>
          </div>
        </template>
        <el-table :data="recentAttendance" size="small" empty-text="暂无学习记录">
          <el-table-column prop="lesson_date" label="日期" width="120" />
          <el-table-column label="课程" min-width="180">
            <template #default="{ row }">{{ row.preset_course_name || row.lesson_topic || row.class_name }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column prop="teacher_name" label="老师" width="120" />
        </el-table>
      </el-card>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/http'

const router = useRouter()
const portal = ref(null)

const studentName = computed(() => portal.value?.student?.student_name || portal.value?.student?.name || '孩子学习档案')
const reportCards = computed(() => portal.value?.report_cards || [])
const classes = computed(() => portal.value?.classes || [])
const upcomingLessons = computed(() => portal.value?.upcoming_lessons || [])
const recentAttendance = computed(() => portal.value?.recent_attendance || [])

onMounted(loadPortal)

async function loadPortal() {
  const data = await api.parentMe()
  portal.value = data.portal
}

async function logout() {
  await api.logout()
  router.replace('/login')
}
</script>
