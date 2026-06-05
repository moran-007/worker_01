<template>
  <el-container class="app-shell">
    <el-aside width="232px" class="app-aside">
      <div class="brand">
        <div class="brand-mark">课</div>
        <div>
          <strong>课时签到</strong>
          <span>{{ user?.display_name || 'Vue 管理端' }}</span>
        </div>
      </div>
      <el-menu router :default-active="activeMenu" class="side-menu">
        <el-menu-item index="/">
          <el-icon><DataBoard /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item v-if="can('students.view')" index="/students">
          <el-icon><User /></el-icon>
          <span>学生</span>
        </el-menu-item>
        <el-menu-item v-if="can('teachers.view')" index="/teachers">
          <el-icon><Avatar /></el-icon>
          <span>教师</span>
        </el-menu-item>
        <el-menu-item v-if="can('classes.view')" index="/classes">
          <el-icon><OfficeBuilding /></el-icon>
          <span>班级</span>
        </el-menu-item>
        <el-menu-item v-if="can('lesson_types.view')" index="/lesson-types">
          <el-icon><Collection /></el-icon>
          <span>课程类型</span>
        </el-menu-item>
        <el-menu-item v-if="can('course_presets.view')" index="/course-presets">
          <el-icon><Notebook /></el-icon>
          <span>预设课程</span>
        </el-menu-item>
        <el-menu-item v-if="can('lessons.view')" index="/lessons">
          <el-icon><Calendar /></el-icon>
          <span>课次</span>
        </el-menu-item>
        <el-menu-item v-if="can('lessons.generate')" index="/lessons/generate">
          <el-icon><Calendar /></el-icon>
          <span>批量排课</span>
        </el-menu-item>
        <el-menu-item v-if="can('statistics.view')" index="/statistics">
          <el-icon><TrendCharts /></el-icon>
          <span>统计导出</span>
        </el-menu-item>
        <el-menu-item v-if="can('users.manage')" index="/users">
          <el-icon><Lock /></el-icon>
          <span>账号权限</span>
        </el-menu-item>
        <el-menu-item v-if="can('logs.view')" index="/logs">
          <el-icon><Document /></el-icon>
          <span>日志</span>
        </el-menu-item>
        <el-menu-item v-if="can('database.view')" index="/database">
          <el-icon><Coin /></el-icon>
          <span>数据库</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div>
          <h1>{{ title }}</h1>
          <p>{{ subtitle }}</p>
        </div>
        <div class="header-actions">
          <el-tag v-if="user" effect="light" round>{{ user.role_label }}</el-tag>
          <el-button plain @click="openClassic">备用入口</el-button>
          <el-button plain @click="openPasswordDialog">修改密码</el-button>
          <el-button type="primary" plain @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <el-dialog v-model="passwordVisible" title="修改密码" width="420px">
    <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-position="top">
      <el-form-item label="当前密码" prop="current_password">
        <el-input v-model="passwordForm.current_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input v-model="passwordForm.new_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirm_password">
        <el-input v-model="passwordForm.confirm_password" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="passwordVisible = false">取消</el-button>
      <el-button type="primary" :loading="passwordSaving" @click="savePassword">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'
import { requiredRule, validateForm } from '../utils/validators'
import { hasPermission } from '../utils/permissions'

const route = useRoute()
const router = useRouter()
const user = ref(null)
const passwordVisible = ref(false)
const passwordSaving = ref(false)
const passwordFormRef = ref(null)
const passwordForm = reactive(defaultPasswordForm())
const passwordRules = {
  current_password: [requiredRule('请输入当前密码')],
  new_password: [{ validator: validateNewPassword, trigger: 'blur' }],
  confirm_password: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

const titleMap = {
  '/': '工作台',
  '/students': '学生管理',
  '/teachers': '教师管理',
  '/classes': '班级管理',
  '/lesson-types': '课程类型',
  '/course-presets': '预设课程',
  '/lessons': '课次管理',
  '/lessons/generate': '批量生成课次',
  '/statistics': '统计导出',
  '/users': '账号权限',
  '/logs': '操作日志',
  '/database': '数据库关系'
}

const subtitleMap = {
  '/': '今日课程、课时提醒与近期安排',
  '/students': '学生课时、班级和联系方式快速浏览',
  '/teachers': '教师资料、授课方向和状态维护',
  '/classes': '班级资料、默认老师和学生名单维护',
  '/lesson-types': '课程类型、默认课时和是否计入统计',
  '/course-presets': '维护课程大类、阶段、节次和具体课程名称',
  '/lessons': '按日期查看课次、签到状态和到课情况',
  '/lessons/generate': '按班级、日期范围和星期批量创建计划课次',
  '/statistics': '按日、周、月或自定义范围查看和导出数据',
  '/users': '账号角色、教师关联和登录权限',
  '/logs': '系统关键操作记录',
  '/database': '面向数据库软件的表、视图和外键关系'
}

const title = computed(() => {
  if (route.name === 'lessonDetail') return '课程详情'
  if (route.name === 'attendance') return '班级签到'
  return titleMap[route.path] || '课时签到系统'
})
const can = (permission) => hasPermission(user.value, permission)
const subtitle = computed(() => {
  if (route.name === 'lessonDetail') return '记录本节课内容、课堂表现、作业和下节安排'
  if (route.name === 'attendance') return '保存学生到课状态、扣课时和签到备注'
  return subtitleMap[route.path] || 'Vue3 + Element Plus 模块化管理端'
})
const activeMenu = computed(() => {
  if (route.name === 'generateLessons') return '/lessons/generate'
  return route.path.startsWith('/lessons') ? '/lessons' : route.path
})

onMounted(async () => {
  try {
    const data = await api.me()
    user.value = data.user
  } catch (error) {
    if (error.status === 401) router.replace('/login')
  }
})

async function handleLogout() {
  await api.logout()
  ElMessage.success('已退出登录')
  router.replace('/login')
}

function openClassic() {
  window.open('http://127.0.0.1:8000', '_blank')
}

function defaultPasswordForm() {
  return { current_password: '', new_password: '', confirm_password: '' }
}

function openPasswordDialog() {
  Object.assign(passwordForm, defaultPasswordForm())
  passwordVisible.value = true
  nextTick(() => passwordFormRef.value?.clearValidate())
}

async function savePassword() {
  const valid = await validateForm(passwordFormRef)
  if (!valid) return
  passwordSaving.value = true
  try {
    await api.changeMyPassword(passwordForm)
    ElMessage.success('密码已修改')
    passwordVisible.value = false
  } finally {
    passwordSaving.value = false
  }
}

function validateNewPassword(_rule, value, callback) {
  const text = String(value || '').trim()
  if (!text) {
    callback(new Error('请输入新密码'))
    return
  }
  if (text.length < 6) {
    callback(new Error('新密码至少需要 6 位'))
    return
  }
  callback()
}

function validateConfirmPassword(_rule, value, callback) {
  if (!value) {
    callback(new Error('请再次输入新密码'))
    return
  }
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的新密码不一致'))
    return
  }
  callback()
}
</script>
