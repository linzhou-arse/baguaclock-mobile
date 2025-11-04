# 快速开始指南

## 🚀 5分钟快速上手

### Windows用户

#### 1. 安装依赖（2分钟）

```powershell
# 安装Python 3.9+
# 然后安装依赖
cd mobile_app
pip install -r requirements_mobile.txt
```

#### 2. 测试运行（1分钟）

```powershell
python main.py
```

如果看到界面，说明基础环境OK！

#### 3. 构建Android APK（需要Android SDK）

```powershell
# 安装buildozer
pip install buildozer

# 构建（首次需要较长时间下载依赖）
buildozer android debug
```

### Linux用户

#### 1. 安装依赖

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev build-essential
cd mobile_app
pip3 install -r requirements_mobile.txt
```

#### 2. 测试运行

```bash
python3 main.py
```

#### 3. 构建APK

```bash
pip3 install buildozer
buildozer android debug
```

### HarmonyOS用户

#### 1. 安装DevEco Studio

- 下载：https://developer.harmonyos.com/
- 安装并配置HarmonyOS SDK

#### 2. 创建项目

- File > New > Create Project
- 选择Empty Ability (Python)
- 配置项目信息

#### 3. 导入代码

将 `mobile_app/` 目录下的代码复制到HarmonyOS项目

#### 4. 运行

在DevEco Studio中点击运行按钮

## 📝 常见问题

**Q: 运行时报错找不到模块？**
A: 确保安装了所有依赖：`pip install -r requirements_mobile.txt`

**Q: Android构建失败？**
A: 需要安装Android SDK和NDK，参考 `DEPLOYMENT_GUIDE.md`

**Q: 界面显示不正常？**
A: 检查Kivy和KivyMD是否正确安装

**Q: HarmonyOS如何运行？**
A: 参考 `harmonyos/README_HarmonyOS.md`

## 🎯 下一步

- 查看 `README_MOBILE.md` 了解完整功能
- 查看 `DEPLOYMENT_GUIDE.md` 了解详细部署流程
- 查看 `harmonyos/README_HarmonyOS.md` 了解HarmonyOS适配

