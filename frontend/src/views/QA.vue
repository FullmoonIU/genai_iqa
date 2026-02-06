<template>
  <el-row :gutter="12">
    <el-col :span="10">
      <el-card>
        <template #header>
          <div class="h1">提问</div>
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
            <el-slider v-model="topK" :min="3" :max="10" />
            <div class="hint">当前：{{ topK }}</div>
          </el-form-item>

          <el-button type="primary" :loading="loading" @click="ask" style="width: 100%">
            发送
          </el-button>
        </el-form>

        <el-divider />
        <el-alert
          type="info"
          show-icon
          title="注意：如果资源库未入库/未覆盖该知识点，系统应提示无法回答或建议上传资料。"
        />
      </el-card>
    </el-col>

    <el-col :span="14">
      <el-card>
        <template #header>
          <div class="h1">回答</div>
        </template>

        <div v-if="!answer && !loading" class="empty">暂无回答，请先提问。</div>

        <el-skeleton v-if="loading" :rows="6" animated />

        <div v-else>
          <div class="answer" v-if="answer">
            {{ answer }}
          </div>

          <el-divider v-if="citations.length" />

          <el-collapse v-if="citations.length">
            <el-collapse-item title="依据来源（点击展开）" name="1">
              <el-timeline>
                <el-timeline-item
                  v-for="(c, idx) in citations"
                  :key="idx"
                  :timestamp="formatSource(c)"
                >
                  <div class="snippet">{{ c.snippet || c.text || '' }}</div>
                  <div class="meta">
                    <el-tag size="small">chunk: {{ c.chunk_id ?? '-' }}</el-tag>
                    <el-tag size="small" type="info">page: {{ c.page ?? '-' }}</el-tag>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { askQuestion } from '@/api/qa'

const question = ref('')
const topK = ref(6)
const loading = ref(false)

const answer = ref('')
const citations = ref([])

function formatSource(c) {
  const name = c.source_name || c.doc_name || 'unknown'
  const p = (c.page !== undefined && c.page !== null) ? `p.${c.page}` : ''
  return `${name} ${p}`.trim()
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
.hint { color: #666; font-size: 12px; margin-top: 6px; }
.empty { color: #999; padding: 16px 0; }
.answer { white-space: pre-wrap; line-height: 1.7; }
.snippet { white-space: pre-wrap; color: #333; }
.meta { display: flex; gap: 8px; margin-top: 8px; }
</style>