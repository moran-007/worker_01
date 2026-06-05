<template>
  <el-card shadow="never" class="data-card">
    <template #header>
      <div class="card-header">
        <div>
          <strong>批量生成课次</strong>
          <p>按班级、日期范围和星期批量创建计划课次</p>
        </div>
        <div class="toolbar">
          <el-button @click="$router.push('/lessons')">返回课次</el-button>
        </div>
      </div>
    </template>

    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="dialog-form">
      <el-form-item label="班级" prop="class_id">
        <el-select v-model="form.class_id" filterable placeholder="请选择班级" @change="applyClassDefaults">
          <el-option v-for="item in classes" :key="item.id" :label="item.class_name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="开始日期" prop="start_date">
        <el-date-picker v-model="form.start_date" value-format="YYYY-MM-DD" type="date" />
      </el-form-item>
      <el-form-item label="结束日期" prop="end_date">
        <el-date-picker v-model="form.end_date" value-format="YYYY-MM-DD" type="date" />
      </el-form-item>
      <el-form-item label="上课星期" prop="weekday">
        <el-select v-model="form.weekday" placeholder="请选择星期">
          <el-option v-for="item in weekdays" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="开始时间" prop="start_time">
        <el-time-picker v-model="form.start_time" value-format="HH:mm" format="HH:mm" />
      </el-form-item>
      <el-form-item label="结束时间" prop="end_time">
        <el-time-picker v-model="form.end_time" value-format="HH:mm" format="HH:mm" />
      </el-form-item>
      <el-form-item label="上课老师" prop="teacher_id">
        <el-select v-model="form.teacher_id" filterable placeholder="请选择老师">
          <el-option v-for="item in teachers" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="课程类型">
        <el-select v-model="form.lesson_type_id" clearable placeholder="不指定">
          <el-option v-for="item in lessonTypes" :key="item.id" :label="item.type_name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="课时数量" prop="lesson_hours">
        <el-input-number v-model="form.lesson_hours" :min="0" :step="0.5" controls-position="right" />
      </el-form-item>
      <el-form-item label="课程大类">
        <el-select v-model="presetSelection.category" clearable filterable placeholder="选择某某课" @change="handlePresetCategoryChange">
          <el-option v-for="item in presetCategories" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item label="阶段">
        <el-select v-model="presetSelection.stage" clearable filterable placeholder="选择阶段" :disabled="!presetSelection.category" @change="handlePresetStageChange">
          <el-option v-for="item in presetStages" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item label="内容/标题" class="form-wide">
        <el-select v-model="form.course_preset_id" clearable filterable placeholder="选择第几节课和具体课程标题" :disabled="!presetSelection.stage" @change="handlePresetChange">
          <el-option v-for="item in filteredCoursePresets" :key="item.id" :label="presetTitleLabel(item)" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="课程主题" prop="lesson_topic" class="form-wide">
        <el-input v-model="form.lesson_topic" />
      </el-form-item>
      <el-form-item label="教室">
        <el-input v-model="form.classroom" />
      </el-form-item>
      <el-form-item label="备注" class="form-wide">
        <el-input v-model="form.remark" type="textarea" :autosize="{ minRows: 3, maxRows: 6 }" />
      </el-form-item>
    </el-form>

    <div class="generate-actions">
      <el-alert :closable="false" type="info" show-icon>
        <template #title>预计生成 {{ estimatedCount }} 节课；已存在同班级、同日期、同开始时间的课次会自动跳过。</template>
      </el-alert>
      <el-button type="primary" :loading="saving" @click="generateLessons">生成课次</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'
import { requiredRule, validateForm, validatePositiveHours } from '../utils/validators'
import { confirmDanger } from '../utils/confirm'
import { hasPermission } from '../utils/permissions'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const saving = ref(false)
const classes = ref([])
const teachers = ref([])
const lessonTypes = ref([])
const coursePresets = ref([])
const presetSelection = reactive({ category: '', stage: '' })
const weekdays = [
  { value: 1, label: '周一' },
  { value: 2, label: '周二' },
  { value: 3, label: '周三' },
  { value: 4, label: '周四' },
  { value: 5, label: '周五' },
  { value: 6, label: '周六' },
  { value: 7, label: '周日' }
]
const form = reactive(defaultForm())
const rules = {
  class_id: [requiredRule('请选择班级')],
  start_date: [requiredRule('请选择开始日期'), { validator: validateDateRange, trigger: 'change' }],
  end_date: [requiredRule('请选择结束日期'), { validator: validateDateRange, trigger: 'change' }],
  weekday: [requiredRule('请选择上课星期')],
  start_time: [requiredRule('请选择开始时间'), { validator: validateTimeRange, trigger: 'change' }],
  end_time: [requiredRule('请选择结束时间'), { validator: validateTimeRange, trigger: 'change' }],
  teacher_id: [requiredRule('请选择上课老师')],
  lesson_topic: [requiredRule('请选择预设课程或填写课程主题')],
  lesson_hours: [{ validator: validatePositiveHours, trigger: 'change' }]
}

const presetCategories = computed(() => uniqueValues(coursePresets.value.map((item) => item.category)))
const presetStages = computed(() =>
  uniqueValues(
    coursePresets.value
      .filter((item) => !presetSelection.category || item.category === presetSelection.category)
      .map((item) => item.stage)
  )
)
const filteredCoursePresets = computed(() =>
  coursePresets.value.filter(
    (item) =>
      (!presetSelection.category || item.category === presetSelection.category) &&
      (!presetSelection.stage || item.stage === presetSelection.stage)
  )
)
const estimatedCount = computed(() => countMatchingWeekdays(form.start_date, form.end_date, form.weekday))

onMounted(async () => {
  const me = await api.me()
  if (!hasPermission(me.user, 'lessons.generate')) {
    ElMessage.warning('当前账号只能查看本人课次，排课请联系管理员或教务。')
    router.replace('/lessons')
    return
  }
  const [classesData, teachersData, lessonTypesData, presetsData] = await Promise.all([
    api.classes({ status: 'active' }),
    api.teachers({ status: 'active' }),
    api.lessonTypes(),
    api.coursePresets({ status: 'active' })
  ])
  classes.value = classesData.items
  teachers.value = teachersData.items
  lessonTypes.value = lessonTypesData.items
  coursePresets.value = presetsData.items
  const classId = Number(route.query.class_id)
  if (classId) {
    form.class_id = classId
    applyClassDefaults()
  }
  if (!form.teacher_id && teachers.value.length === 1) form.teacher_id = teachers.value[0].id
})

function defaultForm() {
  const today = new Date()
  const end = new Date(today)
  end.setDate(today.getDate() + 28)
  return {
    class_id: null,
    start_date: formatDate(today),
    end_date: formatDate(end),
    weekday: null,
    start_time: '',
    end_time: '',
    teacher_id: null,
    lesson_type_id: null,
    course_preset_id: null,
    lesson_topic: '',
    lesson_hours: 1,
    classroom: '',
    remark: ''
  }
}

function applyClassDefaults() {
  const item = classes.value.find((classItem) => classItem.id === form.class_id)
  if (!item) return
  form.weekday = item.default_weekday || form.weekday
  form.start_time = item.default_start_time || form.start_time
  form.end_time = item.default_end_time || form.end_time
  form.teacher_id = item.teacher_id || form.teacher_id
}

function handlePresetCategoryChange() {
  presetSelection.stage = ''
  form.course_preset_id = null
  form.lesson_topic = ''
}

function handlePresetStageChange() {
  form.course_preset_id = null
  form.lesson_topic = ''
}

function handlePresetChange(presetId) {
  const preset = coursePresets.value.find((item) => item.id === presetId)
  if (!preset) return
  form.lesson_topic = preset.course_name
  if (preset.lesson_type_id) form.lesson_type_id = preset.lesson_type_id
  form.lesson_hours = Number(preset.default_hours || 1)
}

async function generateLessons() {
  const valid = await validateForm(formRef)
  if (!valid) return
  try {
    await confirmDanger(`确认批量生成 ${estimatedCount.value} 节课次？重复课次会跳过。`, '批量生成课次')
  } catch {
    return
  }
  saving.value = true
  try {
    const result = await api.generateClassLessons(form.class_id, form)
    ElMessage.success(`生成完成：新增 ${result.created} 节，跳过 ${result.skipped} 节`)
    router.push('/lessons')
  } finally {
    saving.value = false
  }
}

function presetTitleLabel(item) {
  return `第${item.lesson_no}节 / ${item.course_name}`
}

function uniqueValues(values) {
  return [...new Set(values.filter(Boolean))]
}

function validateDateRange(_rule, _value, callback) {
  if (form.start_date && form.end_date && form.end_date < form.start_date) {
    callback(new Error('结束日期不能早于开始日期'))
    return
  }
  callback()
}

function validateTimeRange(_rule, _value, callback) {
  if (form.start_time && form.end_time && form.end_time <= form.start_time) {
    callback(new Error('结束时间必须晚于开始时间'))
    return
  }
  callback()
}

function countMatchingWeekdays(start, end, weekday) {
  if (!start || !end || !weekday || end < start) return 0
  let count = 0
  const current = new Date(`${start}T00:00:00`)
  const last = new Date(`${end}T00:00:00`)
  while (current <= last) {
    const day = current.getDay() || 7
    if (day === weekday) count += 1
    current.setDate(current.getDate() + 1)
  }
  return count
}

function formatDate(date) {
  return date.toISOString().slice(0, 10)
}
</script>
