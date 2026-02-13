<template>
  <div class="auth-page">
    <div class="auth-panel">
      <div class="hero">
        <div class="badge">GenAI EDU</div>
        <h1>创建学习账号</h1>
        <p>注册后即可构建个人知识库，体验可追溯的智能教育问答。</p>
        <ul>
          <li>🧠 上传课程资料并构建索引</li>
          <li>📌 获取带引用的回答</li>
          <li>📚 复盘历史问答与证据</li>
        </ul>
      </div>

      <el-card class="form-card" shadow="never">
        <template #header>
          <div class="title-row">
            <span class="h1">注册账号</span>
            <el-tag>新用户</el-tag>
          </div>
        </template>

        <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" size="large" clearable />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" size="large" />
          </el-form-item>

          <el-form-item label="确认密码" prop="password2">
            <el-input
              v-model="form.password2"
              type="password"
              show-password
              placeholder="请再次输入密码"
              size="large"
              @keyup.enter="onSubmit"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" @click="onSubmit" class="full-btn" size="large">
              注册
            </el-button>
          </el-form-item>

          <div class="tips">
            已有账号？
            <el-link type="primary" @click="router.push('/login')">去登录</el-link>
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
import { registerApi } from '@/api/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  password2: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  password2: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_, val, cb) => {
        if (val !== form.password) cb(new Error('两次密码不一致'))
        else cb()
      },
      trigger: 'blur'
    }
  ]
}

async function onSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await registerApi({ username: form.username, password: form.password })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '注册失败')
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
  background: radial-gradient(circle at 80% 20%, #ecf3ff 0, #f6f8fc 45%, #f6f8fc 100%);
}
.auth-panel {
  width: min(980px, 100%);
  display: grid;
  grid-template-columns: 1fr 440px;
  gap: 18px;
  align-items: stretch;
}
.hero {
  background: linear-gradient(135deg, #223a99 0%, #3162db 55%, #4a7cff 100%);
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