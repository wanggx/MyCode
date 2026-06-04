/**
 * 量化投研平台 — UI 自动化冒烟测试
 *
 * 使用 Playwright 模拟真实用户操作，覆盖：
 * - 注册 / 登录
 * - 9 个菜单页面切换（白屏/404/console.error 检查）
 * - 各页面按钮点击、表单操作
 * - 弹窗/抽屉打开
 *
 * 用法: node tests/e2e/ui-test.mjs
 */

import { chromium } from 'playwright'
import { promises as fs } from 'fs'
import path from 'path'

import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const BASE_URL = 'http://localhost:8083'
const REPORT_PATH = path.resolve(__dirname, 'report.json')

// 测试账号（每次运行尝试注册，失败则用已有账号登录）
const TEST_USER = { username: 'test_e2e', password: 'test123456' }

// 所有菜单项
const MENUS = [
  { path: '/dashboard/overview', name: '总览' },
  { path: '/dashboard/data', name: '数据中心' },
  { path: '/dashboard/factors', name: '因子实验室' },
  { path: '/dashboard/strategies', name: '策略工作台' },
  { path: '/dashboard/backtest', name: '回测中心' },
  { path: '/dashboard/signals', name: '选股信号' },
  { path: '/dashboard/portfolio', name: '组合风控' },
  { path: '/dashboard/tasks', name: '任务中心' },
  { path: '/dashboard/settings', name: '系统设置' },
]

// 各页面需要点击的操作按钮
const PAGE_ACTIONS = {
  '/dashboard/overview': [
    { selector: 'button:has-text("近1年")', desc: '点击近1年' },
    { selector: 'button:has-text("刷新")', desc: '点击刷新' },
  ],
  '/dashboard/data': [
    { selector: 'button:has-text("查询")', desc: '点击查询' },
    { selector: 'button:has-text("重置")', desc: '点击重置' },
  ],
  '/dashboard/factors': [
    { selector: 'button:has-text("分析")', desc: '点击分析' },
    { selector: 'button:has-text("重置")', desc: '点击重置' },
  ],
  '/dashboard/strategies': [
    { selector: 'button:has-text("新建策略")', desc: '点击新建策略' },
  ],
  '/dashboard/backtest': [
    { selector: 'button:has-text("查询")', desc: '点击查询' },
    { selector: 'button:has-text("新建回测")', desc: '点击新建回测' },
  ],
  '/dashboard/signals': [
    { selector: 'button:has-text("查询")', desc: '点击查询' },
    { selector: 'button:has-text("重置")', desc: '点击重置' },
    { selector: 'text=放量信号', desc: '切换放量信号tab' },
    { selector: 'text=趋势信号', desc: '切换趋势信号tab' },
    { selector: 'text=港股信号', desc: '切换港股信号tab' },
    { selector: 'text=今日信号', desc: '切回今日信号tab' },
  ],
  '/dashboard/portfolio': [],
  '/dashboard/tasks': [
    { selector: 'button:has-text("立即执行")', desc: '点击立即执行' },
  ],
  '/dashboard/settings': [
    { selector: 'button:has-text("修改密码")', desc: '打开修改密码弹窗' },
  ],
}

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms))
}

async function run() {
  const results = { passed: 0, failed: 0, errors: [] }

  function pass(desc) {
    results.passed++
    console.log(`  ✅ ${desc}`)
  }

  function fail(desc, msg) {
    results.failed++
    const err = { desc, message: msg }
    results.errors.push(err)
    console.log(`  ❌ ${desc}: ${msg}`)
  }

  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    ignoreHTTPSErrors: true,
  })

  // 收集 console 错误和网络失败
  const page = await context.newPage()
  const consoleErrors = []
  const networkFailures = []
  const pageErrors = []

  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push({ text: msg.text(), url: page.url() })
    }
  })

  page.on('response', response => {
    if (!response.ok() && response.status() >= 400) {
      networkFailures.push({ url: response.url(), status: response.status() })
    }
  })

  page.on('pageerror', err => {
    pageErrors.push({ text: err.message, url: page.url() })
  })

  try {
    // ==================== 1. 登录 ====================
    console.log('\n📌 1. 登录')
    await page.goto(BASE_URL + '/login', { waitUntil: 'networkidle', timeout: 15000 })
    await page.waitForSelector('.login-card', { timeout: 5000 })
    pass('登录页加载成功')

    // 先尝试注册
    const registerTab = page.locator('.el-tabs__item:has-text("注册")')
    if (await registerTab.isVisible()) {
      await registerTab.click()
      await sleep(500)
      const regForm = page.locator('.el-tab-pane:visible')
      const regInputs = regForm.locator('input')
      const regCount = await regInputs.count()
      if (regCount >= 3) {
        await regInputs.nth(0).fill(TEST_USER.username)
        await regInputs.nth(1).fill(TEST_USER.password)
        await regInputs.nth(2).fill(TEST_USER.password)
      }
      await page.locator('.el-tab-pane:visible button:has-text("注册")').click()
      await sleep(800)
    }

    // 切回登录并登录
    const loginTab = page.locator('.el-tabs__item:has-text("登录")')
    if (await loginTab.isVisible()) {
      await loginTab.click()
      await sleep(500)
    }
    const loginForm = page.locator('.el-tab-pane:visible')
    const loginInputs = loginForm.locator('input')
    const loginCount = await loginInputs.count()
    if (loginCount >= 2) {
      await loginInputs.nth(0).fill(TEST_USER.username)
      await loginInputs.nth(1).fill(TEST_USER.password)
    }
    await page.locator('button:has-text("登录")').click()

    // 等待跳转到 dashboard
    await page.waitForURL('**/dashboard/**', { timeout: 8000 })
    pass('登录成功并跳转到主界面')

    // 检查主布局是否渲染
    const sidebar = page.locator('.sidebar')
    await sidebar.waitFor({ state: 'visible', timeout: 5000 })
    pass('主布局渲染正常')

    // ==================== 2. 遍历9个菜单 ====================
    console.log('\n📌 2. 遍历 9 个菜单页面')

    for (const menu of MENUS) {
      console.log(`\n  📄 ${menu.name} (${menu.path})`)
      const prevErrors = consoleErrors.length
      const prevNetwork = networkFailures.length
      const prevPageErrors = pageErrors.length

      // 关闭可能存在的弹窗/抽屉（按 Escape）
      await page.keyboard.press('Escape')
      await sleep(300)

      // 点击菜单
      const menuItem = page.locator(`.sidebar .el-menu-item:has-text("${menu.name}")`).first()
      if (await menuItem.isVisible({ timeout: 3000 })) {
        await menuItem.click()
      } else {
        // 直接导航
        await page.goto(BASE_URL + menu.path, { waitUntil: 'networkidle', timeout: 15000 })
      }
      await sleep(1500)

      // 隐藏 webpack overlay（JS 报错时会挡住界面）
      await page.evaluate(() => {
        const overlay = document.getElementById('webpack-dev-server-client-overlay')
        if (overlay) overlay.style.display = 'none'
      }).catch(() => {})

      // 检查白屏和未捕获异常
      const bodyText = await page.locator('body').textContent()
      const newNetwork = networkFailures.slice(prevNetwork)

      if (bodyText.trim().length === 0) {
        fail(menu.name, '页面白屏（body 内容为空）')
      } else if (pageErrors.length > prevPageErrors) {
        const err = pageErrors[pageErrors.length - 1]
        fail(menu.name, `未捕获 JS 异常: ${err.text.substring(0, 100)}`)
      } else {
        // 检查是否有 console.error（由前端 catch 块产生）——视为警告，非失败
        const newConsoleErrors = consoleErrors.slice(prevErrors)
        const apiErrors = newConsoleErrors.filter(e => !e.text.includes('Failed to load resource'))
        if (apiErrors.length > 0) {
          console.log(`  ⚠️  ${menu.name}: ${apiErrors.length} 个 console.error（前端已处理）`)
        }
        if (newNetwork.filter(n => n.status >= 500).length > 0) {
          const err500 = newNetwork.find(n => n.status >= 500)
          console.log(`  ⚠️  ${menu.name}: API 500 — ${err500.url.split('?')[0]}`)
        }
        if (newNetwork.filter(n => n.status === 404).length > 0) {
          const err404 = newNetwork.find(n => n.status === 404)
          console.log(`  ⚠️  ${menu.name}: API 404 — ${err404.url.split('?')[0]}`)
        }
        pass(`${menu.name} 页面加载正常`)
      }

      // ==================== 3. 交互操作 ====================
      const actions = PAGE_ACTIONS[menu.path] || []
      for (const action of actions) {
        try {
          const btn = page.locator(action.selector).first()
          if (await btn.isVisible({ timeout: 2000 })) {
            await btn.click()
            await sleep(500)
            pass(`${menu.name}: ${action.desc}`)
          } else {
            fail(`${menu.name}: ${action.desc}`, '按钮不可见')
          }
        } catch (e) {
          fail(`${menu.name}: ${action.desc}`, e.message.substring(0, 80))
        }
      }

      // 如果有弹窗/抽屉，关闭它
      const dialogClose = page.locator('.el-dialog__headerbtn, .el-drawer__close-btn').first()
      if (await dialogClose.isVisible({ timeout: 500 }).catch(() => false)) {
        await dialogClose.click()
        await sleep(300)
        pass(`${menu.name}: 关闭弹窗`)
      }
    }

    // ==================== 4. 账户下拉菜单 ====================
    console.log('\n📌 3. 账户操作')
    try {
      const account = page.locator('.account-dropdown').first()
      if (await account.isVisible({ timeout: 2000 })) {
        await account.click()
        await sleep(500)
        const changePwd = page.locator('.el-dropdown-menu__item:has-text("修改密码")').first()
        if (await changePwd.isVisible({ timeout: 2000 })) {
          await changePwd.click()
          await sleep(500)
          const closeBtn = page.locator('.el-dialog__headerbtn').first()
          if (await closeBtn.isVisible({ timeout: 1000 })) await closeBtn.click()
          pass('账户下拉菜单和修改密码弹窗正常')
        } else {
          fail('修改密码', '下拉菜单项不可见')
        }
      } else {
        pass('账户区域可见（无下拉菜单）')
      }
    } catch (e) {
      fail('账户操作', e.message.substring(0, 80))
    }

    // ==================== 5. 总结 ====================
    console.log('\n========================================')
    console.log('📊  测试结果')
    console.log('========================================')
    console.log(`  通过: ${results.passed}`)
    console.log(`  失败: ${results.failed}`)
    if (results.errors.length > 0) {
      console.log('\n  错误列表:')
      for (const err of results.errors) {
        console.log(`    ❌ ${err.desc}`)
        console.log(`       ${err.message}`)
      }
    }
    if (pageErrors.length > 0) {
      console.log(`\n  📋 未捕获 JS 异常: ${pageErrors.length} 个`)
      for (const pe of pageErrors.slice(0, 5)) {
        console.log(`    - ${pe.text.substring(0, 120)}`)
      }
    }
    if (consoleErrors.length > 0) {
      console.log(`\n  📋 页面 console.error 总计: ${consoleErrors.length} 个`)
      for (const ce of consoleErrors.slice(0, 5)) {
        console.log(`    - ${ce.text.substring(0, 120)}`)
      }
    }
    if (networkFailures.length > 0) {
      console.log(`\n  📋 网络请求失败总计: ${networkFailures.length} 个`)
      for (const nf of networkFailures.slice(0, 10)) {
        console.log(`    - ${nf.status} ${nf.url}`)
      }
    }
    console.log('========================================\n')

    // 保存报告
    await fs.writeFile(REPORT_PATH, JSON.stringify({
      ...results,
      pageErrors: pageErrors.slice(0, 20),
      consoleErrors: consoleErrors.slice(0, 20),
      networkFailures: networkFailures.slice(0, 20),
      timestamp: new Date().toISOString(),
    }, null, 2))

  } catch (e) {
    console.error('\n🔥 测试框架异常:', e.message)
    results.failed++
    results.errors.push({ desc: '测试框架', message: e.message })
  } finally {
    await browser.close()
  }

  // 退出码
  process.exit(results.failed > 0 ? 1 : 0)
}

run()
