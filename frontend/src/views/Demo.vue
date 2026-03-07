<template>
  <div class="demo-container">
    <el-card>
      <div slot="header">
        <span>LIDA Demo - 在线体验</span>
      </div>

      <div class="demo-content">
        <el-alert
          title="欢迎使用 LIDA 在线演示"
          description="这是一个简化的演示版本，展示 LIDA 的核心功能。完整功能请查看 API文档。"
          type="success"
          :closable="false"
          show-icon
        />

        <div class="features mt-20">
          <h3>核心功能</h3>
          <el-row :gutter="20">
            <el-col :span="8" v-for="(feature, index) in features" :key="index">
              <el-card shadow="hover" class="feature-card">
                <div class="feature-icon">
                  <i :class="feature.icon"></i>
                </div>
                <h4>{{ feature.title }}</h4>
                <p>{{ feature.description }}</p>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <div class="try-section mt-20 text-center">
          <el-button type="primary" size="large" @click="$router.push('/login')">
            立即体验
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Demo',
  data() {
    return {
      features: [
        {
          icon: 'el-icon-data-analysis',
          title: '数据总结',
          description: '自动分析数据集并生成简洁的统计摘要'
        },
        {
          icon: 'el-icon-chat-dot-square',
          title: '目标探索',
          description: '基于数据自动生成有意义的可视化目标'
        },
        {
          icon: 'el-icon-picture-outline',
          title: '可视化生成',
          description: '使用多种库自动生成专业图表'
        },
        {
          icon: 'el-icon-edit-outline',
          title: '自然语言编辑',
          description: '通过自然语言指令修改和优化图表'
        },
        {
          icon: 'el-icon-document-copy',
          title: '图表解释',
          description: '为生成的可视化提供详细解释'
        },
        {
          icon: 'el-icon-star-off',
          title: '信息图表',
          description: '生成美观的信息图表和数据故事'
        }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
.demo-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.demo-content {
  .features {
    h3 {
      font-size: 20px;
      color: #333;
      margin-bottom: 20px;
    }
  }

  .feature-card {
    text-align: center;
    margin-bottom: 20px;
    
    .feature-icon {
      font-size: 48px;
      color: #67c23a;
      margin-bottom: 15px;
    }

    h4 {
      font-size: 18px;
      color: #333;
      margin-bottom: 10px;
    }

    p {
      color: #666;
      font-size: 14px;
      line-height: 1.6;
    }
  }

  .try-section {
    padding: 40px 0;
  }
}
</style>
