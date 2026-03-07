<template>
  <div class="layout-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30" fill="none">
            <rect x="1" y="1" width="28" height="28" rx="2" stroke="#16A34A" stroke-width="2"></rect>
            <rect x="7" y="9" width="3" height="15" rx="1.5" fill="#22C55E"></rect>
            <rect x="21" y="9" width="3" height="15" rx="1.5" fill="#16A34A"></rect>
            <rect x="14" y="6" width="3" height="18" rx="1.5" fill="#F2CB39"></rect>
          </svg>
          <span>LIDA</span>
        </div>
        
        <div class="nav-menu">
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            background-color="#fff"
            text-color="#333"
            active-text-color="#67c23a"
            @select="handleMenuSelect"
          >
            <el-menu-item index="home">
              <i class="el-icon-house"></i>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="upload">
              <i class="el-icon-upload"></i>
              <span>上传数据</span>
            </el-menu-item>
            <el-menu-item index="chats">
              <i class="el-icon-chat-line-square"></i>
              <span>聊天历史</span>
            </el-menu-item>
          </el-menu>
        </div>
        
        <div class="user-actions">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="36" :icon="userAvatar">{{ username[0].toUpperCase() }}</el-avatar>
              <span class="username">{{ username }}</span>
              <i class="el-icon-arrow-down"></i>
            </div>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="main-container">
      <!-- 上传视图 -->
      <div v-if="currentView === 'upload'" class="view-section">
        <el-card class="upload-card">
          <div slot="header" class="card-header">
            <span><i class="el-icon-upload"></i> 上传数据文件</span>
          </div>
          
          <div class="upload-content">
            <el-upload
              drag
              action="#"
              :http-request="handleUpload"
              :before-upload="beforeUpload"
              accept=".csv,.xls,.xlsx,.json"
              multiple
            >
              <i class="el-icon-upload el-icon--upload"></i>
              <div class="el-upload__text">
                将文件拖到此处，或 <em>点击上传</em>
              </div>
              <div class="el-upload__tip" slot="tip">
                支持 CSV、Excel、JSON 格式文件，单个文件不超过 10MB
              </div>
            </el-upload>

            <el-form :model="dataDescription" label-width="120px" class="desc-form">
              <el-form-item label="数据描述" required>
                <el-input
                  v-model="dataDescription.description"
                  type="textarea"
                  :rows="4"
                  placeholder="请描述这个数据集，例如：这是一个销售数据集，包含日期、产品、销售额等字段"
                ></el-input>
              </el-form-item>
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="submitUpload"
                  :loading="uploading"
                  icon="el-icon-check"
                >
                  确认上传
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </div>

      <!-- 聊天列表视图 -->
      <div v-if="currentView === 'chats'" class="view-section">
        <el-card>
          <div slot="header" class="card-header">
            <span><i class="el-icon-chat-line-square"></i> 聊天历史</span>
            <el-button 
              type="primary" 
              size="small" 
              icon="el-icon-refresh"
              circle
              @click="loadChats"
            ></el-button>
          </div>
          
          <el-table 
            :data="chats" 
            style="width: 100%" 
            @row-click="handleChatClick"
            :default-sort="{prop: 'update_time', order: 'descending'}"
          >
            <el-table-column prop="name" label="名称" min-width="200"></el-table-column>
            <el-table-column prop="create_time" label="创建时间" width="180" sortable></el-table-column>
            <el-table-column prop="update_time" label="更新时间" width="180" sortable></el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template slot-scope="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click.stop="openChat(scope.row.id)"
                >
                  打开
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-container">
            <el-pagination
              background
              layout="prev, pager, next"
              :total="totalChats"
              :page-size="pageSize"
              @current-change="handlePageChange"
            ></el-pagination>
          </div>
        </el-card>
      </div>
    </el-main>
  </div>
</template>

<script>
import { getChatList, uploadFile } from '@/api'

export default {
  name: 'HomeLayout',
  data() {
    return {
      activeMenu: 'home',
      currentView: 'upload',
      username: localStorage.getItem('username') || '用户',
      userAvatar: '',
      chats: [],
      totalChats: 0,
      currentPage: 1,
      pageSize: 10,
      dataDescription: {
        description: ''
      },
      selectedFile: null,
      uploading: false
    }
  },
  created() {
    this.loadChats()
  },
  methods: {
    async loadChats() {
      try {
        const skip = (this.currentPage - 1) * this.pageSize
        const res = await getChatList(skip, this.pageSize)
        this.chats = res.chats || []
        this.totalChats = this.chats.length
      } catch (error) {
        console.error(error)
      }
    },
    
    handleMenuSelect(index) {
      if (index === 'home') {
        this.currentView = 'chats'
      } else if (index === 'upload') {
        this.currentView = 'upload'
      } else if (index === 'chats') {
        this.currentView = 'chats'
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
    
    async submitUpload() {
      if (!this.selectedFile) {
        this.$message.warning('请选择要上传的文件')
        return
      }
      
      if (!this.dataDescription.description.trim()) {
        this.$message.warning('请填写数据描述')
        return
      }
      
      this.uploading = true
      const loading = this.$loading({
        lock: true,
        text: '正在上传并分析数据...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      
      try {
        const res = await uploadFile(
          this.selectedFile,
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
        loading.close()
        this.$message.error('上传失败：' + error.message)
      } finally {
        this.uploading = false
      }
    },
    
    handleUpload(options) {
      // 由 submitUpload 统一处理
    },
    
    handleChatClick(row) {
      this.openChat(row.id)
    },
    
    openChat(chatId) {
      this.$router.push(`/chat/${chatId}`)
    },
    
    handlePageChange(page) {
      this.currentPage = page
      this.loadChats()
    },
    
    handleCommand(command) {
      if (command === 'logout') {
        this.$confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.$store.commit('LOGOUT')
          this.$router.push('/login')
          this.$message.success('已退出登录')
        }).catch(() => {})
      } else if (command === 'profile') {
        this.$message.info('个人中心功能开发中...')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.layout-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
    padding: 0 20px;
  }
  
  .logo {
    display: flex;
    align-items: center;
    cursor: pointer;
    
    svg {
      width: 40px;
      height: 40px;
      margin-right: 10px;
    }
    
    span {
      font-size: 20px;
      font-weight: bold;
      color: #333;
    }
  }
  
  .nav-menu {
    flex: 1;
    display: flex;
    justify-content: center;
  }
  
  .user-actions {
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      
      .username {
        margin: 0 8px;
        color: #333;
      }
    }
  }
}

.main-container {
  padding: 20px;
}

.view-section {
  max-width: 1200px;
  margin: 0 auto;
}

.upload-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .upload-content {
    .desc-form {
      margin-top: 30px;
      padding: 20px;
      background: #f9fafb;
      border-radius: 4px;
    }
  }
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.card-header {
  i {
    margin-right: 8px;
  }
}
</style>
