<template>
  <router-view v-if="$route.meta.public || $route.meta.standalone" />
  <AppShell v-else />
</template>

<script setup>
import AppShell from './components/AppShell.vue'
</script>
