<template>
  <el-card shadow="never" class="metric-card">
    <div class="metric-icon" :class="tone">
      <el-icon>
        <component :is="icon" />
      </el-icon>
    </div>
    <div>
      <span>{{ label }}</span>
      <strong>{{ value }}</strong>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: 0 },
  icon: { type: String, default: 'DataLine' },
  tone: { type: String, default: 'blue' }
})
</script>
