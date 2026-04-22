# LLM Mock Server Desktop Application

LLM Mock Server 桌面应用 - 用于管理和测试 LLM Mock Server 的图形化界面。

## 功能特性

- ✅ 服务器管理（启动/停止/重启/状态监控）
- ✅ 配置管理（延迟/故障/YAML配置）
- ✅ 日志查看（实时显示/过滤/搜索/导出）
- ✅ 测试界面（聊天/流式/批量/性能测试）
- ✅ 性能监控（实时指标/统计/错误显示）
- ✅ 图形化界面，易于使用

## 快速开始

### 环境要求

- Python 3.13+
- pip
- LLM Mock Server 后端服务运行中

### 安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[build]"
```

### 启动应用

```bash
# 使用 Python 直接启动
python main.py

# 或使用安装的命令
llm-mock-desktop
```

### 打包成可执行文件

```bash
# Windows
python scripts/build.bat

# Linux/Mac
python scripts/build.sh
```

打包完成后，可执行文件位于：
- Windows: `dist/LLM_Mock_Desktop.exe`
- Linux/Mac: `dist/LLM_Mock_Desktop`

## 使用说明

### 服务器管理

1. 在"服务器管理"标签页中
2. 点击"启动服务器"按钮
3. 服务器启动后，状态会显示为"运行中"
4. 可以自定义服务器端口
5. 查看服务器输出和健康检查结果

### 配置管理

#### 延迟注入

1. 切换到"配置管理"标签页
2. 在"延迟注入"部分
3. 启用延迟注入
4. 设置最小和最大延迟时间
5. 点击"应用配置"

#### 故障注入

1. 切换到"配置管理"标签页
2. 在"故障注入"部分
3. 启用故障注入
4. 选择故障类型
5. 设置故障概率
6. 点击"应用配置"

#### YAML 配置

1. 切换到"配置管理"标签页
2. 在"YAML 配置"部分
3. 点击"添加规则"按钮
4. 填写触发词、响应内容等
5. 保存规则

### 日志查看

1. 切换到"日志查看"标签页
2. 选择日志类型（请求/错误/访问）
3. 使用搜索框过滤日志
4. 点击"导出日志"保存日志文件

### 测试界面

#### 聊天测试

1. 切换到"测试界面"标签页
2. 在"聊天测试"部分
3. 输入消息内容
4. 点击"发送"按钮
5. 查看响应结果

#### 流式响应测试

1. 切换到"测试界面"标签页
2. 在"流式响应测试"部分
3. 输入消息内容
4. 点击"发送"按钮
5. 查看流式响应

#### 批量测试

1. 切换到"测试界面"标签页
2. 在"批量测试"部分
3. 设置测试次数和并发数
4. 点击"开始测试"
5. 查看测试结果

### 性能监控

1. 切换到"性能监控"标签页
2. 查看实时指标
3. 查看统计信息
4. 查看错误信息

## 项目结构

```
desktop-app/
├── app/                    # 应用代码
│   ├── config/            # 配置管理
│   ├── services/          # 业务服务
│   └── ui/               # 用户界面
├── scripts/               # 工具脚本
│   ├── build.bat         # Windows 打包脚本
│   └── build.sh         # Linux/Mac 打包脚本
├── tests/                 # 测试代码（可选）
├── main.py               # 应用入口
├── build.spec            # PyInstaller 配置
└── pyproject.toml        # 项目配置
```

## 开发

### 代码风格

```bash
# 格式化代码
black app/ tests/

# 检查代码风格
flake8 app/ tests/

# 类型检查
mypy app/
```

### 添加新功能

1. 在 `app/ui/` 中添加新的界面组件
2. 在 `app/services/` 中添加业务逻辑
3. 在 `app/config/` 中添加配置
4. 更新文档

## 配置

### 应用配置

应用配置位于 `app/config/settings.py`：

```python
# 服务器配置
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000

# 界面配置
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
```

### 日志配置

日志文件位于应用目录下的 `logs/` 文件夹。

## 故障排查

### 无法连接到服务器

1. 检查服务器是否启动
2. 检查服务器地址和端口是否正确
3. 检查防火墙设置

### 打包失败

1. 确保已安装 PyInstaller
2. 检查依赖是否完整
3. 查看打包日志中的错误信息

### 应用启动失败

1. 检查 Python 版本是否满足要求
2. 检查依赖是否正确安装
3. 查看错误日志

## 许可证

MIT License