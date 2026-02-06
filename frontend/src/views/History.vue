<template>
  <el-card>
    <template #header>
      <div class="row">
        <div class="h1">历史查询</div>
        <div class="actions">
          <el-input v-model="kw" placeholder="按关键词过滤" clearable style="width: 220px" />
          <el-button @click="refresh">刷新</el-button>
        </div>
      </div>
    </template>

    <el-table :data="filtered" v-loading="loading" @row-click="openRow">
      <el-table-column prop="created_at" label="时间" width="180" />
      <el-table-column prop="question" label="问题" min-width="260" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" @click.stop="openRow(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="历史记录" width="720px">
      <div v-if="current">
        <h4>问题</h4>
        <div class="box">{{ current.question }}</div>
        <h4 style="margin-top: 12px;">回答</h4>
        <div class="box">{{ current.answer }}</div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { listHistory } from '@/api/history'

const rows = ref([])
const loading = ref(false)
const kw = ref('')

const dialogVisible = ref(false)
const current = ref(null)

const filtered = computed(() => {
  const k = kw.value.trim().toLowerCase()
  if (!k) return rows.value
  return rows.value.filter(r =>
    String(r.question || '').toLowerCase().includes(k) ||
    String(r.answer || '').toLowerCase().includes(k)
  )
})

function openRow(row) {
  current.value = row
  dialogVisible.value = true
}

async function refresh() {
  loading.value = true
  try {
    const res = await listHistory()
    rows.value = res || []
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '获取历史失败（后端未启动也会这样）')
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
</script>

<style scoped>
.row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.h1 { font-size: 16px; font-weight: 700; }
.actions { display: flex; gap: 8px; align-items: center; }
.box { white-space: pre-wrap; background: #fafafa; padding: 10px; border: 1px solid #eee; border-radius: 8px; }
</style>