<script setup lang="ts">
defineProps<{
  value: number | string
  label: string
  color?: string
}>()
</script>

<template>
  <div class="stat-card">
    <div class="stat-value" :style="{ color: color ?? '#2e86ab' }">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
  </div>
</template>

<style scoped>
.stat-card {
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.06);
  border: 1px solid #e5f2f7;
  border-top: 4px solid currentColor;
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}
.stat-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 6px;
}
.stat-label {
  color: #6c757d;
  font-size: 0.875rem;
  font-weight: 500;
}
</style>
