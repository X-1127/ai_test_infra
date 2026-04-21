# LLM Mock Server 桌面应用

LLM Mock Server 的图形化管理界面，提供便捷的服务器管理、配置、日志查看和测试功能。

## 🚀 快速开始

### 安装依赖

```bash
# 安装桌面应用依赖
pip install -e .[desktop]
```

### 启动桌面应用

#### Windows
```bash
# 使用批处理文件
start_desktop.bat

# 或直接运行
python desktop/main.py
```

#### Linux/Mac
```bash
python desktop/main.py
```

## 📋 功能特性

### 1. 服务器管理
- ✅ 启动/停止/重启服务器
- ✅ 实时服务器状态监控
- ✅ 自定义端口配置
- ✅ 服务器输出实时显示
- 🚧 健康检查（开发中）

### 2. 配置管理（开发中）
- 🚧 延迟注入配置
- 🚧 故障注入配置
- 🚧 YAML配置管理
- 🚧 配置导入/导出

### 3. 日志查看（开发中）
- 🚧 实时日志显示
- 🚧 日志过滤（按类型）
- 🚧 日志搜索
- 🚧 日志导出

### 4. 测试界面（开发中）
- 🚧 聊天测试界面
- 🚧 流式响应测试
- 🚧 批量测试
- 🚧 性能测试

### 5. 性能监控（开发中）
- 🚧 实时性能指标
- 🚧 请求统计图表
- 🚧 响应时间图表
- 🚧 错误率统计

## 🎨 界面预览

### 主窗口
- 5个功能标签页：服务器、配置、日志、测试、监控
- 现代化的界面设计
- 状态栏实时显示服务器状态

### 服务器管理
- 一键启动/停止/重启服务器
- 实时显示服务器输出
- 自定义端口配置
- 服务器状态监控

## ⚙️ 配置文件

桌面应用配置保存在 `~/.llm-mock-server/desktop_config.json`

配置项：
```json
{
  "server_host": "localhost",
  "server_port": 8000,
  "auto_start_server": false,
  "minimize_to_tray": true,
  "show_notifications": true,
  "log_auto_refresh": true,
  "log_refresh_interval": 5,
  "theme": "default",
  "language": "zh_CN",
  "window_width": 1200,
  "window_height": 800
}
```

## 🔧 技术栈

- **GUI框架**: PyQt6
- **HTTP客户端**: httpx
- **异步处理**: asyncio + QThread
- **配置管理**: JSON

## 📂 项目结构

```
desktop/
├── __init__.py           # 包初始化
├── main.py              # 应用入口
├── config/              # 配置模块
│   ├── __init__.py
│   └── settings.py      # 配置管理
├── ui/                  # 用户界面
│   ├── __init__.py
│   ├── main_window.py   # 主窗口
│   ├── server_tab.py    # 服务器管理
│   ├── config_tab.py    # 配置管理
│   ├── logs_tab.py      # 日志查看
│   ├── test_tab.py      # 测试界面
│   └── monitor_tab.py   # 性能监控
└── services/            # 服务模块
    ├── __init__.py
    ├── api_client.py    # API客户端
    └── server_manager.py # 服务器管理
```

## 🐛 故障排查

### 应用无法启动
1. 检查Python版本（需要3.13+）
2. 确认PyQt6已安装：`pip install PyQt6`
3. 检查是否有权限问题

### 服务器无法启动
1. 检查端口是否被占用
2. 确认后端服务脚本存在
3. 查看服务器输出了解错误信息

### 界面显示异常
1. 尝试重启应用
2. 删除配置文件：`rm ~/.llm-mock-server/desktop_config.json`
3. 检查系统主题兼容性

## 📝 开发计划

### 阶段1：基础框架 ✅
- [x] 创建桌面应用目录结构
- [x] 设置PyQt6环境
- [x] 实现主窗口框架
- [x] 创建标签页布局
- [x] 实现基础样式

### 阶段2：服务器管理 ✅
- [x] 实现服务器启动/停止功能
- [x] 服务器状态监控
- [x] 端口配置界面
- [ ] 健康检查显示

### 阶段3：配置管理（进行中）
- [ ] 延迟注入配置界面
- [ ] 故障注入配置界面
- [ ] YAML配置管理界面
- [ ] 配置导入/导出功能

### 阶段4：日志查看（待开始）
- [ ] 实时日志显示
- [ ] 日志过滤功能
- [ ] 日志搜索功能
- [ ] 日志导出功能

### 阶段5：测试界面（待开始）
- [ ] 聊天测试界面
- [ ] 流式响应测试
- [ ] 批量测试功能
- [ ] 性能测试界面

### 阶段6：性能监控（待开始）
- [ ] 实时性能指标显示
- [ ] 请求统计图表
- [ ] 响应时间图表
- [ ] 错误率统计

### 阶段7：优化和测试（待开始）
- [ ] 性能优化
- [ ] 错误处理
- [ ] 用户体验优化
- [ ] 完整测试

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

本项目采用 MIT 许可证

## 📞 联系方式

- 作者: XY
- 项目: [LLM Mock Server](https://github.com/yourusername/llm-mock-server)