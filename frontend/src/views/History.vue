<template>
  <el-card class="history-card">
    <template #header>
      <div class="row">
        <div class="h1">历史对话</div>
        <div class="actions">
          <el-input v-model="kw" placeholder="按问题/回答过滤" clearable style="width: 260px" />
          <el-button @click="refresh">刷新</el-button>
        </div>
      </div>
    </template>

    <el-row :gutter="12" class="panel" v-loading="loading">
      <el-col :span="9" class="left-col">
        <div class="count">共 {{ filtered.length }} 条</div>
        <div class="list">
          <div
            v-for="row in filtered"
            :key="row.id"
            class="item"
            :class="{ active: current?.id === row.id }"
            @click="openRow(row)"
          >
            <div class="item-time">{{ row.created_at }}</div>
            <div class="item-q">{{ row.question }}</div>
            <div class="item-meta">{{ row.citations?.length || 0 }} 条依据来源</div>
          </div>
          <div v-if="!filtered.length" class="empty">暂无匹配历史</div>
        </div>
      </el-col>

      <el-col :span="15" class="right-col">
        <div v-if="!current" class="empty">请选择左侧一条历史记录查看。</div>
        <template v-else>
          <div class="chat-line user">
            <div class="bubble">{{ current.question }}</div>
          </div>
          <div class="chat-line ai">
            <div class="bubble">{{ current.answer }}</div>
          </div>

          <div class="src-title" v-if="current.citations?.length">依据来源</div>
          <el-collapse v-if="current.citations?.length">
            <el-collapse-item
              v-for="(c, idx) in current.citations"
              :key="idx"
              :title="`${idx + 1}. ${formatSource(c)}`"
              :name="String(idx)"
            >
              <div class="snippet">{{ c.snippet || '（无摘要）' }}</div>
              <div class="meta">
                <el-tag size="small">chunk: {{ c.chunk_id ?? '-' }}</el-tag>
                <el-tag size="small" type="info">page: {{ c.page ?? '-' }}</el-tag>
                <el-button text type="primary" @click="openCitation(c)">展开全文</el-button>
              </div>
            </el-collapse-item>
          </el-collapse>
        </template>
      </el-col>
    </el-row>
  </el-card>

  <el-dialog v-model="citationVisible" width="760px" title="证据全文">
    <div class="full-text">{{ activeCitation?.text || activeCitation?.snippet || '暂无内容' }}</div>
    <template #footer>
      <el-button @click="citationVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { listHistory } from '@/api/history'

const rows = ref([])
const loading = ref(false)
const kw = ref('')
const current = ref(null)

const citationVisible = ref(false)
const activeCitation = ref(null)

const filtered = computed(() => {
  const k = kw.value.trim().toLowerCase()
  if (!k) return rows.value
  return rows.value.filter((r) =>
    String(r.question || '').toLowerCase().includes(k) ||
    String(r.answer || '').toLowerCase().includes(k)
  )
})

function formatSource(c) {
  const name = c.source_name || c.doc_name || 'unknown'
  const p = (c.page !== undefined && c.page !== null) ? `p.${c.page}` : ''
  return `${name} ${p}`.trim()
}

function openCitation(c) {
  activeCitation.value = c
  citationVisible.value = true
}

function openRow(row) {
  current.value = row
}

async function refresh() {
  loading.value = true
  try {
    const res = await listHistory()
    rows.value = res || []
    current.value = rows.value[0] || null
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
.panel { min-height: 560px; }
.left-col { border-right: 1px solid #eee; }
.count { color: #777; font-size: 12px; margin-bottom: 8px; }
.list { max-height: 560px; overflow: auto; padding-right: 6px; }
.item { padding: 10px; border: 1px solid #eceff4; border-radius: 8px; margin-bottom: 8px; cursor: pointer; }
.item:hover { border-color: #cdd9ff; }
.item.active { border-color: #9ab6ff; background: #f5f8ff; }
.item-time { color: #909399; font-size: 12px; }
.item-q { margin-top: 4px; font-weight: 600; color: #303133; line-height: 1.4; }
.item-meta { margin-top: 4px; font-size: 12px; color: #909399; }
.right-col { padding-left: 4px; }
.empty { color: #999; padding: 16px 0; }
.chat-line { display: flex; margin-bottom: 10px; }
.chat-line.user { justify-content: flex-end; }
.chat-line.ai { justify-content: flex-start; }
.bubble {
  max-width: 95%;
  border-radius: 12px;
  padding: 10px 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  border: 1px solid #eceff4;
  background: #f8f9fb;
}
.chat-line.user .bubble {
  border-color: #d9e6ff;
  background: #eef4ff;
}
.src-title { margin: 10px 0 6px; color: #666; font-size: 13px; }
.snippet { white-space: pre-wrap; color: #333; }
.meta { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.full-text {
  white-space: pre-wrap;
  max-height: 56vh;
  overflow: auto;
  background: #fafafa;
  border: 1px solid #ececec;
  border-radius: 8px;
  padding: 12px;
  line-height: 1.75;
}
</style>