<template>
  <el-container class="h">
    <el-aside width="220px" class="aside">
      <div class="brand">智能教育答疑系统</div>
      <el-menu :default-active="active" router>
        <el-menu-item index="/qa">智能答疑</el-menu-item>
        <el-menu-item index="/documents">资源管理</el-menu-item>
        <el-menu-item index="/history">历史查询</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <el-tag type="info" class="mr8">{{ user?.username || 'User' }}</el-tag>
          <el-button size="small" @click="logout">退出</el-button>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearAuth, getUser } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const user = getUser()

const active = computed(() => route.path)

const pageTitle = computed(() => {
  if (route.path.startsWith('/qa')) return '智能答疑'
  if (route.path.startsWith('/documents')) return '资源管理'
  if (route.path.startsWith('/history')) return '历史查询'
  return '系统'
})

function logout() {
  clearAuth()
  router.push('/login')
}
</script>

<style scoped>
.h { height: 100vh; }
.aside { border-right: 1px solid #eee; }
.brand {
  height: 56px; display: flex; align-items: center;
  padding: 0 16px; font-weight: 700;
}
.header {
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #eee;
}
.title { font-size: 16px; font-weight: 600; }
.header-right { display: flex; align-items: center; gap: 8px; }
.mr8 { margin-right: 8px; }
.main { background: #fafafa; }
</style>