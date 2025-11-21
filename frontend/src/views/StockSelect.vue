<!-- StockSelect.vue -->
<template>
  <div class="stock-select-view">
    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="成交量选股" name="volume">
          <VolSelect ref="volSelectRef" @date-change="handleDateChange" />
        </el-tab-pane>
        <el-tab-pane label="成交量趋势" name="volLine">
          <VolLine ref="volLineRef" @date-change="handleDateChange"/>
        </el-tab-pane>
        <el-tab-pane label="趋势选股" name="trend">
          <TrendSelect ref="trendSelectRef" @date-change="handleDateChange" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import VolSelect from './VolSelect.vue'
import TrendSelect from './TrendSelect.vue'
import VolLine from './VolLine.vue'

const activeTab = ref('volume')
const volSelectRef = ref(null)
const trendSelectRef = ref(null)
const volLineRef = ref(null)

const handleDateChange = (date) => {
  // 可以在这里处理日期变化事件
  console.log('选股日期已更改:', date)
}
</script>

<style scoped>
.stock-select-view {
  padding: 0px;
}
</style>