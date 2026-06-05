<template>
  <div v-loading="loading">
    <section class="metric-grid">
      <MetricCard label="今日课程" :value="summary.lesson_count" icon="Calendar" tone="blue" />
      <MetricCard label="待签到" :value="summary.pending_count" icon="Clock" tone="amber" />
      <MetricCard label="已完成" :value="summary.completed_count" icon="CircleCheck" tone="green" />
      <MetricCard label="应到人数" :value="summary.expected_total" icon="UserFilled" tone="slate" />
      <MetricCard label="实到人数" :value="summary.arrived_total" icon="Select" tone="green" />
      <MetricCard label="请假人数" :value="summary.leave_total" icon="DocumentChecked" tone="cyan" />
      <MetricCard label="缺勤人数" :value="summary.absent_total" icon="WarningFilled" tone="red" />
    </section>

    <section class="content-grid">
      <el-card shadow="never" class="data-card">
        <template #header>
          <div class="table-title">
            <span>课时不足</span>
            <el-tag type="warning" effect="light" round>{{ lowHourStudents.length }} 人</el-tag>
          </div>
        </template>
        <el-table :data="lowHourStudents" size="small" empty-text="暂无提醒">
          <el-table-column prop="student_name" label="学生" />
          <el-table-column prop="class_names" label="班级" />
          <el-table-column prop="remaining_hours" label="剩余" width="90">
            <template #default="{ row }">
              <el-tag type="danger" effect="light" round>{{ Number(row.remaining_hours).toFixed(1) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card shadow="never" class="data-card">
        <template #header>
          <div class="table-title">
            <span>今日课程</span>
            <el-button link type="primary" @click="loadData">刷新</el-button>
          </div>
        </template>
        <el-table :data="todayLessons" size="small" empty-text="今日暂无课程">
          <el-table-column prop="start_time" label="时间" width="90" />
          <el-table-column prop="class_name" label="班级" />
          <el-table-column prop="teacher_name" label="教师" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="lessonStatusType(row.status)" effect="light" round>
                {{ lessonStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </section>

    <el-card shadow="never" class="section-card data-card">
      <template #header>
        <div class="table-title">
          <span>未来 7 天待上课程</span>
          <span class="muted-text">用于快速核对排课</span>
        </div>
      </template>
      <el-table :data="upcomingLessons" empty-text="未来 7 天暂无课程">
        <el-table-column prop="lesson_date" label="日期" width="120" />
        <el-table-column prop="start_time" label="开始" width="90" />
        <el-table-column prop="class_name" label="班级" />
        <el-table-column prop="teacher_name" label="教师" width="120" />
        <el-table-column prop="type_name" label="类型" width="120" />
        <el-table-column prop="expected_count" label="应到" width="90" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import MetricCard from '../components/MetricCard.vue'
import { api } from '../api/http'

const loading = ref(false)
const summary = ref({})
const todayLessons = ref([])
const upcomingLessons = ref([])
const lowHourStudents = ref([])

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const data = await api.dashboard()
    summary.value = data.summary
    todayLessons.value = data.today_lessons
    upcomingLessons.value = data.upcoming_lessons
    lowHourStudents.value = data.low_hour_students
  } finally {
    loading.value = false
  }
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
</script>
