<template>
  <el-row :gutter="20">
    <el-col v-for="item in items" :key="item.key" :span="6">
      <el-card shadow="hover">
        <div class="stat-item">
          <el-icon :size="40" :color="item.color">
            <component :is="item.icon" />
          </el-icon>
          <div class="stat-info">
            <h3>{{ item.value }}</h3>
            <p>{{ item.label }}</p>
          </div>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
defineProps({
  items: { type: Array, required: true }
})
</script>