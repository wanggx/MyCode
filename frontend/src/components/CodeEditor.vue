<template>
  <div class="code-editor-wrap">
    <div class="editor-toolbar">
      <span class="dot red"></span>
      <span class="dot yellow"></span>
      <span class="dot green"></span>
      <span class="filename">{{ filename }}</span>
      <span class="mode-badge">{{ readOnly ? '只读' : '编辑中' }}</span>
    </div>
    <textarea
      ref="textarea"
      :value="modelValue"
      :readonly="readOnly"
      class="code-textarea"
      :class="{ editable: !readOnly }"
      spellcheck="false"
      @input="$emit('update:modelValue', $event.target.value)"
      @keydown.ctrl.s.prevent="$emit('save', $event.target.value)"
      @keydown.meta.s.prevent="$emit('save', $event.target.value)"
      placeholder="# 在此编写策略代码..."
    ></textarea>
    <div class="editor-status">
      <span>Python</span><span>|</span><span>UTF-8</span><span>|</span>
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
  emits: ['update:modelValue', 'save']
}
</script>

<style scoped>
.code-editor-wrap {
  display: flex; flex-direction: column; height: 100%;
  border-radius: 6px; overflow: hidden;
  border: 1px solid #e0e0e0;
}
.editor-toolbar {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 12px; background: #2d2d2d; flex-shrink: 0;
}
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.red { background: #ff5f56; } .dot.yellow { background: #ffbd2e; } .dot.green { background: #27c93f; }
.filename { color: #ccc; font-size: 12px; margin-left: 8px; }
.mode-badge { margin-left: auto; color: #999; font-size: 11px; padding: 2px 8px; background: #1e1e1e; border-radius: 3px; }
.code-textarea {
  flex: 1; width: 100%; border: none; outline: none; resize: none;
  padding: 16px; font-family: 'SF Mono','Fira Code',Menlo,Consolas,monospace;
  font-size: 13px; line-height: 1.65; tab-size: 4;
  background: #1e1e1e; color: #d4d4d4;
}
.code-textarea::placeholder { color: #666; }
.code-textarea.editable { background: #1a1a1a; }
.editor-status {
  display: flex; align-items: center; gap: 10px;
  padding: 4px 16px; background: #007acc; color: #fff;
  font-size: 11px; flex-shrink: 0;
}
</style>
