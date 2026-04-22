# LLM Mock Server 后端压测指南

本文档介绍如何使用 Locust 对 LLM Mock Server 后端进行性能压测，包含4种压测场景：基准测试、负载测试、稳定性测试、压力测试。

## 目录

- [安装依赖](#安装依赖)
- [启动服务器](#启动服务器)
- [压测场景](#压测场景)
- [查看报告](#查看报告)
- [性能指标](#性能指标)
- [故障排查](#故障排查)

## 安装依赖

### 方法1: 使用项目依赖

```bash
cd backend
pip install -e ".[loadtest]"
```

### 方法2: 手动安装

```bash
pip install locust httpx
```

## 启动服务器

在进行压测之前，需要先启动 LLM Mock Server。

### 方法1: 使用 Python 直接启动

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 方法2: 使用启动脚本

```bash
cd backend
python scripts/start_server.py
```

### 方法3: 使用 Docker

```bash
cd backend
docker-compose up -d
```

## 压测场景

### 场景1: 基准测试 (Baseline Test)

**目的**：在低并发下运行一段时间，获取系统性能的基线数据，作为后续测试的参考标准。

**特点**：
- 低并发，低压力
- 获取系统在正常情况下的性能表现
- 作为后续测试的参考标准

**运行方式**：

```bash
cd backend

# 方法1: 使用压测脚本（推荐）
python scripts/run_loadtest.py --scenario baseline

# 方法2: 使用 Locust 命令
locust -f tests/loadtest/locustfile.py \
  --host http://localhost:8000 \
  --users 10 \
  --spawn-rate 2 \
  --run-time 120 \
  --headless \
  --html loadtest_reports/baseline_test.html \
  --csv loadtest_reports/baseline_test
```

**参数说明**：
- `--users 10`: 10个并发用户
- `--spawn-rate 2`: 每秒启动2个用户
- `--run-time 120`: 运行120秒（2分钟）
- `--headless`: 无头模式，不启动Web UI
- `--html`: 生成HTML报告
- `--csv`: 生成CSV统计文件

**预期结果**：
- 获取系统的基线性能数据
- 平均响应时间、P95、P99等指标
- 成功率应该接近100%

### 场景2: 负载测试 (Load Test)

**目的**：逐步增加并发用户数，观察响应时间和吞吐量的变化趋势，找到系统性能开始急剧下降的"拐点"。

**特点**：
- 逐步增加负载
- 观察性能变化趋势
- 找到性能拐点

**运行方式**：

```bash
cd backend

# 使用压测脚本（推荐）
python scripts/run_loadtest.py --scenario load
```

**测试流程**：
脚本会自动运行5个负载级别：

| 级别 | 用户数 | 生成速率 | 运行时间 |
|------|--------|----------|----------|
| 1 | 10 | 2/s | 120s |
| 2 | 25 | 5/s | 120s |
| 3 | 50 | 10/s | 120s |
| 4 | 75 | 15/s | 120s |
| 5 | 100 | 20/s | 120s |

每个级别之间有30秒的恢复时间。

**预期结果**：
- 找到性能拐点（响应时间急剧增加的负载级别）
- 观察吞吐量随负载的变化
- 确定系统的最佳负载范围

### 场景3: 稳定性测试 (Stability Test)

**目的**：在一定负载下（如目标QPS的80%），长时间运行（如1-2小时），监控响应时间标准差和错误率，检验系统是否存在内存泄漏等问题。

**特点**：
- 中等负载，长时间运行
- 监控系统稳定性
- 检测内存泄漏等问题

**运行方式**：

```bash
cd backend

# 方法1: 使用压测脚本（推荐）
python scripts/run_loadtest.py --scenario stability

# 方法2: 使用 Locust 命令（自定义时间）
locust -f tests/loadtest/locustfile.py \
  --host http://localhost:8000 \
  --users 50 \
  --spawn-rate 10 \
  --run-time 3600 \
  --headless \
  --html loadtest_reports/stability_test.html \
  --csv loadtest_reports/stability_test
```

**参数说明**：
- `--users 50`: 50个并发用户（目标QPS的80%）
- `--spawn-rate 10`: 每秒启动10个用户
- `--run-time 3600`: 运行3600秒（1小时，可根据需要调整为7200秒=2小时）

**预期结果**：
- 响应时间保持稳定，标准差较小
- 错误率保持在低水平（<1%）
- 内存使用稳定，没有内存泄漏
- CPU使用率稳定

### 场景4: 压力测试 (Stress Test)

**目的**：持续增加负载，直至系统达到极限并开始出现错误，目的是找出系统的最大承载能力和瓶颈点。

**特点**：
- 持续增加负载
- 找到系统极限
- 识别性能瓶颈

**运行方式**：

```bash
cd backend

# 使用压测脚本（推荐）
python scripts/run_loadtest.py --scenario stress
```

**测试流程**：
脚本会自动运行6个压力级别，直到系统达到极限：

| 级别 | 用户数 | 生成速率 | 运行时间 |
|------|--------|----------|----------|
| 1 | 50 | 10/s | 120s |
| 2 | 100 | 20/s | 120s |
| 3 | 150 | 30/s | 120s |
| 4 | 200 | 40/s | 120s |
| 5 | 250 | 50/s | 120s |
| 6 | 300 | 60/s | 120s |

如果某个级别测试失败，脚本会停止并报告系统极限。

**预期结果**：
- 找到系统的最大承载能力
- 识别性能瓶颈（CPU、内存、网络等）
- 确定系统崩溃点

### 运行所有场景

按顺序运行所有4种压测场景：

```bash
cd backend
python scripts/run_loadtest.py --scenario all
```

测试流程：
1. 基准测试 - 获取基线数据
2. 负载测试 - 逐步加压，找到拐点
3. 稳定性测试 - 长时间运行，检验稳定性
4. 压力测试 - 找出系统极限

### Web UI 模式

使用交互式Web UI进行压测：

```bash
cd backend
locust -f tests/loadtest/locustfile.py --host http://localhost:8000
```

访问 http://localhost:8089 查看压测界面，可以实时调整参数和查看结果。

## 查看报告

压测完成后，报告会保存在 `backend/loadtest_reports/` 目录：

```
backend/loadtest_reports/
├── baseline_test_20260422_143022.html
├── baseline_test_20260422_143022_stats.csv
├── baseline_test_20260422_143022_stats_history.csv
├── baseline_test_20260422_143022_stats_failures.csv
├── load_test_level1_20260422_143245.html
├── load_test_level2_20260422_143610.html
├── stability_test_20260422_144010.html
├── stress_test_level1_20260422_144250.html
└── ...
```

### HTML 报告

使用浏览器打开 HTML 文件查看详细报告，包含：

- **概览页面**：
  - 总请求数
  - 失败请求数
  - 中位数响应时间
  - 平均响应时间
  - 最小/最大响应时间
  - RPS（每秒请求数）

- **请求统计**：
  - 请求类型和名称
  - 请求数量
  - 失败数量
  - 响应时间统计
  - 失败率

- **图表**：
  - 响应时间分布图
  - RPS 趋势图
  - 用户数变化图

### CSV 统计

CSV 文件包含详细的原始数据，便于进一步分析：

- `*_stats.csv`: 汇总统计数据
- `*_stats_history.csv`: 历统计数据
- `*_stats_failures.csv`: 失败请求数据

## 性能指标

### 关键指标

| 指标 | 说明 | 目标值 | 基准值 |
|------|------|--------|----------|
| **RPS** | 每秒请求数 | > 100 | 基准测试获取 |
| **平均响应时间** | 平均响应时间 | < 100ms | 基准测试获取 |
| **P50** | 50% 请求的响应时间 | < 80ms | 基准测试获取 |
| **P95** | 95% 请求的响应时间 | < 200ms | 基准测试获取 |
| **P99** | 99% 请求的响应时间 | < 500ms | 基准测试获取 |
| **成功率** | 成功请求占比 | > 99% | 100% |
| **错误率** | 失败请求占比 | < 1% | 0% |

### 基准测试指标

基准测试应该获取以下数据：

- **响应时间基线**：
  - 平均响应时间
  - P50、P95、P99 响应时间
  - 响应时间标准差

- **吞吐量基线**：
  - 平均 RPS
  - 最大 RPS
  - RPS 标准差

- **资源使用基线**：
  - CPU 使用率
  - 内存使用量
  - 网络带宽

### 负载测试指标

负载测试应该观察以下变化：

- **响应时间趋势**：
  - 响应时间随负载增加的变化
  - 识别性能拐点
  - 确定最佳负载范围

- **吞吐量趋势**：
  - RPS 随负载增加的变化
  - 识别吞吐量拐点
  - 确定最大吞吐量

### 稳定性测试指标

稳定性测试应该监控以下指标：

- **响应时间稳定性**：
  - 响应时间标准差
  - 响应时间波动范围
  - 是否有响应时间激增

- **错误率稳定性**：
  - 错误率是否稳定
  - 是否有错误率激增
  - 错误类型分布

- **资源使用稳定性**：
  - 内存使用是否稳定（检测内存泄漏）
  - CPU 使用是否稳定
  - 是否有资源泄漏

### 压力测试指标

压力测试应该确定以下极限：

- **最大承载能力**：
  - 最大并发用户数
  - 最大 RPS
  - 系统崩溃点

- **性能瓶颈**：
  - CPU 瓶颈
  - 内存瓶颈
  - 网络瓶颈
  - I/O 瓶颈

## 故障排查

### 问题1: 连接被拒绝

**错误信息**：
```
Connection refused: [Errno 61] Connection refused
```

**解决方案**：
1. 确认服务器是否启动
2. 检查服务器地址和端口是否正确
3. 检查防火墙设置

### 问题2: 超时错误

**错误信息**：
```
HTTPConnectionPool: Read timeout
```

**解决方案**：
1. 增加超时时间
2. 检查服务器性能
3. 减少并发用户数

### 问题3: 内存不足

**错误信息**：
```
MemoryError: Unable to allocate memory
```

**解决方案**：
1. 减少并发用户数
2. 增加系统内存
3. 优化内存使用

### 问题4: Locust 安装失败

**错误信息**：
```
ERROR: Could not find a version that satisfies the requirement locust
```

**解决方案**：
```bash
pip install --upgrade pip
pip install locust httpx
```

## 最佳实践

1. **逐步加压**：从基准测试开始，逐步增加负载
2. **监控资源**：监控 CPU、内存、磁盘使用情况
3. **记录基线**：记录正常情况下的性能基线
4. **定期压测**：定期进行压测以发现性能退化
5. **分析瓶颈**：根据压测结果分析性能瓶颈
6. **持续优化**：持续优化系统性能

## 压测计划建议

### 开发阶段

- **频率**：每周一次
- **场景**：基准测试 + 负载测试
- **目的**：发现性能退化

### 测试阶段

- **频率**：每个版本发布前
- **场景**：所有4种场景
- **目的**：确保性能达标

### 生产环境

- **频率**：每月一次
- **场景**：基准测试 + 稳定性测试
- **目的**：监控生产环境性能

## 相关文档

- [Locust 官方文档](https://docs.locust.io/)
- [后端服务器文档](../README.md)
- [部署指南](../docs/deployment.md)
- [API文档](../docs/api.md)

## 支持

如有问题，请提交 Issue 或联系项目维护者。