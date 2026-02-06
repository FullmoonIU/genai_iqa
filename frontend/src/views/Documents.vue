<template>
  <el-card>
    <template #header>
      <div class="row">
        <div class="h1">资源管理</div>
        <div class="actions">
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            :on-change="onPickFile"
            accept=".pdf,.doc,.docx,.txt,.md"
          >
            <el-button type="primary">选择文件</el-button>
          </el-upload>

          <el-button :loading="loadingUpload" :disabled="!pickedFile" @click="upload">
            上传
          </el-button>

          <el-button @click="refresh">刷新</el-button>
        </div>
      </div>
    </template>

    <el-alert type="info" show-icon class="mb12"
      title="建议：先上传课程资料 → 点击“处理入库”生成知识库片段，然后去“智能答疑”提问。" />

    <el-table :data="rows" v-loading="loadingList" style="width: 100%">
      <el-table-column prop="name" label="文件名" min-width="220" />
      <el-table-column prop="type" label="类型" width="90" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ row.status || 'unknown' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="上传时间" width="180" />

      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" :loading="row._processing" @click="process(row)">处理入库</el-button>
          <el-popconfirm title="确定删除该资源？" @confirm="remove(row)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt12 note" v-if="pickedFile">
      已选择：<b>{{ pickedFile.name }}</b>
    </div>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { listDocuments, uploadDocument, processDocument, deleteDocument } from '@/api/documents'

const rows = ref([])
const pickedFile = ref(null)
const loadingList = ref(false)
const loadingUpload = ref(false)

function statusType(s) {
  if (!s) return 'info'
  const v = String(s).toLowerCase()
  if (['done', 'ready', 'indexed', 'success'].includes(v)) return 'success'
  if (['processing', 'running'].includes(v)) return 'warning'
  if (['failed', 'error'].includes(v)) return 'danger'
  return 'info'
}

function onPickFile(file) {
  pickedFile.value = file.raw
}

async function refresh() {
  loadingList.value = true
  try {
    const res = await listDocuments()
    rows.value = (res || []).map(x => ({ ...x, _processing: false }))
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '获取资源列表失败（后端未启动也会这样）')
  } finally {
    loadingList.value = false
  }
}

async function upload() {
  if (!pickedFile.value) return
  loadingUpload.value = true
  try {
    await uploadDocument(pickedFile.value)
    ElMessage.success('上传成功')
    pickedFile.value = null
    await refresh()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '上传失败')
  } finally {
    loadingUpload.value = false
  }
}

async function process(row) {
  row._processing = true
  try {
    await processDocument(row.id)
    ElMessage.success('开始处理/入库（或已完成）')
    await refresh()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '处理失败')
  } finally {
    row._processing = false
  }
}

async function remove(row) {
  try {
    await deleteDocument(row.id)
    ElMessage.success('删除成功')
    await refresh()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

onMounted(refresh)
</script>

<style scoped>
.row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.h1 { font-size: 16px; font-weight: 700; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; }
.mb12 { margin-bottom: 12px; }
.mt12 { margin-top: 12px; }
.note { color: #666; }
</style>