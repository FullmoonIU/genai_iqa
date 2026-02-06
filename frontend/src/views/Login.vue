<template>
  <div class="wrap">
    <el-card class="card">
      <template #header>
        <div class="h1">登录</div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="onSubmit" style="width: 100%">
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
    // 后端未实现时：可临时注释掉 API，直接 setAuth('dev-token', {username: form.username})
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
.wrap { height: 100vh; display: flex; align-items: center; justify-content: center; background: #f4f6fb; }
.card { width: 420px; }
.h1 { font-size: 18px; font-weight: 700; }
.tips { text-align: center; color: #666; }
</style>