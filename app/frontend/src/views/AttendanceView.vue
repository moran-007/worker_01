<template>
  <div v-loading="loading">
    <el-card shadow="never" class="data-card">
      <template #header>
        <div class="card-header">
          <div>
            <strong>{{ lesson?.class_name || '班级签到' }}</strong>
            <p>{{ lesson?.lesson_date }} {{ lesson?.start_time }}-{{ lesson?.end_time }} / {{ lesson?.teacher_name || '未指定教师' }}</p>
          </div>
          <div class="toolbar">
            <el-input v-if="canManage" v-model="operator" class="search-input" placeholder="操作人" />
            <el-button v-if="route.query.from" @click="backToSource">返回上课页</el-button>
            <el-button @click="goLessonDetail">课程详情</el-button>
            <el-button v-if="canManage" @click="markAllPresent">一键全员已到</el-button>
            <el-button v-if="canManage" type="primary" :loading="saving" @click="saveAttendance">保存签到</el-button>
          </div>
        </div>
      </template>

      <el-table :data="items" class="pretty-table" empty-text="暂无学生">
        <el-table-column prop="name" label="学生" min-width="120" />
        <el-table-column prop="parent_phone" label="家长电话" min-width="130" />
        <el-table-column label="状态" width="150">
          <template #default="{ row }">
            <el-select v-model="row.status" :disabled="!canManage">
              <el-option v-for="status in statuses" :key="status" :label="status" :value="status" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="扣课时" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.deduct_hours" :min="0" :step="0.5" controls-position="right" :disabled="!canManage" />
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="180">
          <template #default="{ row }">
            <el-input v-model="row.remark" :disabled="!canManage" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'
import { hasPermission } from '../utils/permissions'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const lesson = ref(null)
const user = ref(null)
const items = ref([])
const statuses = ref([])
const operator = ref('老师')

const canManage = computed(() => hasPermission(user.value, 'attendance.manage'))

onMounted(async () => {
  await Promise.all([loadCurrentUser(), loadData()])
})

async function loadCurrentUser() {
  const data = await api.me()
  user.value = data.user
}

async function loadData() {
  loading.value = true
  try {
    const data = await api.lessonAttendance(route.params.id)
    lesson.value = data.lesson
    items.value = data.items
    statuses.value = data.statuses
  } finally {
    loading.value = false
  }
}

function markAllPresent() {
  if (!canManage.value) return
  items.value.forEach((item) => {
    item.status = '已到'
    item.deduct_hours = lesson.value?.lesson_hours || 1
  })
}

async function saveAttendance() {
  if (!canManage.value) return
  if (!operator.value.trim()) {
    ElMessage.error('请填写操作人')
    return
  }
  const invalid = items.value.find((item) => !item.status || Number(item.deduct_hours) < 0)
  if (invalid) {
    ElMessage.error('请检查签到状态和扣课时，扣课时不能小于 0')
    return
  }
  saving.value = true
  try {
    await api.saveLessonAttendance(route.params.id, {
      operator: operator.value,
      records: items.value.map((item) => ({
        student_id: item.student_id,
        status: item.status,
        deduct_hours: item.deduct_hours,
        remark: item.remark
      }))
    })
    ElMessage.success('签到已保存')
    await loadData()
  } finally {
    saving.value = false
  }
}

function goLessonDetail() {
  router.push({ path: `/lessons/${route.params.id}/detail`, query: route.query.from ? { from: route.query.from } : {} })
}

function backToSource() {
  router.push(safeReturnPath(route.query.from) || '/classroom')
}

function safeReturnPath(value) {
  const text = Array.isArray(value) ? value[0] : value
  if (!text || typeof text !== 'string') return ''
  if (!text.startsWith('/') || text.startsWith('//')) return ''
  return text
}
</script>
