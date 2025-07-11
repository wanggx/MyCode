<template>
  <div id="app">
    <el-button @click="toggleTheme" style="position: absolute; right: 20px; top: 20px;">切换主题</el-button>
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      dark: false
    }
  },
  methods: {
    toggleTheme() {
      this.dark = !this.dark;
      document.body.classList.toggle('dark-theme', this.dark);
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  min-height: 100vh;
  background: var(--bg-color, #fff);
}
body.dark-theme {
  --bg-color: #222;
  color: #eee;
  background: #222;
}
</style>
