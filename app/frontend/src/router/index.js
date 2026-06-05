import { createRouter, createWebHistory } from 'vue-router'
import { api } from '../api/http'
import { hasPermission } from '../utils/permissions'

const DashboardView = () => import('../views/DashboardView.vue')
const LoginView = () => import('../views/LoginView.vue')
const StudentsView = () => import('../views/StudentsView.vue')
const TeachersView = () => import('../views/TeachersView.vue')
const ClassesView = () => import('../views/ClassesView.vue')
const LessonTypesView = () => import('../views/LessonTypesView.vue')
const CoursePresetsView = () => import('../views/CoursePresetsView.vue')
const LessonsView = () => import('../views/LessonsView.vue')
const GenerateLessonsView = () => import('../views/GenerateLessonsView.vue')
const LessonDetailView = () => import('../views/LessonDetailView.vue')
const AttendanceView = () => import('../views/AttendanceView.vue')
const StatisticsView = () => import('../views/StatisticsView.vue')
const UsersView = () => import('../views/UsersView.vue')
const LogsView = () => import('../views/LogsView.vue')
const DatabaseView = () => import('../views/DatabaseView.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    { path: '/', name: 'dashboard', component: DashboardView, meta: { permission: 'dashboard.view' } },
    { path: '/students', name: 'students', component: StudentsView, meta: { permission: 'students.view' } },
    { path: '/teachers', name: 'teachers', component: TeachersView, meta: { permission: 'teachers.view' } },
    { path: '/classes', name: 'classes', component: ClassesView, meta: { permission: 'classes.view' } },
    { path: '/lesson-types', name: 'lessonTypes', component: LessonTypesView, meta: { permission: 'lesson_types.view' } },
    { path: '/course-presets', name: 'coursePresets', component: CoursePresetsView, meta: { permission: 'course_presets.view' } },
    { path: '/lessons', name: 'lessons', component: LessonsView, meta: { permission: 'lessons.view' } },
    { path: '/lessons/generate', name: 'generateLessons', component: GenerateLessonsView, meta: { permission: 'lessons.generate' } },
    { path: '/lessons/:id/detail', name: 'lessonDetail', component: LessonDetailView, meta: { permission: 'lesson_detail.view' } },
    { path: '/lessons/:id/attendance', name: 'attendance', component: AttendanceView, meta: { permission: 'attendance.view' } },
    { path: '/statistics', name: 'statistics', component: StatisticsView, meta: { permission: 'statistics.view' } },
    { path: '/users', name: 'users', component: UsersView, meta: { permission: 'users.manage' } },
    { path: '/logs', name: 'logs', component: LogsView, meta: { permission: 'logs.view' } },
    { path: '/database', name: 'database', component: DatabaseView, meta: { permission: 'database.view' } }
  ]
})

let currentUser = null
const backendOrigin = import.meta.env.VITE_BACKEND_ORIGIN || 'http://127.0.0.1:8000'

function isStudentUser(user) {
  return user?.role === 'student' || user?.permissions?.includes('student_portal.view')
}

function isParentUser(user) {
  return user?.role === 'parent' || user?.permissions?.includes('parent_portal.view')
}

router.beforeEach(async (to) => {
  if (to.meta.public) return true
  try {
    const data = await api.me()
    currentUser = data.user
  } catch {
    return { path: '/login' }
  }
  if (isStudentUser(currentUser)) {
    window.location.href = `${backendOrigin}/student`
    return false
  }
  if (isParentUser(currentUser)) {
    window.location.href = `${backendOrigin}/parent`
    return false
  }
  if (to.meta.permission && !hasPermission(currentUser, to.meta.permission)) return { path: '/' }
  return true
})

export default router
