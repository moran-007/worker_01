<template>
  <main class="login-page">
    <section class="login-copy">
      <span>Class Attendance</span>
      <h1>课时签到管理系统</h1>
      <p>面向培训校区的排课、签到、统计和课时管理工作台。</p>
      <div class="login-points">
        <span>局域网访问</span>
        <span>SQLite 本地数据</span>
        <span>Excel 导出</span>
      </div>
    </section>

    <el-card class="login-card" shadow="never">
      <div class="login-title">
        <span>校区内部系统</span>
        <h2>账号登录</h2>
        <p>默认管理员：admin / admin123</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleLogin">
        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" autofocus />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-button type="primary" class="full-button" :loading="loading" @click="handleLogin">
          登录系统
        </el-button>
      </el-form>
    </el-card>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'
import { requiredRule, validateForm } from '../utils/validators'

const router = useRouter()
const loading = ref(false)
const formRef = ref(null)
const form = reactive({
  username: 'admin',
  password: ''
})
const rules = {
  username: [requiredRule('请输入账号')],
  password: [requiredRule('请输入密码')]
}
function isStudentUser(user) {
  return user?.role === 'student' || user?.permissions?.includes('student_portal.view')
}

function isParentUser(user) {
  return user?.role === 'parent' || user?.permissions?.includes('parent_portal.view')
}

async function handleLogin() {
  const valid = await validateForm(formRef)
  if (!valid) return
  loading.value = true
  try {
    const data = await api.login(form)
    ElMessage.success('登录成功')
    if (isStudentUser(data.user)) {
      router.replace('/student')
      return
    }
    if (isParentUser(data.user)) {
      router.replace('/parent')
      return
    }
    router.replace('/')
  } catch {
    ElMessage.error('账号或密码错误')
  } finally {
    loading.value = false
  }
}
</script>
