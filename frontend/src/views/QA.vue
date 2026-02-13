<template>
  <el-row :gutter="14">
    <el-col :span="9">
      <el-card class="ask-card">
        <template #header>
          <div class="head-row">
            <span class="h1">提问</span>
            <el-tag type="info">RAG 模式</el-tag>
          </div>
        </template>

        <el-form label-position="top">
          <el-form-item label="问题">
            <el-input
              v-model="question"
              type="textarea"
              :rows="6"
              placeholder="请输入你的问题，例如：什么是二叉搜索树？插入过程是什么？"
            />
          </el-form-item>

          <el-form-item label="TopK（检索证据条数）">
            <el-slider v-model="topK" :min="1" :max="20" />
            <div class="hint">当前：{{ topK }}</div>
          </el-form-item>

          <el-button type="primary" :loading="loading" @click="ask" class="full-btn">
            发送
          </el-button>
        </el-form>

        <el-divider />
        <el-alert
          type="info"
          show-icon
          title="回答后的“依据来源”仅展示模型实际使用的证据，支持展开查看全文。"
        />
      </el-card>
    </el-col>

    <el-col :span="15">
      <el-card class="answer-card">
        <template #header>
          <div class="head-row">
            <span class="h1">AI 回答</span>
            <el-button text type="primary" @click="clearResult" :disabled="loading || (!answer && !citations.length)">
              清空
            </el-button>
          </div>
        </template>

        <div v-if="!answer && !loading" class="empty">暂无回答，请先提问。</div>
        <el-skeleton v-if="loading" :rows="7" animated />

        <template v-else>
          <div class="chat-line user" v-if="lastQuestion">
            <div class="bubble">{{ lastQuestion }}</div>
          </div>
          <div class="chat-line ai" v-if="answer">
            <div class="bubble answer">{{ answer }}</div>
          </div>

          <el-divider v-if="citations.length" />

          <div v-if="citations.length" class="source-wrap">
            <div class="source-title">依据来源（模型实际引用）</div>
            <div class="source-list">
              <el-card v-for="(c, idx) in citations" :key="idx" shadow="never" class="source-item">
                <div class="source-head">
                  <el-tag size="small" effect="dark">{{ idx + 1 }}</el-tag>
                  <span class="source-name">{{ formatSource(c) }}</span>
                </div>
                <div class="snippet">{{ c.snippet || '（无摘要）' }}</div>
                <div class="meta">
                  <el-tag size="small">chunk: {{ c.chunk_id ?? '-' }}</el-tag>
                  <el-tag size="small" type="info">page: {{ c.page ?? '-' }}</el-tag>
                  <el-button text type="primary" @click="openCitation(c)">展开全文</el-button>
                </div>
              </el-card>
            </div>
          </div>
        </template>
      </el-card>
    </el-col>
  </el-row>

  <el-dialog v-model="citationVisible" width="760px" title="证据全文">
    <div class="full-text">{{ activeCitation?.text || activeCitation?.snippet || '暂无内容' }}</div>
    <template #footer>
      <el-button @click="citationVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { askQuestion } from '@/api/qa'

const question = ref('')
const topK = ref(6)
const loading = ref(false)

const lastQuestion = ref('')
const answer = ref('')
const citations = ref([])

const citationVisible = ref(false)
const activeCitation = ref(null)

function formatSource(c) {
  const name = c.source_name || c.doc_name || 'unknown'
  const p = (c.page !== undefined && c.page !== null) ? `p.${c.page}` : ''
  return `${name} ${p}`.trim()
}

function openCitation(c) {
  activeCitation.value = c
  citationVisible.value = true
}

function clearResult() {
  answer.value = ''
  citations.value = []
  lastQuestion.value = ''
}

async function ask() {
  const q = question.value.trim()
  if (!q) {
    ElMessage.warning('请输入问题')
    return
  }

  loading.value = true
  answer.value = ''
  citations.value = []
  lastQuestion.value = q

  try {
    const res = await askQuestion({ question: q, top_k: topK.value })
    answer.value = res.answer || ''
    citations.value = res.citations || []
    if (!answer.value) ElMessage.warning('未返回答案（检查后端接口）')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '请求失败（后端未启动也会这样）')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.h1 { font-size: 16px; font-weight: 700; }
.head-row { display: flex; justify-content: space-between; align-items: center; }
.hint { color: #666; font-size: 12px; margin-top: 6px; }
.full-btn { width: 100%; }
.empty { color: #999; padding: 18px 0; }

.chat-line { display: flex; margin-bottom: 10px; }
.chat-line.user { justify-content: flex-end; }
.chat-line.ai { justify-content: flex-start; }
.bubble {
  max-width: 92%;
  border-radius: 12px;
  padding: 10px 12px;
  line-height: 1.7;
  white-space: pre-wrap;
}
.chat-line.user .bubble {
  background: #eef4ff;
  border: 1px solid #d9e6ff;
}
.chat-line.ai .bubble {
  background: #f8f9fb;
  border: 1px solid #eceff4;
}

.source-title { font-size: 13px; color: #666; margin-bottom: 8px; }
.source-list { display: flex; flex-direction: column; gap: 8px; }
.source-item { border: 1px solid #eef1f4; }
.source-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.source-name { font-weight: 600; color: #303133; }
.snippet { white-space: pre-wrap; color: #333; margin-bottom: 8px; }
.meta { display: flex; align-items: center; gap: 8px; }
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