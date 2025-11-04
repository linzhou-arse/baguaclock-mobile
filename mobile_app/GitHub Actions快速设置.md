# 🚀 GitHub Actions 快速设置（3步完成）

## 步骤1：运行设置脚本

双击运行：
```
mobile_app/设置GitHub Actions.bat
```

这个脚本会自动：
- ✅ 检查Git是否安装
- ✅ 初始化Git仓库（如果还没有）
- ✅ 创建GitHub Actions工作流文件
- ✅ 添加所有文件到Git

## 步骤2：创建GitHub仓库并推送代码

### 2.1 在GitHub上创建新仓库

1. 访问：https://github.com/new
2. 填写仓库名称（例如：`baguaclock-mobile`）
3. 选择 **Public**（公开仓库免费）或 **Private**（私有仓库）
4. **不要**勾选"Initialize with README"
5. 点击 **"Create repository"**

### 2.2 推送代码到GitHub

在设置脚本完成后，运行以下命令：

```bash
# 添加远程仓库（替换为你的仓库URL）
git remote add origin https://github.com/你的用户名/仓库名.git

# 设置主分支
git branch -M main

# 推送代码
git push -u origin main
```

**或者使用设置脚本的交互模式**：
- 运行 `设置GitHub Actions.bat` 时选择 "Y" 推送代码
- 输入你的GitHub仓库URL

## 步骤3：触发构建并下载APK

### 3.1 触发构建

1. 访问你的GitHub仓库页面
2. 点击顶部的 **"Actions"** 标签
3. 在左侧选择 **"Build Android APK"** 工作流
4. 点击右侧的 **"Run workflow"** 按钮
5. 选择构建类型：
   - **Debug**：调试版，构建更快，适合测试
   - **Release**：发布版，需要签名，适合正式使用
6. 点击绿色的 **"Run workflow"** 按钮

### 3.2 等待构建完成

- 构建过程通常需要 **10-30分钟**
- 可以在Actions页面查看实时日志
- 绿色✓表示成功，红色✗表示失败

### 3.3 下载APK

1. 构建完成后，点击构建任务
2. 滚动到页面底部
3. 在 **"Artifacts"** 部分找到 **"apk-file"**
4. 点击下载（ZIP格式）
5. 解压ZIP文件，找到APK文件

## 📱 安装APK到手机

### 方法1：USB安装（推荐）

```bash
adb install app-debug.apk
```

### 方法2：直接传输

1. 将APK文件复制到手机
2. 在手机上点击APK文件
3. 允许"未知来源"安装
4. 完成安装

## ❓ 常见问题

### Q: Git未安装怎么办？

**A:** 
1. 下载：https://git-scm.com/download/win
2. 安装后重启设置脚本

### Q: 推送代码时提示需要认证？

**A:** 
1. 使用GitHub Personal Access Token
2. 或使用GitHub Desktop（图形界面）

### Q: 构建失败怎么办？

**A:** 
1. 查看构建日志（点击失败的任务）
2. 检查错误信息
3. 常见问题：
   - 模块导入错误：检查`copy_modules.py`是否正确
   - 网络问题：重试构建
   - 依赖下载失败：检查网络连接

### Q: 需要付费吗？

**A:** 
- **公开仓库**：完全免费
- **私有仓库**：每月2000分钟免费额度（通常足够使用）

## 🎉 完成！

现在您可以在任何地方构建APK，无需本地环境！

每次需要新APK时：
1. 访问GitHub仓库
2. 点击Actions → Run workflow
3. 等待构建完成
4. 下载APK

---

**提示**：如果遇到问题，请查看 `GitHub Actions构建指南.md` 获取详细说明。

