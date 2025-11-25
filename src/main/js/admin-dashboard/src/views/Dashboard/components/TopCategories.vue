<template>
  <el-card shadow="hover" style="margin-top: 20px">
    <template #header>
      <h3>熱門分類</h3>
    </template>

    <el-empty v-if="!categories.length" description="暫無資料" />

    <el-table v-else :data="categories" style="width:100%">
      <el-table-column prop="category_name" label="分類" />
      <el-table-column prop="count" label="意見數" width="120" />
    </el-table>
  </el-card>
</template>

<script setup>
defineProps({
  categories: { type: Array, default: () => [] }
})
</script>
