<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-header">
        <svg class="logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30" fill="none">
          <rect x="1" y="1" width="28" height="28" rx="2" stroke="#16A34A" stroke-width="2"></rect>
          <rect x="7" y="9" width="3" height="15" rx="1.5" fill="#22C55E"></rect>
          <rect x="21" y="9" width="3" height="15" rx="1.5" fill="#16A34A"></rect>
          <rect x="14" y="6" width="3" height="18" rx="1.5" fill="#F2CB39"></rect>
        </svg>
        <h1>LIDA</h1>
        <p>自动化数据可视化平台</p>
      </div>

      <el-form :model="loginForm" :rules="rules" ref="loginForm" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="el-icon-user"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="el-icon-lock" @keyup.enter.native="handleLogin"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="success" :loading="loading" style="width: 100%" @click="handleLogin">登录</el-button>
        </el-form-item>
        <div class="text-center">
          <span>还没有账号？</span>
          <router-link to="/register" class="link">立即注册</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { login } from '@/api'

export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      await this.$refs.loginForm.validate(async(valid) => {
        if (valid) {
          this.loading = true
          try {
            const res = await login(this.loginForm.username, this.loginForm.password)
            localStorage.setItem('access_token', res.access_token)
            this.$store.commit('SET_TOKEN', res.access_token)
            this.$message.success('登录成功')
            this.$router.push('/')
          } catch (error) {
            console.error(error)
          } finally {
            this.loading = false
          }
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 450px;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;

  .logo {
    width: 80px;
    height: 80px;
    margin-bottom: 10px;
  }

  h1 {
    font-size: 32px;
    color: #333;
    margin-bottom: 5px;
  }

  p {
    color: #666;
    font-size: 14px;
  }
}

.link {
  color: #67c23a;
  text-decoration: none;
  margin-left: 5px;
}
</style>
