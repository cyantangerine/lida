<template>
  <div class="home-container">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="logo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30" fill="none">
          <rect x="1" y="1" width="28" height="28" rx="2" stroke="#16A34A" stroke-width="2"></rect>
          <rect x="7" y="9" width="3" height="15" rx="1.5" fill="#22C55E"></rect>
          <rect x="21" y="9" width="3" height="15" rx="1.5" fill="#16A34A"></rect>
          <rect x="14" y="6" width="3" height="18" rx="1.5" fill="#F2CB39"></rect>
        </svg>
        <span>LIDA</span>
      </div>
      
      <el-menu :default-active="activeIndex" background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
        <el-menu-item index="1" @click="currentView = 'upload'">
          <i class="el-icon-upload"></i>
          <span slot="title">上传数据</span>
        </el-menu-item>
        <el-menu-item index="2" @click="currentView = 'chats'">
          <i class="el-icon-chat-line-square"></i>
          <span slot="title">聊天历史</span>
        </el-menu-item>
      </el-menu>

      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span class="el-dropdown-link">
            {{ username }}<i class="el-icon-arrow-down el-icon--right"></i>
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 上传视图 -->
      <div v-if="currentView === 'upload'" class="upload-view">
        <el-card>
          <div slot="header">
            <span>上传数据文件</span>
          </div>
          
          <el-upload
            drag
            action="#"
            :http-request="handleUpload"
            :before-upload="beforeUpload"
            :on-success="handleSuccess"
            :on-error="handleError"
            accept=".csv,.xls,.xlsx,.json"
          >
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <div class="el-upload__tip" slot="tip">支持 CSV、Excel、JSON 格式文件</div>
          </el-upload>

          <el-form :model="dataDescription" label-width="100px" class="mt-20">
            <el-form-item label="数据描述">
              <el-input
                v-model="dataDescription.description"
                type="textarea"
                :rows="3"
                placeholder="请描述这个数据集"
              ></el-input>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 聊天列表视图 -->
      <div v-if="currentView === 'chats'" class="chats-view">
        <el-card>
          <div slot="header">
            <span>聊天历史</span>
          </div>
          
          <el-table :data="chats" style="width: 100%" @row-click="handleChatClick">
            <el-table-column prop="name" label="名称"></el-table-column>
            <el-table-column prop="create_time" label="创建时间" width="180"></el-table-column>
            <el-table-column prop="update_time" label="更新时间" width="180"></el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { getChatList, uploadFile } from '@/api'

export default {
  name: 'Home',
  data() {
    return {
      activeIndex: '1',
      currentView: 'upload',
      username: localStorage.getItem('username') || '用户',
      chats: [],
      dataDescription: {
        description: ''
      },
      selectedFile: null
    }
  },
  created() {
    this.loadChats()
  },
  methods: {
    async loadChats() {
      try {
        const res = await getChatList(0, 10)
        this.chats = res.chats || []
      } catch (error) {
        console.error(error)
      }
    },
    
    beforeUpload(file) {
      const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/json']
      const allowedExts = ['csv', 'xls', 'xlsx', 'json']
      const fileExt = file.name.split('.').pop().toLowerCase()
      
      if (!allowedTypes.includes(file.type) && !allowedExts.includes(fileExt)) {
        this.$message.error('只能上传 CSV、Excel 或 JSON 格式的文件!')
        return false
      }
      
      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isLt10M) {
        this.$message.error('文件大小不能超过 10MB!')
        return false
      }
      
      this.selectedFile = file
      return true
    },
    
    async handleUpload(options) {
      const { file, onSuccess, onError } = options
      
      if (!this.dataDescription.description) {
        this.$message.warning('请填写数据描述')
        return
      }
      
      try {
        const loading = this.$loading({
          lock: true,
          text: '正在上传并分析数据...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        
        // 调用上传 API
        const res = await uploadFile(
          file,
          { description: this.dataDescription.description, fields: {} },
          'new'
        )
        
        loading.close()
        
        if (res.status) {
          this.$message.success('上传成功!')
          this.dataDescription.description = ''
          this.selectedFile = null
          
          // 跳转到聊天详情页面
          this.$router.push(`/chat/${res.chat_id}`)
        }
      } catch (error) {
        console.error(error)
        onError(error)
      }
    }
    
    handleSuccess(response, file) {
      this.$message.success('上传成功')
    },
    
    handleError(err) {
      this.$message.error('上传失败：' + err.message)
    },
    
    handleChatClick(row) {
      this.$router.push(`/chat/${row.id}`)
    },
    
    handleCommand(command) {
      if (command === 'logout') {
        this.$store.commit('LOGOUT')
        this.$router.push('/login')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.home-container {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 240px;
  background-color: #304156;
  color: #fff;
  display: flex;
  flex-direction: column;
  
  .logo {
    padding: 20px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    svg {
      width: 40px;
      height: 40px;
      margin-right: 10px;
    }
    
    span {
      font-size: 20px;
      font-weight: bold;
      color: #fff;
    }
  }
  
  .user-info {
    margin-top: auto;
    padding: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    
    .el-dropdown-link {
      color: #fff;
      cursor: pointer;
    }
  }
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: #f5f7fa;
  overflow-y: auto;
}

.upload-view, .chats-view {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
