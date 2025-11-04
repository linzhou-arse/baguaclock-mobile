# HarmonyOS 4.0+ 适配指南

## 概述

HarmonyOS 4.0+ 支持Python运行时，可以通过以下方式将八卦时钟应用适配到HarmonyOS平台。

## 方案一：使用HarmonyOS Python运行时（推荐）

### 1. 环境准备

```bash
# 安装HarmonyOS开发工具
# 下载DevEco Studio
# 配置HarmonyOS SDK
```

### 2. 创建HarmonyOS项目

```bash
# 使用DevEco Studio创建Python应用项目
# 选择模板：Python应用
```

### 3. 项目结构

```
harmonyos_app/
├── entry/
│   └── src/
│       └── main/
│           ├── ets/
│           │   └── pages/
│           │       └── Index.ets  # ArkUI主页面
│           ├── python/
│           │   └── main.py        # Python主程序
│           └── resources/
└── build-profile.json5
```

### 4. 集成Python代码

将 `mobile_app/` 目录下的Python代码复制到HarmonyOS项目的 `python/` 目录。

### 5. 创建ArkUI界面

在 `entry/src/main/ets/pages/Index.ets` 中创建HarmonyOS原生界面，通过FFI调用Python逻辑。

## 方案二：使用WebView + Python Web服务

### 1. 创建Flask/FastAPI Web服务

```python
# harmonyos_app/web_service.py
from flask import Flask, jsonify
from mobile_app.services.bazi_service import BaziService

app = Flask(__name__)
service = BaziService()

@app.route('/api/bazi/calculate', methods=['POST'])
def calculate_bazi():
    data = request.json
    result = service.calculate(**data)
    return jsonify(result)
```

### 2. 在HarmonyOS中嵌入WebView

```typescript
// Index.ets
import webview from '@ohos.web.webview'

@Entry
@Component
struct Index {
  controller: webview.WebviewController = new webview.WebviewController()
  
  build() {
    Column() {
      Web({ src: 'http://localhost:5000', controller: this.controller })
    }
  }
}
```

## 方案三：使用Kivy + Buildozer（实验性）

目前Buildozer主要支持Android，但可以通过以下方式尝试：

1. 使用Android运行时环境
2. 通过兼容层运行APK

## 推荐方案

**推荐使用方案一**：HarmonyOS原生Python支持，性能最好，体验最佳。

## 构建步骤

### 1. 安装依赖

```bash
cd harmonyos_app
npm install  # 如果使用Web方案
```

### 2. 配置构建

编辑 `build-profile.json5`，配置应用信息。

### 3. 构建应用

```bash
# 在DevEco Studio中
# Build -> Build HAP(s)/APP(s) -> Build HAP(s)
```

### 4. 安装到设备

```bash
# 通过USB连接HarmonyOS设备
# 在DevEco Studio中点击运行
```

## 注意事项

1. **Python版本**：HarmonyOS 4.0+ 支持Python 3.9+
2. **依赖库**：某些Python库可能不兼容，需要测试
3. **性能**：Python运行时性能可能不如原生ArkTS，建议关键路径使用原生代码
4. **权限**：需要在 `config.json` 中声明所需权限

## 测试

```bash
# 在HarmonyOS设备上安装应用
# 测试各项功能
# 检查性能表现
```

## 更新日志

- 2025-01-XX: 初始版本，支持HarmonyOS 4.0+

