# GitHub Actions 自动构建APK指南

## 🚀 最简单的方法 - 无需本地环境

使用GitHub Actions可以在云端自动构建APK，完全不需要安装WSL、Android SDK等复杂环境。

## 步骤1：上传代码到GitHub

### 方法A：使用Git命令（推荐）

```bash
# 1. 初始化Git仓库（如果还没有）
cd "D:\xianmuweijianjia\py_suanming传统版 - 安卓版"
git init

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "初始化项目"

# 4. 在GitHub上创建新仓库，然后推送
git remote add origin https://github.com/你的用户名/你的仓库名.git
git branch -M main
git push -u origin main
```

### 方法B：使用GitHub Desktop（图形界面）

1. 下载GitHub Desktop：https://desktop.github.com/
2. 登录GitHub账号
3. 点击"File" → "Add Local Repository"
4. 选择项目目录
5. 点击"Publish repository"

## 步骤2：启用GitHub Actions

1. 打开GitHub仓库页面
2. 点击"Actions"标签
3. 如果看到"Workflow file was not found in .github/workflows"，点击"set up a workflow yourself"
4. 如果已经有`.github/workflows/build_apk.yml`文件，Actions会自动启用

## 步骤3：触发构建

1. 在GitHub仓库页面，点击"Actions"标签
2. 选择"Build Android APK"工作流
3. 点击"Run workflow"
4. 选择构建类型：
   - **Debug版本**：适合测试，构建更快
   - **Release版本**：适合正式发布，需要签名
5. 点击绿色的"Run workflow"按钮

## 步骤4：等待构建完成

- 构建过程通常需要10-30分钟
- 可以在"Actions"页面查看构建进度
- 绿色✓表示成功，红色✗表示失败

## 步骤5：下载APK

1. 构建完成后，点击构建任务
2. 滚动到页面底部，找到"Artifacts"
3. 点击"apk-file"下载
4. 解压ZIP文件，找到APK文件

## ⚙️ 配置说明

### 自动构建（可选）

修改`.github/workflows/build_apk.yml`，添加自动触发：

```yaml
on:
  push:
    branches: [ main ]
  workflow_dispatch:
```

这样每次推送代码到main分支时，会自动构建APK。

### Release版本签名（可选）

如果需要签名Release版本，需要：

1. 生成签名密钥：
   ```bash
   keytool -genkey -v -keystore baguaclock.keystore -alias baguaclock -keyalg RSA -keysize 2048 -validity 10000
   ```

2. 在GitHub仓库中添加Secrets：
   - Settings → Secrets → New repository secret
   - 添加以下Secrets：
     - `KEYSTORE_BASE64`：密钥库文件的Base64编码
     - `KEYSTORE_PASSWORD`：密钥库密码
     - `KEY_ALIAS`：密钥别名
     - `KEY_PASSWORD`：密钥密码

3. 修改`buildozer.spec`添加签名配置

## ❓ 常见问题

### Q: 构建失败怎么办？

**A:** 查看构建日志：
1. 点击失败的构建任务
2. 查看"Build APK"步骤的日志
3. 根据错误信息修复问题

常见错误：
- **模块导入错误**：检查`copy_modules.py`是否正确复制了所有模块
- **依赖下载失败**：网络问题，重试即可
- **内存不足**：GitHub Actions有内存限制，可能需要优化构建配置

### Q: 需要付费吗？

**A:** 不需要！GitHub Actions对公开仓库完全免费，私有仓库每月有2000分钟免费额度。

### Q: 可以自动构建多个版本吗？

**A:** 可以！修改工作流文件，添加矩阵构建：

```yaml
strategy:
  matrix:
    arch: [arm64-v8a, armeabi-v7a]
```

### Q: 构建速度慢怎么办？

**A:** 
- 使用Debug版本（更快）
- 优化依赖，减少不必要的包
- 使用构建缓存（如果支持）

## 📱 安装APK到手机

下载APK后：

1. **USB安装**：
   ```bash
   adb install app-debug.apk
   ```

2. **直接安装**：
   - 将APK文件复制到手机
   - 在手机上点击APK文件
   - 允许"未知来源"安装

## 🎉 完成！

现在您可以在任何地方构建APK，无需本地环境！

---

**提示**：如果GitHub Actions不可用，可以查看其他构建方案文档。

