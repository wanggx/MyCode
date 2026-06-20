<template>
  <div class="code-editor-wrap">
    <div class="editor-toolbar">
      <span class="filename">{{ filename }}</span>
    </div>
    <div class="editor-body">
      <div ref="lineNumbers" class="line-numbers" :style="{ minHeight: lineHeight }">
        <div v-for="n in lineCount" :key="n">{{ n }}</div>
      </div>
      <textarea
        ref="textarea"
        :value="modelValue"
        :readonly="readOnly"
        class="code-textarea"
        :class="{ editable: !readOnly }"
        spellcheck="false"
        @input="onInput"
        @keydown.ctrl.s.prevent="$emit('save', modelValue)"
        @keydown.meta.s.prevent="$emit('save', modelValue)"
        @scroll="syncScroll"
        placeholder="# 在此编写策略代码..."
      ></textarea>
    </div>
    <div class="editor-status">
      <span>Python</span><span>|</span><span>UTF-8</span><span>|</span>
      <span>{{ lineCount }} 行</span><span>|</span>
      <span>{{ readOnly ? '只读' : '编辑中' }} · Ctrl+S 保存</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CodeEditor',
  props: {
    modelValue: { type: String, default: '' },
    readOnly: { type: Boolean, default: false },
    filename: { type: String, default: 'strategy.py' }
  },
  emits: ['update:modelValue', 'save'],
  computed: {
    lineCount() {
      return (this.modelValue || '').split('\n').length
    },
    lineHeight() {
      // 匹配 textarea 的行高: font-size 13px * line-height 1.65 = 21.45px
      return (this.modelValue || '').split('\n').length * 21.45 + 32 + 'px'
    }
  },
  methods: {
    onInput(e) {
      this.$emit('update:modelValue', e.target.value)
    },
    syncScroll() {
      const textarea = this.$refs.textarea
      const lineNums = this.$refs.lineNumbers
      if (textarea && lineNums) {
        lineNums.scrollTop = textarea.scrollTop
      }
    }
  }
}
</script>

<style scoped>
.code-editor-wrap {
  display: flex; flex-direction: column; height: 100%;
  border-radius: 6px; overflow: hidden;
  border: 1px solid #e0e0e0;
}
.editor-toolbar {
  display: flex; align-items: center;
  padding: 6px 12px; background: #2d2d2d; flex-shrink: 0;
}
.filename { color: #ccc; font-size: 12px; }
.editor-body {
  flex: 1; display: flex; overflow: hidden; min-height: 0;
}
.line-numbers {
  width: 44px; flex-shrink: 0; overflow: hidden;
  background: #1a1a1a; color: #6a737d;
  font-family: 'SF Mono','Fira Code',Menlo,Consolas,monospace;
  font-size: 13px; line-height: 1.65; text-align: right;
  padding: 16px 0 16px 4px;
  user-select: none; pointer-events: none;
  border-right: 1px solid #333;
}
.line-numbers div {
  height: 21.45px; /* font-size 13px * 1.65 line-height */
}
.code-textarea {
  flex: 1; border: none; outline: none; resize: none;
  padding: 16px 16px 16px 6px; font-family: 'SF Mono','Fira Code',Menlo,Consolas,monospace;
  font-size: 13px; line-height: 1.65; tab-size: 4;
  background: #1e1e1e; color: #d4d4d4;
  overflow-y: auto; white-space: pre; word-wrap: normal;
}
.code-textarea::placeholder { color: #666; }
.code-textarea.editable { background: #1a1a1a; }
.editor-status {
  display: flex; align-items: center; gap: 10px;
  padding: 4px 16px; background: #007acc; color: #fff;
  font-size: 11px; flex-shrink: 0;
}
</style>
