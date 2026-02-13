<template>
  <div class="auth-page">
    <div class="auth-panel">
      <div class="hero">
        <div class="badge">GenAI EDU</div>
        <h1>欢迎回来</h1>
        <p>登录后可继续使用智能答疑、依据来源追溯、历史复盘等能力。</p>
        <ul>
          <li>✅ 证据可追溯问答</li>
          <li>✅ 资料入库后检索增强</li>
          <li>✅ 历史对话可回看与对比</li>
        </ul>
      </div>

      <el-card class="form-card" shadow="never">
        <template #header>
          <div class="title-row">
            <span class="h1">账号登录</span>
            <el-tag type="info">安全连接</el-tag>
          </div>
        </template>

        <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" size="large" clearable />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              placeholder="请输入密码"
              size="large"
              @keyup.enter="onSubmit"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" @click="onSubmit" class="full-btn" size="large">
              登录
            </el-button>
          </el-form-item>

          <div class="tips">
            没有账号？
            <el-link type="primary" @click="router.push('/register')">去注册</el-link>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { loginApi } from '@/api/auth'
import { setAuth } from '@/stores/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function onSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await loginApi(form)
    setAuth(res.token, res.user)
    ElMessage.success('登录成功')
    router.push('/qa')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: radial-gradient(circle at 20% 20%, #ecf3ff 0, #f6f8fc 45%, #f6f8fc 100%);
}
.auth-panel {
  width: min(980px, 100%);
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 18px;
  align-items: stretch;
}
.hero {
  background: linear-gradient(135deg, #1f4fe0 0%, #3675ff 55%, #5a8dff 100%);
  color: #fff;
  border-radius: 18px;
  padding: 28px;
  box-shadow: 0 12px 30px rgba(43, 84, 185, 0.25);
}
.badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 999px;
  padding: 4px 10px;
  margin-bottom: 12px;
}
.hero h1 {
  margin: 0 0 8px;
  font-size: 28px;
}
.hero p {
  margin: 0;
  opacity: 0.92;
}
.hero ul {
  margin: 18px 0 0;
  padding-left: 18px;
  line-height: 1.8;
}
.form-card {
  border-radius: 16px;
  border: 1px solid #e7ecf5;
}
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.h1 {
  font-size: 18px;
  font-weight: 700;
}
.full-btn {
  width: 100%;
}
.tips {
  text-align: center;
  color: #667085;
}

@media (max-width: 900px) {
  .auth-panel {
    grid-template-columns: 1fr;
  }
}
</style>