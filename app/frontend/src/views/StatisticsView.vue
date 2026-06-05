<template>
  <div>
    <el-card shadow="never" class="data-card">
      <template #header>
        <div class="card-header">
          <div>
            <strong>统计筛选</strong>
            <p>按日期范围、班级、老师和签到状态查看统计</p>
          </div>
          <div class="toolbar">
            <el-button type="primary" @click="loadData"><el-icon><Refresh /></el-icon>查询</el-button>
            <el-button @click="exportExcel"><el-icon><Download /></el-icon>导出 Excel</el-button>
          </div>
        </div>
      </template>
      <el-form ref="formRef" :model="filters" :rules="rules" label-position="top" class="filter-form">
        <el-form-item label="快捷范围">
          <el-radio-group v-model="scope" @change="applyScope">
            <el-radio-button label="day">当日</el-radio-button>
            <el-radio-button label="week">本周</el-radio-button>
            <el-radio-button label="month">本月</el-radio-button>
            <el-radio-button label="custom">自定义</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date"><el-date-picker v-model="filters.start_date" value-format="YYYY-MM-DD" type="date" @change="scope = 'custom'" /></el-form-item>
        <el-form-item label="结束日期" prop="end_date"><el-date-picker v-model="filters.end_date" value-format="YYYY-MM-DD" type="date" @change="scope = 'custom'" /></el-form-item>
        <el-form-item label="班级">
          <el-select v-model="filters.class_id" clearable>
            <el-option v-for="item in classes" :key="item.id" :label="item.class_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="老师">
          <el-select v-model="filters.teacher_id" clearable>
            <el-option v-for="item in teachers" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="签到状态">
          <el-select v-model="filters.attendance_status" clearable>
            <el-option v-for="status in statuses" :key="status" :label="status" :value="status" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <section class="metric-grid section-card">
      <MetricCard label="课次数" :value="summary.lesson_count" icon="Calendar" tone="blue" />
      <MetricCard label="应到人数" :value="summary.expected_total" icon="UserFilled" tone="slate" />
      <MetricCard label="实到人数" :value="summary.arrived_total" icon="Select" tone="green" />
      <MetricCard label="出勤率" :value="`${summary.attendance_rate || 0}%`" icon="TrendCharts" tone="cyan" />
      <MetricCard label="请假" :value="summary.leave_total" icon="DocumentChecked" tone="amber" />
      <MetricCard label="缺勤" :value="summary.absent_total" icon="WarningFilled" tone="red" />
      <MetricCard label="消耗课时" :value="summary.deduct_hours || 0" icon="Coin" tone="blue" />
    </section>

    <section class="chart-grid">
      <el-card shadow="never" class="data-card">
        <template #header>出勤率柱状图</template>
        <div class="bar-chart">
          <div v-for="item in attendanceBars" :key="item.label" class="bar-row">
            <span class="bar-label">{{ item.label }}</span>
            <div class="bar-track"><div class="bar-fill green" :style="{ width: `${item.value}%` }" /></div>
            <strong>{{ item.value }}%</strong>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="data-card">
        <template #header>老师课时图</template>
        <div class="bar-chart">
          <div v-for="item in teacherHourBars" :key="item.label" class="bar-row">
            <span class="bar-label">{{ item.label }}</span>
            <div class="bar-track"><div class="bar-fill blue" :style="{ width: `${item.percent}%` }" /></div>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </el-card>
    </section>

    <el-card shadow="never" class="data-card section-card">
      <template #header>签到明细</template>
      <el-table v-loading="loading" :data="rows" class="pretty-table" empty-text="暂无数据">
        <el-table-column prop="lesson_date" label="日期" width="120" />
        <el-table-column prop="class_name" label="班级" min-width="150" />
        <el-table-column prop="teacher_name" label="老师" width="120" />
        <el-table-column prop="student_name" label="学生" width="120" />
        <el-table-column prop="attendance_status" label="状态" width="100" />
        <el-table-column prop="deduct_hours" label="扣课时" width="100" />
        <el-table-column prop="remark" label="备注" min-width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import MetricCard from '../components/MetricCard.vue'
import { api } from '../api/http'
import { requiredRule, validateForm } from '../utils/validators'

const today = formatDate(new Date())
const thisWeek = weekRange(new Date())
const loading = ref(false)
const formRef = ref(null)
const scope = ref('week')
const summary = ref({})
const rows = ref([])
const classStats = ref([])
const teacherStats = ref([])
const classes = ref([])
const teachers = ref([])
const statuses = ['未确认', '已到', '迟到', '请假', '缺勤', '补签', '试听', '停课']
const filters = reactive({ start_date: thisWeek.start, end_date: thisWeek.end, class_id: '', teacher_id: '', attendance_status: '' })
const rules = {
  start_date: [requiredRule('请选择开始日期'), { validator: validateDateRange, trigger: 'change' }],
  end_date: [requiredRule('请选择结束日期'), { validator: validateDateRange, trigger: 'change' }]
}

const attendanceBars = computed(() => {
  const bars = classStats.value.map((item) => {
    const total = Number(item.arrived || 0) + Number(item.leave || 0) + Number(item.absent || 0)
    const value = total ? Math.round((Number(item.arrived || 0) / total) * 1000) / 10 : 0
    return { label: item.class_name, value }
  })
  if (bars.length) return bars.slice(0, 8)
  return [{ label: '总体出勤率', value: Number(summary.value.attendance_rate || 0) }]
})

const teacherHourBars = computed(() => {
  const max = Math.max(...teacherStats.value.map((item) => Number(item.deduct_hours || 0)), 1)
  return teacherStats.value
    .map((item) => ({
      label: item.teacher_name,
      value: Number(item.deduct_hours || 0).toFixed(1),
      percent: Math.round((Number(item.deduct_hours || 0) / max) * 100)
    }))
    .slice(0, 8)
})

onMounted(async () => {
  const [classData, teacherData] = await Promise.all([api.classes({ status: '' }), api.teachers({ status: '' })])
  classes.value = classData.items
  teachers.value = teacherData.items
  await loadData()
})

async function loadData() {
  const valid = await validateForm(formRef)
  if (!valid) return
  loading.value = true
  try {
    const data = await api.statistics(filters)
    summary.value = data.summary
    rows.value = data.rows
    classStats.value = data.class_stats || []
    teacherStats.value = data.teacher_stats || []
  } finally {
    loading.value = false
  }
}

async function exportExcel() {
  const valid = await validateForm(formRef)
  if (!valid) return
  const params = new URLSearchParams(filters)
  window.open(`http://127.0.0.1:8000/exports/attendance?${params}`, '_blank')
}

function validateDateRange(_rule, _value, callback) {
  if (filters.start_date && filters.end_date && filters.end_date < filters.start_date) {
    callback(new Error('结束日期不能早于开始日期'))
    return
  }
  callback()
}

function applyScope() {
  if (scope.value === 'custom') return
  const now = new Date()
  if (scope.value === 'day') {
    filters.start_date = today
    filters.end_date = today
    return
  }
  if (scope.value === 'month') {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
    filters.start_date = formatDate(start)
    filters.end_date = formatDate(end)
    return
  }
  const range = weekRange(now)
  filters.start_date = range.start
  filters.end_date = range.end
}

function weekRange(baseDate) {
  const start = new Date(baseDate)
  start.setDate(baseDate.getDate() - ((baseDate.getDay() + 6) % 7))
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  return { start: formatDate(start), end: formatDate(end) }
}

function formatDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
</script>
