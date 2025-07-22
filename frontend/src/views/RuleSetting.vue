<template>
  <div class="rule-setting-page">
    <el-card>
      <div class="rule-setting-title">规则配置</div>
      <div class="rule-setting-content">
        <!-- 这里是规则配置内容占位，后续可扩展 -->
        <el-empty description="暂无规则配置内容" />
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'RuleSetting'
}
</script>

<style scoped>
.rule-setting-page {
  padding: 24px;
}
.rule-setting-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 16px;
}
.rule-setting-content {
  min-height: 120px;
}
</style> 