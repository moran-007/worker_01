<template>
  <el-card shadow="never" class="data-card">
    <template #header>
      <div class="card-header">
        <div>
          <strong>操作日志</strong>
          <p>查看登录、排课、签到和数据维护记录</p>
        </div>
        <div class="toolbar">
          <el-input v-model="filters.q" clearable placeholder="搜索动作、账号、详情" class="search-input" @keyup.enter="loadData" />
          <el-button type="primary" @click="loadData"><el-icon><Search /></el-icon>查询</el-button>
          <el-button @click="exportLogs"><el-icon><Download /></el-icon>导出 Excel</el-button>
        </div>
      </div>
    </template>
    <el-form ref="formRef" :model="filters" :rules="rules" label-position="top" class="filter-form">
      <el-form-item label="开始日期" prop="start_date">
        <el-date-picker v-model="filters.start_date" value-format="YYYY-MM-DD" type="date" placeholder="开始日期" />
      </el-form-item>
      <el-form-item label="结束日期" prop="end_date">
        <el-date-picker v-model="filters.end_date" value-format="YYYY-MM-DD" type="date" placeholder="结束日期" />
      </el-form-item>
    </el-form>
    <el-table v-loading="loading" :data="items" class="pretty-table" empty-text="暂无日志">
      <el-table-column prop="created_at" label="时间" width="170" />
      <el-table-column prop="username" label="账号" width="120" />
      <el-table-column prop="action" label="动作" width="150" />
      <el-table-column prop="target_type" label="对象" width="110" />
      <el-table-column prop="detail" label="详情" min-width="220" />
      <el-table-column prop="ip_address" label="IP" width="130" />
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/http'
import { validateForm } from '../utils/validators'

const loading = ref(false)
const formRef = ref(null)
const items = ref([])
const filters = reactive({ q: '', start_date: '', end_date: '' })
const rules = {
  start_date: [{ validator: validateDateRange, trigger: 'change' }],
  end_date: [{ validator: validateDateRange, trigger: 'change' }]
}

onMounted(loadData)

async function loadData() {
  const valid = await validateForm(formRef)
  if (!valid) return
  loading.value = true
  try {
    const data = await api.logs(filters)
    items.value = data.items
  } finally {
    loading.value = false
  }
}

async function exportLogs() {
  const valid = await validateForm(formRef)
  if (!valid) return
  window.open(api.logsExportUrl(filters), '_blank')
}

function validateDateRange(_rule, _value, callback) {
  if (filters.start_date && filters.end_date && filters.end_date < filters.start_date) {
    callback(new Error('结束日期不能早于开始日期'))
    return
  }
  callback()
}
</script>
