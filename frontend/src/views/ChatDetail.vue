<template>
  <div class="chat-detail-container">
    <el-card>
      <div slot="header" class="clearfix">
        <el-button icon="el-icon-back" circle @click="$router.push('/')"></el-button>
        <span style="margin-left: 10px">{{ chatName }}</span>
        <el-button 
          type="primary" 
          size="small" 
          style="float: right"
          @click="handleGenerateGoals"
          :loading="generatingGoals"
        >
          自动生成分析目标
        </el-button>
      </div>

      <!-- 数据摘要 -->
      <div v-if="summary" class="summary-section mb-20">
        <el-card>
          <div slot="header">
            <span><i class="el-icon-document"></i> 数据摘要</span>
          </div>
          <div class="summary-content">
            <p><strong>数据集:</strong> {{ summary.name }}</p>
            <p><strong>文件:</strong> {{ summary.file_name }}</p>
            <p><strong>描述:</strong> {{ summary.dataset_description }}</p>
            <div v-if="summary.field_names && summary.field_names.length > 0">
              <p><strong>字段:</strong></p>
              <el-tag 
                v-for="(field, index) in summary.field_names" 
                :key="index"
                size="small"
                style="margin-right: 8px; margin-bottom: 8px"
              >
                {{ field }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 目标列表 -->
      <div class="goals-section">
        <div class="section-header">
          <h3>可视化目标 ({{ goals.length }})</h3>
        </div>
        <el-collapse v-model="activeNames" accordion>
          <el-collapse-item 
            v-for="(goal, index) in goals" 
            :key="index"
            :name="String(index)"
          >
            <template slot="title">
              <div class="goal-title">
                <el-tag size="small" :type="goal.is_auto ? 'success' : 'primary'">
                  {{ goal.is_auto ? '自动生成' : '手动创建' }}
                </el-tag>
                <el-tag size="small" style="margin-left: 10px">{{ goal.visualization || '图表' }}</el-tag>
                <span style="margin-left: 10px; flex: 1">{{ goal.question }}</span>
              </div>
            </template>
            
            <div class="goal-content">
              <p><strong>理由:</strong> {{ goal.rationale || '暂无说明' }}</p>
              
              <!-- 可视化区域 -->
              <div v-if="goal.code" class="visualization-area">
                <div class="code-section mb-10">
                  <el-button 
                    type="text" 
                    @click="showCode = !showCode"
                  >
                    {{ showCode ? '隐藏代码' : '查看代码' }}
                  </el-button>
                  <pre v-show="showCode" class="code-block">{{ goal.code }}</pre>
                </div>
                
                <!-- 直接使用 img 标签显示图片 -->
                <div v-if="goal.raster" class="chart-container">
                  <img :src="'data:image/png;base64,' + goal.raster" alt="可视化图表" style="max-width: 100%; height: auto;" />
                </div>
                
                <div class="actions mt-20">
                  <el-button-group>
                    <el-button type="info" size="small" @click="handleExplain(goal)">
                      <i class="el-icon-document-copy"></i> 解释
                    </el-button>
                    <el-button type="warning" size="small" @click="handleEvaluate(goal)">
                      <i class="el-icon-star-off"></i> 评估
                    </el-button>
                    <el-button type="primary" size="small" @click="handleEdit(goal)">
                      <i class="el-icon-edit"></i> 编辑
                    </el-button>
                    <el-button type="success" size="small" @click="handleRecommend(goal)">
                      <i class="el-icon-connection"></i> 推荐
                    </el-button>
                    <el-dropdown size="small" @command="(command) => handleExport(command, goal)">
                      <el-button type="default" size="small">
                        <i class="el-icon-download"></i> 导出<i class="el-icon-arrow-down el-icon--right"></i>
                      </el-button>
                      <el-dropdown-menu slot="dropdown">
                        <el-dropdown-item command="image">导出为图片</el-dropdown-item>
                        <el-dropdown-item command="code">导出代码</el-dropdown-item>
                        <el-dropdown-item command="spec">导出规格</el-dropdown-item>
                      </el-dropdown-menu>
                    </el-dropdown>
                  </el-button-group>
                </div>
              </div>
              
              <el-button 
                v-else 
                type="success" 
                @click="handleVisualize(goal)"
                :loading="goal.loading"
                icon="el-icon-picture-outline"
              >
                生成可视化
              </el-button>
            </div>
          </el-collapse-item>
        </el-collapse>
        
        <el-empty v-if="goals.length === 0" description="暂无可视化目标，点击生成分析目标按钮开始探索数据"></el-empty>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog title="编辑可视化" :visible.sync="editDialogVisible" width="60%">
      <el-input
        v-model="editInstructions"
        type="textarea"
        :rows="4"
        placeholder="请输入编辑指令，例如：将柱状图改为折线图"
      ></el-input>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import {
  getChatInfo,
  visualize,
  explainVisualization,
  editVisualize,
  generateGoals,
  recommendVisualization,
  evaluateVisualization
} from '@/api'

export default {
  name: 'ChatDetail',
  data() {
    return {
      chatId: this.$route.params.id,
      chatName: '',
      summary: null,
      goals: [],
      activeNames: '',
      editDialogVisible: false,
      currentGoal: null,
      editInstructions: '',
      generatingGoals: false,
      showCode: false
    }
  },
  created() {
    this.loadChatDetail()
  },
  methods: {
    async loadChatDetail() {
      try {
        const res = await getChatInfo(this.chatId)
        this.chatName = res.summary.name
        this.summary = res.summary
        this.goals = res.data || []
      } catch (error) {
        this.$message.error('加载聊天详情失败')
        console.error(error)
      }
    },

    async handleGenerateGoals() {
      if (!this.summary) {
        this.$message.warning('数据摘要尚未生成')
        return
      }

      this.generatingGoals = true
      const loading = this.$loading({
        lock: true,
        text: '正在生成分析目标...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      try {
        const res = await generateGoals(this.summary, this.chatId, 5)
        if (res.status && res.data) {
          this.goals = res.data
          this.$message.success(`成功生成 ${res.data.length} 个分析目标!`)
        }
      } catch (error) {
        this.$message.error('生成目标失败：' + error.message)
      } finally {
        loading.close()
        this.generatingGoals = false
      }
    },

    async handleVisualize(goal) {
      goal.loading = true
      try {
        const res = await visualize(this.summary, goal, this.chatId)
        if (res.status && res.charts && res.charts.length > 0) {
          // 更新 goal 数据
          goal.code = res.charts[0].code
          goal.raster = res.charts[0].raster
          goal.library = res.charts[0].library
          
          // 强制触发 Vue 响应式更新
          this.$set(goal, 'code', goal.code)
          this.$set(goal, 'raster', goal.raster)
          this.$set(goal, 'library', goal.library)
          
          // 等待 DOM 更新
          setTimeout(() => {
            // 不需要手动渲染，让 Vue 自动处理
          }, 100)
        }
      } catch (error) {
        console.error(error)
      } finally {
        goal.loading = false
      }
    },

    async handleExplain(goal) {
      try {
        const res = await explainVisualization(this.chatId, goal.id, goal.code)
        if (res.status && res.explanations) {
          this.$alert(res.explanations[0].explanation, '可视化解释', {
            confirmButtonText: '确定'
          })
        }
      } catch (error) {
        console.error(error)
      }
    },

    async handleRecommend(goal) {
      if (!goal.code) {
        this.$message.warning('请先生成可视化')
        return
      }

      try {
        const res = await recommendVisualization(this.summary, goal.code)
        if (res.status && res.charts && res.charts.length > 0) {
          this.$alert(
            `<pre style="max-height: 400px; overflow: auto;">${res.charts[0].code}</pre>`,
            '推荐的可视化方案',
            {
              dangerouslyUseHTMLString: true,
              confirmButtonText: '确定'
            }
          )
        }
      } catch (error) {
        this.$message.error('推荐失败：' + error.message)
      }
    },

    handleExport(command, goal) {
      switch (command) {
        case 'image':
          this.exportAsImage(goal)
          break
        case 'code':
          this.exportCode(goal)
          break
        case 'spec':
          this.exportSpec(goal)
          break
      }
    },

    exportAsImage(goal) {
      if (!goal.raster) {
        this.$message.warning('没有可导出的图片')
        return
      }
      
      const link = document.createElement('a')
      link.download = `visualization-${goal.id}.png`
      link.href = `data:image/png;base64,${goal.raster}`
      link.click()
      this.$message.success('图片已下载')
    },

    exportCode(goal) {
      if (!goal.code) {
        this.$message.warning('没有可导出的代码')
        return
      }
      
      const blob = new Blob([goal.code], { type: 'text/plain' })
      const link = document.createElement('a')
      link.download = `visualization-${goal.id}.py`
      link.href = URL.createObjectURL(blob)
      link.click()
      URL.revokeObjectURL(link.href)
      this.$message.success('代码已下载')
    },

    exportSpec(goal) {
      if (!goal.spec) {
        this.$message.warning('没有可导出的规格')
        return
      }
      
      const specStr = typeof goal.spec === 'string' ? goal.spec : JSON.stringify(goal.spec, null, 2)
      const blob = new Blob([specStr], { type: 'application/json' })
      const link = document.createElement('a')
      link.download = `visualization-${goal.id}.json`
      link.href = URL.createObjectURL(blob)
      link.click()
      URL.revokeObjectURL(link.href)
      this.$message.success('规格已下载')
    },

    async handleEvaluate(goal) {
      try {
        const loading = this.$loading({
          lock: true,
          text: '正在评估可视化...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        const res = await evaluateVisualization(this.chatId, goal.code, goal)
        loading.close()
        
        if (res.status && res.evaluations) {
          const evalData = res.evaluations
          let content = '<div style="line-height: 2;">'
          for (const [key, value] of Object.entries(evalData)) {
            content += `<p><strong>${key}:</strong> ${value}</p>`
          }
          content += '</div>'
          
          this.$alert(content, '可视化评估报告', {
            dangerouslyUseHTMLString: true,
            confirmButtonText: '确定'
          })
        }
      } catch (error) {
        this.$message.error('评估失败：' + error.message)
      }
    },

    handleEdit(goal) {
      this.currentGoal = goal
      this.editInstructions = ''
      this.editDialogVisible = true
    },

    async submitEdit() {
      if (!this.editInstructions.trim()) {
        this.$message.warning('请输入编辑指令')
        return
      }

      try {
        const res = await editVisualize(
          this.chatId,
          this.currentGoal.id,
          this.summary,
          this.currentGoal.code,
          this.editInstructions
        )
        
        if (res.status && res.charts && res.charts.length > 0) {
          this.currentGoal.code = res.charts[0].code
          this.currentGoal.raster = res.charts[0].raster
          this.editDialogVisible = false
          
          this.$nextTick(() => {
            this.renderChart(this.currentGoal)
          })
          
          this.$message.success('编辑成功')
        }
      } catch (error) {
        console.error(error)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.chat-detail-container {
  padding: 20px;
}

.summary-section {
  .summary-content {
    p {
      margin-bottom: 10px;
      line-height: 1.6;
      
      strong {
        color: #333;
        font-weight: 600;
      }
    }
  }
}

.goals-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    
    h3 {
      margin: 0;
      color: #333;
      font-size: 18px;
    }
  }
}

.goal-title {
  display: flex;
  align-items: center;
  width: 100%;
}

.goal-content {
  p {
    margin-bottom: 15px;
    color: #666;
    line-height: 1.6;
  }
  
  .code-section {
    .code-block {
      background: #f6f8fa;
      padding: 12px;
      border-radius: 4px;
      font-family: 'Courier New', Courier, monospace;
      font-size: 12px;
      overflow-x: auto;
      margin-top: 8px;
      border: 1px solid #e1e4e8;
    }
  }
}

.visualization-area {
  .chart-container {
    min-height: 400px;
    background: #fff;
    border-radius: 4px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }
  
  .actions {
    text-align: right;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #e1e4e8;
  }
}

.mb-20 {
  margin-bottom: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.mr-10 {
  margin-right: 10px;
}
</style>
