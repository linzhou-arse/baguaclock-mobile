# 八卦时钟移动版 - Android & HarmonyOS 4.0+

## 📱 项目简介

这是八卦时钟桌面版的移动端移植版本，支持Android和HarmonyOS 4.0+平台。

## ✨ 核心特性

- ✅ **完全本地化** - 不依赖任何外部API
- ✅ **触摸优化** - 专为移动设备优化的UI界面
- ✅ **跨平台** - 支持Android和HarmonyOS 4.0+
- ✅ **保持原有逻辑** - 核心业务逻辑完全保持不变
- ✅ **现代化UI** - 使用KivyMD Material Design风格

## 🏗️ 项目结构

```
mobile_app/
├── main.py                    # 主程序入口
├── bagua_clock_mobile.kv      # Kivy界面定义文件
├── requirements_mobile.txt    # 移动端依赖
├── buildozer.spec             # Android构建配置
├── screens/                   # 界面模块
│   ├── bazi_screen.py         # 八字算命界面
│   ├── shensha_screen.py      # 神煞分析界面
│   └── ...
├── services/                  # 业务服务层
│   ├── bazi_service.py        # 八字计算服务
│   └── ...
└── harmonyos/                 # HarmonyOS适配
    ├── README_HarmonyOS.md    # HarmonyOS适配指南
    └── config.json            # HarmonyOS配置文件
```

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Android SDK (用于Android构建)
- DevEco Studio (用于HarmonyOS构建)

### 安装依赖

```bash
cd mobile_app
pip install -r requirements_mobile.txt
```

### 运行测试（Windows/Linux）

```bash
python main.py
```

### 构建Android APK

```bash
# 安装buildozer
pip install buildozer

# 初始化（首次运行）
buildozer init

# 构建APK
buildozer android debug

# 构建发布版APK
buildozer android release
```

### 构建HarmonyOS应用

参考 `harmonyos/README_HarmonyOS.md` 文件。

## 📦 功能模块

### 1. 八字算命
- 输入出生信息
- 计算四柱八字
- 显示详细分析

### 2. 神煞分析
- 传统神煞查询
- 组合分析

### 3. 财运分析
- 财星识别
- 大运财运

### 4. 婚姻分析
- 配偶星分析
- 婚姻质量评估

### 5. 职业分析
- 基于十神的职业建议

## 🔧 技术栈

- **UI框架**: KivyMD (Material Design)
- **业务逻辑**: 保持原有Python代码不变
- **构建工具**: Buildozer (Android)
- **HarmonyOS**: ArkUI + Python运行时

## 📱 平台支持

### Android
- ✅ 最低版本: Android 5.0 (API 21)
- ✅ 目标版本: Android 13 (API 33)
- ✅ 架构: arm64-v8a, armeabi-v7a

### HarmonyOS
- ✅ 最低版本: HarmonyOS 4.0
- ✅ 架构: arm64-v8a

## 🛠️ 开发指南

### 添加新界面

1. 在 `screens/` 目录创建新的屏幕类
2. 在 `bagua_clock_mobile.kv` 中定义UI
3. 在 `main.py` 中注册新屏幕

### 添加新服务

1. 在 `services/` 目录创建服务类
2. 保持与桌面版相同的业务逻辑接口
3. 在界面中调用服务

## 📝 注意事项

1. **保持兼容性**: 移动端代码保持与桌面版相同的业务逻辑接口
2. **性能优化**: 移动端需要注意性能，避免阻塞UI线程
3. **权限管理**: Android和HarmonyOS都需要声明必要的权限
4. **资源管理**: 注意图片、字体等资源的大小

## 🐛 问题排查

### Android构建失败

```bash
# 检查SDK路径
buildozer android debug 2>&1 | grep -i error

# 清理构建缓存
buildozer android clean
```

### HarmonyOS构建问题

参考 `harmonyos/README_HarmonyOS.md` 中的故障排除部分。

## 📄 许可证

与主项目保持一致。

## 👥 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题，请通过以下方式联系：
- 项目Issue
- 邮箱：[您的邮箱]

---

**版本**: 2.0.0  
**更新日期**: 2025-01-XX

