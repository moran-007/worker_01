<template>
  <div v-loading="loading" class="database-page">
    <el-alert
      title="数据库文件：E:\\moran_project\\class_worker\\data\\attendance.db"
      type="info"
      show-icon
      :closable="false"
    />

    <section class="db-summary">
      <MetricCard label="数据表" :value="tableCount" icon="Grid" tone="blue" />
      <MetricCard label="联表视图" :value="viewCount" icon="Connection" tone="green" />
      <MetricCard label="外键表" :value="foreignKeyTableCount" icon="Link" tone="amber" />
    </section>

    <el-card shadow="never" class="section-card data-card">
      <template #header>
        <div class="table-title">
          <span>数据库对象</span>
          <span class="muted-text">Tables / Views</span>
        </div>
      </template>
      <el-table :data="objects" empty-text="暂无对象" class="pretty-table">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.type === 'view' ? 'success' : ''">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" class="section-card data-card">
      <template #header>
        <div class="table-title">
          <span>外键关系</span>
          <span class="muted-text">用于数据库软件核对关系</span>
        </div>
      </template>
      <el-collapse>
        <el-collapse-item v-for="(items, table) in foreignKeys" :key="table" :title="table">
          <el-table :data="items" size="small" empty-text="无外键">
            <el-table-column prop="from" label="字段" />
            <el-table-column prop="table" label="关联表" />
            <el-table-column prop="to" label="关联字段" />
          </el-table>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import MetricCard from '../components/MetricCard.vue'
import { api } from '../api/http'

const loading = ref(false)
const objects = ref([])
const foreignKeys = ref({})
const tableCount = computed(() => objects.value.filter((item) => item.type === 'table').length)
const viewCount = computed(() => objects.value.filter((item) => item.type === 'view').length)
const foreignKeyTableCount = computed(() => Object.values(foreignKeys.value).filter((items) => items.length).length)

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const data = await api.databaseMeta()
    objects.value = data.objects
    foreignKeys.value = data.foreign_keys
  } finally {
    loading.value = false
  }
}
</script>
