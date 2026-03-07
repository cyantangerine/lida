<template>
  <div class="register-container">
    <el-card class="register-card">
      <div class="register-header">
        <svg class="logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30" fill="none">
          <rect x="1" y="1" width="28" height="28" rx="2" stroke="#16A34A" stroke-width="2"></rect>
          <rect x="7" y="9" width="3" height="15" rx="1.5" fill="#22C55E"></rect>
          <rect x="21" y="9" width="3" height="15" rx="1.5" fill="#16A34A"></rect>
          <rect x="14" y="6" width="3" height="18" rx="1.5" fill="#F2CB39"></rect>
        </svg>
        <h1>用户注册</h1>
      </div>

      <el-form :model="registerForm" :rules="rules" ref="registerForm" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" prefix-icon="el-icon-user"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" prefix-icon="el-icon-lock"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" prefix-icon="el-icon-lock"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="success" :loading="loading" style="width: 100%" @click="handleRegister">注册</el-button>
        </el-form-item>
        <div class="text-center">
          <span>已有账号？</span>
          <router-link to="/login" class="link">立即登录</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { register } from '@/api'

export default {
  name: 'Register',
  data() {
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      registerForm: {
        username: '',
        password: '',
        confirmPassword: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  methods: {
    async handleRegister() {
      await this.$refs.registerForm.validate(async(valid) => {
        if (valid) {
          this.loading = true
          try {
            await register(this.registerForm.username, this.registerForm.password)
            this.$message.success('注册成功，请登录')
            this.$router.push('/login')
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
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 450px;
  padding: 20px;
}

.register-header {
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
  }
}

.link {
  color: #67c23a;
  text-decoration: none;
  margin-left: 5px;
}
</style>
