# 八卦时钟移动版 - 部署指南

## 📱 完整部署流程

### 一、Android APK构建

#### 1. 环境准备

**Windows系统：**
```bash
# 安装Python 3.9+
# 安装Git for Windows
# 安装Android SDK
# 安装Cython
pip install cython
```

**Linux系统：**
```bash
# 安装依赖
sudo apt-get update
sudo apt-get install -y \
    git \
    unzip \
    openjdk-11-jdk \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    cython

# 安装Android SDK
# 下载并解压到 ~/Android/Sdk
```

#### 2. 安装Buildozer

```bash
pip install buildozer
```

#### 3. 配置环境变量

**Linux/Mac:**
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export ANDROIDSDK=~/Android/Sdk
export ANDROIDNDK=~/Android/Sdk/ndk/25.1.8937393
export PATH=$PATH:$ANDROIDSDK/platform-tools:$ANDROIDSDK/tools
```

**Windows:**
```powershell
# 设置环境变量
$env:ANDROIDSDK = "C:\Users\YourName\AppData\Local\Android\Sdk"
$env:ANDROIDNDK = "$env:ANDROIDSDK\ndk\25.1.8937393"
$env:PATH += ";$env:ANDROIDSDK\platform-tools;$env:ANDROIDSDK\tools"
```

#### 4. 构建APK

```bash
cd mobile_app

# 首次构建（会下载依赖，需要较长时间）
buildozer android debug

# 后续构建（更快）
buildozer android debug

# 构建发布版（需要签名）
buildozer android release
```

#### 5. 安装到设备

```bash
# 通过ADB安装
adb install bin/*.apk

# 或直接传输APK文件到手机安装
```

### 二、HarmonyOS应用构建

#### 1. 环境准备

- 下载并安装 **DevEco Studio**
- 配置HarmonyOS SDK
- 安装HarmonyOS设备模拟器或连接真机

#### 2. 创建项目

1. 打开DevEco Studio
2. 选择 **File > New > Create Project**
3. 选择 **Empty Ability** 模板
4. 选择 **Python** 作为开发语言
5. 配置项目信息：
   - Project Name: BaguaClock
   - Package Name: com.quanhang.baguaclock
   - SDK Version: API 9 (HarmonyOS 4.0+)

#### 3. 导入代码

```bash
# 将mobile_app目录下的Python代码复制到项目
cp -r mobile_app/* harmonyos_project/entry/src/main/python/
```

#### 4. 配置ArkUI界面

在 `entry/src/main/ets/pages/Index.ets` 中创建界面：

```typescript
import webview from '@ohos.web.webview'
import { PythonBridge } from '../python/PythonBridge'

@Entry
@Component
struct Index {
  @State message: string = '八卦时钟'
  controller: webview.WebviewController = new webview.WebviewController()
  
  build() {
    Column() {
      Text(this.message)
        .fontSize(24)
        .fontWeight(FontWeight.Bold)
      
      // 嵌入Python Web服务
      Web({ 
        src: 'http://localhost:5000',
        controller: this.controller 
      })
        .width('100%')
        .height('100%')
    }
    .width('100%')
    .height('100%')
    .padding(16)
  }
}
```

#### 5. 构建和运行

1. 在DevEco Studio中点击 **Build > Build HAP(s)**
2. 等待构建完成
3. 点击 **Run** 运行到设备或模拟器

### 三、测试

#### Android测试

```bash
# 连接设备
adb devices

# 安装APK
adb install bin/*.apk

# 运行应用
adb shell am start -n com.quanhang.baguaclock/.MainActivity

# 查看日志
adb logcat | grep -i bagua
```

#### HarmonyOS测试

1. 在DevEco Studio中连接设备
2. 点击运行按钮
3. 查看控制台日志

### 四、常见问题

#### 1. Buildozer构建失败

**问题：** 找不到Android SDK
```bash
# 解决方案：检查buildozer.spec中的路径配置
# 或手动设置环境变量
```

**问题：** 编译错误
```bash
# 清理构建缓存
buildozer android clean

# 重新构建
buildozer android debug
```

#### 2. HarmonyOS构建问题

**问题：** Python模块导入失败
```bash
# 确保所有依赖都在requirements_mobile.txt中
# 检查Python路径配置
```

**问题：** 界面不显示
```bash
# 检查Web服务是否启动
# 检查权限配置
```

#### 3. 运行时错误

**问题：** 模块找不到
```bash
# 确保所有Python文件都在正确位置
# 检查sys.path配置
```

**问题：** 性能问题
```bash
# 优化代码，避免阻塞UI线程
# 使用异步操作
```

### 五、发布准备

#### Android发布

1. **生成签名密钥：**
```bash
keytool -genkey -v -keystore bagua_clock.keystore -alias bagua_clock -keyalg RSA -keysize 2048 -validity 10000
```

2. **配置签名：**
在 `buildozer.spec` 中添加：
```ini
[app]
android.keystore = bagua_clock.keystore
android.keystore_password = your_password
android.keyalias = bagua_clock
android.keyalias_password = your_password
```

3. **构建发布版：**
```bash
buildozer android release
```

#### HarmonyOS发布

1. 在DevEco Studio中配置签名
2. 构建发布版HAP
3. 上传到华为应用市场

### 六、性能优化建议

1. **代码优化：**
   - 使用异步操作避免阻塞UI
   - 优化图片资源大小
   - 减少不必要的计算

2. **资源优化：**
   - 压缩图片资源
   - 使用适当的图片格式
   - 移除未使用的资源

3. **构建优化：**
   - 启用代码混淆（Android）
   - 启用资源压缩
   - 优化APK大小

### 七、更新和维护

#### 版本更新

1. 更新 `buildozer.spec` 中的版本号
2. 更新 `config.json` 中的版本信息
3. 重新构建并测试
4. 发布新版本

#### 日志收集

```bash
# Android日志
adb logcat > bagua_clock.log

# HarmonyOS日志
# 在DevEco Studio中查看
```

---

**注意事项：**
- Android最低版本：API 21 (Android 5.0)
- HarmonyOS最低版本：4.0
- 建议在真机上测试，模拟器可能性能不足
- 首次构建时间较长，请耐心等待

