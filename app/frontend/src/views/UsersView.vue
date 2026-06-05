<template>
  <el-card shadow="never" class="data-card">
    <template #header>
      <div class="card-header">
        <div>
          <strong>账号权限</strong>
          <p>超级管理员统一分配账号角色，角色内置细分权限点</p>
        </div>
        <div class="toolbar">
          <el-button @click="openPermissionMatrix"><el-icon><Lock /></el-icon>权限矩阵</el-button>
          <el-button @click="openCreate"><el-icon><Plus /></el-icon>新增</el-button>
          <el-button type="primary" @click="loadData"><el-icon><Refresh /></el-icon>刷新</el-button>
        </div>
      </div>
    </template>
    <el-table v-loading="loading" :data="items" class="pretty-table" empty-text="暂无账号">
      <el-table-column prop="username" label="账号" min-width="120" />
      <el-table-column prop="display_name" label="名称" min-width="120" />
      <el-table-column label="角色" width="150">
        <template #default="{ row }">{{ row.role_label || roleText(row.role) }}</template>
      </el-table-column>
      <el-table-column prop="teacher_name" label="关联教师" width="120" />
      <el-table-column prop="student_name" label="关联学生" width="130" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'warning'" effect="light" round>
            {{ row.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_login_at" label="最近登录" min-width="160" />
      <el-table-column label="操作" width="90" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-card shadow="never" class="data-card permission-editor-card">
    <template #header>
      <div class="card-header">
        <div>
          <strong>身份权限矩阵</strong>
          <p>按身份手动勾选权限；自定义身份创建后可直接分配到账号。</p>
        </div>
        <el-button type="primary" @click="refreshPermissions"><el-icon><Refresh /></el-icon>刷新权限</el-button>
      </div>
    </template>

    <el-form :model="newRole" label-position="top" class="dialog-form role-create-form">
      <el-form-item label="身份标识">
        <el-input v-model="newRole.role_code" placeholder="assistant_teacher" />
      </el-form-item>
      <el-form-item label="身份名称">
        <el-input v-model="newRole.label" placeholder="助教" />
      </el-form-item>
      <el-form-item label="等级">
        <el-input-number v-model="newRole.level" :min="1" :max="99" />
      </el-form-item>
      <el-form-item label="说明">
        <el-input v-model="newRole.note" />
      </el-form-item>
      <el-form-item label="操作">
        <el-button type="primary" :loading="roleSaving" @click="createRole">创建身份</el-button>
      </el-form-item>
    </el-form>

    <div class="permission-matrix-vue">
      <section v-for="group in groupedPermissions" :key="group.category" class="permission-block">
        <div class="permission-category-title">{{ group.category }}</div>
        <el-table :data="group.items" size="small" border>
          <el-table-column label="权限" min-width="260" fixed>
            <template #default="{ row }">
              <strong>{{ row.label }}</strong>
              <p>{{ row.key }}</p>
              <small>{{ row.description }}</small>
            </template>
          </el-table-column>
          <el-table-column v-for="role in roleOptions" :key="role.value" align="center" width="150">
            <template #header>
              <div class="role-permission-header">
                <strong>{{ role.label }}</strong>
                <small>{{ role.value }}</small>
                <el-button size="small" :disabled="role.value === 'super_admin'" @click="saveRolePermissions(role)">
                  保存
                </el-button>
              </div>
            </template>
            <template #default="{ row }">
              <el-checkbox
                :model-value="hasDraftPermission(role.value, row.key)"
                :disabled="role.value === 'super_admin'"
                @change="(checked) => togglePermission(role.value, row.key, checked)"
              />
            </template>
          </el-table-column>
        </el-table>
      </section>
    </div>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="editingId ? '编辑账号' : '新增账号'" width="680px">
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="dialog-form two-col">
      <el-form-item label="登录账号" prop="username"><el-input v-model="form.username" :disabled="Boolean(editingId)" /></el-form-item>
      <el-form-item label="显示名称" prop="display_name"><el-input v-model="form.display_name" /></el-form-item>
      <el-form-item :label="editingId ? '新密码' : '初始密码'" prop="password"><el-input v-model="form.password" type="password" show-password /></el-form-item>
      <el-form-item label="角色" prop="role">
        <el-select v-model="form.role">
          <el-option v-for="role in roleOptions" :key="role.value" :label="role.label" :value="role.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="关联教师" prop="teacher_id">
        <el-select v-model="form.teacher_id" clearable>
          <el-option v-for="teacher in teachers" :key="teacher.id" :label="teacher.name" :value="teacher.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="关联学生" prop="student_id">
        <el-select v-model="form.student_id" clearable filterable>
          <el-option v-for="student in students" :key="student.id" :label="student.name" :value="student.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="权限预览" class="form-wide">
        <div class="permission-preview">
          <div class="permission-note">{{ selectedRole?.note || '请选择角色查看权限范围' }}</div>
          <div class="permission-tags">
            <el-tag v-for="permission in previewPermissions" :key="permission.key" effect="light" round>
              {{ permission.label }}
            </el-tag>
          </div>
        </div>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="form.status">
          <el-option label="启用" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注" class="form-wide"><el-input v-model="form.remark" type="textarea" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="saveUser">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api/http'
import { requiredRule, validateForm } from '../utils/validators'
import { confirmDanger } from '../utils/confirm'

const loading = ref(false)
const saving = ref(false)
const roleSaving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const originalStatus = ref('')
const items = ref([])
const teachers = ref([])
const students = ref([])
const roleOptions = ref([])
const permissionCatalog = ref([])
const rolePermissionDrafts = reactive({})
const newRole = reactive(defaultNewRole())
const form = reactive(defaultForm())
const rules = {
  username: [requiredRule('请填写登录账号')],
  display_name: [requiredRule('请填写显示名称')],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  role: [requiredRule('请选择角色')],
  teacher_id: [{ validator: validateTeacherLink, trigger: 'change' }],
  student_id: [{ validator: validateStudentLink, trigger: 'change' }]
}

const selectedRole = computed(() => roleOptions.value.find((role) => role.value === form.role))
const permissionLabelMap = computed(() => new Map(permissionCatalog.value.map((item) => [item.key, item.label])))
const previewPermissions = computed(() =>
  (selectedRole.value?.permissions || []).map((key) => ({
    key,
    label: permissionLabelMap.value.get(key) || key
  }))
)
const groupedPermissions = computed(() => {
  const groups = new Map()
  for (const permission of permissionCatalog.value) {
    const category = permission.category || '未分类'
    if (!groups.has(category)) groups.set(category, [])
    groups.get(category).push(permission)
  }
  return [...groups.entries()].map(([category, items]) => ({ category, items }))
})

onMounted(async () => {
  const [teacherData, studentData, permissionData] = await Promise.all([
    api.teachers({ status: 'active' }),
    api.students({ status: 'active' }),
    api.permissions()
  ])
  teachers.value = teacherData.items
  students.value = studentData.items
  applyPermissionData(permissionData)
  await loadData()
})

function defaultForm() {
  return { username: '', display_name: '', password: '', role: 'academic_manager', status: 'active', teacher_id: null, student_id: null, remark: '' }
}

function defaultNewRole() {
  return { role_code: '', label: '', level: 25, note: '' }
}

function resetForm(row = null) {
  Object.assign(form, defaultForm(), row || {}, { password: '' })
}

function applyPermissionData(data) {
  roleOptions.value = data.roles
  permissionCatalog.value = data.permissions
  for (const role of data.roles) {
    rolePermissionDrafts[role.value] = [...(role.permissions || [])]
  }
}

async function refreshPermissions() {
  const data = await api.permissions()
  applyPermissionData(data)
}

async function loadData() {
  loading.value = true
  try {
    const data = await api.users()
    items.value = data.items
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  originalStatus.value = ''
  resetForm()
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

function openEdit(row) {
  editingId.value = row.id
  originalStatus.value = row.status
  resetForm(row)
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

async function saveUser() {
  const valid = await validateForm(formRef)
  if (!valid) return
  if (editingId.value && originalStatus.value === 'active' && form.status === 'inactive') {
    try {
      await confirmDanger('停用后该账号将无法登录系统。确认停用？', '停用账号')
    } catch {
      return
    }
  }
  saving.value = true
  try {
    if (editingId.value) await api.updateUser(editingId.value, form)
    else await api.createUser(form)
    ElMessage.success('账号已保存')
    dialogVisible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

function roleText(role) {
  return roleOptions.value.find((item) => item.value === role)?.label || role
}

function openPermissionMatrix() {
  window.open('http://127.0.0.1:8000/permissions', '_blank')
}

function hasDraftPermission(roleCode, permissionKey) {
  return (rolePermissionDrafts[roleCode] || []).includes(permissionKey)
}

function togglePermission(roleCode, permissionKey, checked) {
  const draft = new Set(rolePermissionDrafts[roleCode] || [])
  if (checked) draft.add(permissionKey)
  else draft.delete(permissionKey)
  rolePermissionDrafts[roleCode] = [...draft].sort()
}

async function saveRolePermissions(role) {
  if (role.value === 'super_admin') return
  await api.updateRolePermissions(role.value, rolePermissionDrafts[role.value] || [])
  ElMessage.success(`${role.label} 权限已保存`)
  await refreshPermissions()
}

async function createRole() {
  roleSaving.value = true
  try {
    await api.createRole(newRole)
    ElMessage.success('身份已创建')
    Object.assign(newRole, defaultNewRole())
    await refreshPermissions()
  } finally {
    roleSaving.value = false
  }
}

function validatePassword(_rule, value, callback) {
  const text = String(value || '').trim()
  if (!editingId.value && !text) {
    callback(new Error('请设置初始密码'))
    return
  }
  if (text && text.length < 6) {
    callback(new Error('密码至少需要 6 位'))
    return
  }
  callback()
}

function validateTeacherLink(_rule, value, callback) {
  if (form.role === 'teacher' && !value) {
    callback(new Error('老师账号必须关联教师'))
    return
  }
  callback()
}

function validateStudentLink(_rule, value, callback) {
  if ((form.role === 'student' || form.role === 'parent') && !value) {
    callback(new Error('学生/家长账号必须关联学生'))
    return
  }
  callback()
}
</script>
