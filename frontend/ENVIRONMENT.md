# 環境配置說明

## 環境類型

### 1. 開發環境 (Development)
- **後端地址**: `http://localhost:8080`
- **啟動命令**: `npm run dev`
- **構建命令**: `npm run build:dev`

### 2. 測試環境 (Test)
- **後端地址**: `http://test-backend:8080`
- **啟動命令**: `npm run test`
- **構建命令**: `npm run build:test`

### 3. 生產環境 (Production)
- **後端地址**: `http://production-backend:8080`
- **啟動命令**: `npm run prod`
- **構建命令**: `npm run build:prod`

## 使用方法

### 啟動開發服務器
```bash
# 開發環境
npm run dev

# 測試環境
npm run test

# 生產環境
npm run prod
```

### 構建應用
```bash
# 開發環境構建
npm run build:dev

# 測試環境構建
npm run build:test

# 生產環境構建
npm run build:prod
```

## 環境變量

可以通過設置環境變量來覆蓋默認配置：

```bash
# 設置自定義後端地址
export VUE_APP_BACKEND_URL=http://your-custom-backend:8080

# 然後啟動服務
npm run dev
```

## 代理配置

所有 `/api` 開頭的請求都會被代理到對應環境的後端服務器：

- 開發環境: `http://localhost:8080`
- 測試環境: `http://test-backend:8080`
- 生產環境: `http://production-backend:8080`

## 配置文件

- `env.development` - 開發環境配置
- `env.test` - 測試環境配置
- `env.production` - 生產環境配置
- `src/config/api.js` - API 配置文件 