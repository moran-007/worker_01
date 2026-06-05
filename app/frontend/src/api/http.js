import { ElMessage } from 'element-plus'

export async function request(url, options = {}) {
  const isFormData = options.body instanceof FormData
  const response = await fetch(url, {
    credentials: 'include',
    headers: {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options.headers || {})
    },
    ...options
  })

  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    const message = typeof data === 'object' ? data.message || '请求失败' : '请求失败'
    if (response.status !== 401) ElMessage.error(message)
    const error = new Error(message)
    error.status = response.status
    throw error
  }

  return data
}

export const api = {
  login(payload) {
    return request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },
  logout() {
    return request('/api/auth/logout', { method: 'POST' })
  },
  me() {
    return request('/api/me')
  },
  studentMe() {
    return request('/api/student/me')
  },
  parentMe() {
    return request('/api/parent/me')
  },
  permissions() {
    return request('/api/permissions')
  },
  createRole(payload) {
    return request('/api/permissions/roles', { method: 'POST', body: JSON.stringify(payload) })
  },
  updateRoleDefinition(roleCode, payload) {
    return request(`/api/permissions/roles/${roleCode}/definition`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  updateRolePermissions(roleCode, permissions) {
    return request(`/api/permissions/roles/${roleCode}`, {
      method: 'PUT',
      body: JSON.stringify({ permissions })
    })
  },
  changeMyPassword(payload) {
    return request('/api/me/password', { method: 'POST', body: JSON.stringify(payload) })
  },
  coursePresetImportTemplateUrl: '/api/course-presets/import-template',
  dashboard() {
    return request('/api/dashboard')
  },
  students(params = {}) {
    return request(`/api/students?${new URLSearchParams(params)}`)
  },
  createStudent(payload) {
    return request('/api/students', { method: 'POST', body: JSON.stringify(payload) })
  },
  updateStudent(id, payload) {
    return request(`/api/students/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  deactivateStudent(id) {
    return request(`/api/students/${id}/deactivate`, { method: 'POST' })
  },
  teachers(params = {}) {
    return request(`/api/teachers?${new URLSearchParams(params)}`)
  },
  createTeacher(payload) {
    return request('/api/teachers', { method: 'POST', body: JSON.stringify(payload) })
  },
  updateTeacher(id, payload) {
    return request(`/api/teachers/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  deactivateTeacher(id) {
    return request(`/api/teachers/${id}/deactivate`, { method: 'POST' })
  },
  classes(params = {}) {
    return request(`/api/classes?${new URLSearchParams(params)}`)
  },
  createClass(payload) {
    return request('/api/classes', { method: 'POST', body: JSON.stringify(payload) })
  },
  updateClass(id, payload) {
    return request(`/api/classes/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  archiveClass(id) {
    return request(`/api/classes/${id}/archive`, { method: 'POST' })
  },
  generateClassLessons(classId, payload) {
    return request(`/api/classes/${classId}/lessons/generate`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },
  classStudents(classId) {
    return request(`/api/classes/${classId}/students`)
  },
  addClassStudent(classId, payload) {
    return request(`/api/classes/${classId}/students`, { method: 'POST', body: JSON.stringify(payload) })
  },
  removeClassStudent(classId, studentId) {
    return request(`/api/classes/${classId}/students/${studentId}`, { method: 'DELETE' })
  },
  lessonTypes() {
    return request('/api/lesson-types')
  },
  createLessonType(payload) {
    return request('/api/lesson-types', { method: 'POST', body: JSON.stringify(payload) })
  },
  updateLessonType(id, payload) {
    return request(`/api/lesson-types/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  coursePresets(params = {}) {
    return request(`/api/course-presets?${new URLSearchParams(params)}`)
  },
  createCoursePreset(payload) {
    return request('/api/course-presets', { method: 'POST', body: JSON.stringify(payload) })
  },
  updateCoursePreset(id, payload) {
    return request(`/api/course-presets/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  importCoursePresets(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request('/api/course-presets/import', { method: 'POST', body: formData })
  },
  lessons(params = {}) {
    return request(`/api/lessons?${new URLSearchParams(params)}`)
  },
  createLesson(payload) {
    return request('/api/lessons', { method: 'POST', body: JSON.stringify(payload) })
  },
  cancelLesson(id) {
    return request(`/api/lessons/${id}/cancel`, { method: 'POST' })
  },
  lessonAttendance(id) {
    return request(`/api/lessons/${id}/attendance`)
  },
  saveLessonAttendance(id, payload) {
    return request(`/api/lessons/${id}/attendance`, { method: 'POST', body: JSON.stringify(payload) })
  },
  lessonDetail(id) {
    return request(`/api/lessons/${id}/detail`)
  },
  saveLessonDetail(id, payload) {
    return request(`/api/lessons/${id}/detail`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  uploadLessonAsset(lessonId, formData) {
    return request(`/api/lessons/${lessonId}/assets`, { method: 'POST', body: formData })
  },
  deleteLessonAsset(lessonId, lessonAssetId) {
    return request(`/api/lessons/${lessonId}/assets/${lessonAssetId}`, { method: 'DELETE' })
  },
  scratchTemplates(params = {}) {
    return request(`/api/scratch/templates?${new URLSearchParams(params)}`)
  },
  createLessonScratchAssignment(lessonId, formData) {
    return request(`/api/lessons/${lessonId}/scratch/assignments`, { method: 'POST', body: formData })
  },
  createScratchWork(lessonId, templateId) {
    return request(`/api/lessons/${lessonId}/scratch/templates/${templateId}/work`, { method: 'POST' })
  },
  updateLessonScratchAssignment(lessonId, templateId, payload) {
    return request(`/api/lessons/${lessonId}/scratch/templates/${templateId}/assignment`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    })
  },
  unbindLessonScratchTemplate(lessonId, templateId) {
    return request(`/api/lessons/${lessonId}/scratch/templates/${templateId}`, { method: 'DELETE' })
  },
  reviewScratchWork(workId, payload) {
    return request(`/api/scratch/works/${workId}/review`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  statistics(params = {}) {
    return request(`/api/statistics?${new URLSearchParams(params)}`)
  },
  users() {
    return request('/api/users')
  },
  createUser(payload) {
    return request('/api/users', { method: 'POST', body: JSON.stringify(payload) })
  },
  updateUser(id, payload) {
    return request(`/api/users/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  logs(params = {}) {
    return request(`/api/logs?${new URLSearchParams(params)}`)
  },
  logsExportUrl(params = {}) {
    return `/api/logs/export?${new URLSearchParams(params)}`
  },
  databaseMeta() {
    return request('/api/database/meta')
  }
}
