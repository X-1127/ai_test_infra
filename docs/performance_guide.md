# 性能测试使用指南

## 🚀 快速开始

### 1. 基础性能测试

```bash
# 基础测试：100次顺序请求，无延迟注入
python scripts/performance_test.py

# 基础测试：1000次请求
python scripts/performance_test.py --count 1000
```

### 2. 延迟注入测试

```bash
# 延迟注入测试：100-200ms延迟
python scripts/performance_test.py --scenario delay --delay-min 100 --delay-max 200

# 更大的延迟：500-800ms
python scripts/performance_test.py --scenario delay --delay-min 500 --delay-max 800
```

### 3. 故障注入测试

```bash
# 故障注入测试：30%故障率
python scripts/performance_test.py --scenario fault --fault-prob 0.3

# 高故障率：50%故障率
python scripts/performance_test.py --scenario fault --fault-prob 0.5
```

### 4. 组合测试

```bash
# 组合测试：延迟+故障
python scripts/performance_test.py --scenario combined --delay-min 100 --delay-max 200 --fault-prob 0.2

# 恶劣环境测试：高延迟+高故障率
python scripts/performance_test.py --scenario combined --delay-min 500 --delay-max 1000 --fault-prob 0.4
```

### 5. 并发测试

```bash
# 并发测试：10个并发，100次请求
python scripts/performance_test.py --concurrency 10 --count 100

# 高并发测试：50个并发，1000次请求
python scripts/performance_test.py --concurrency 50 --count 1000
```

## 📊 测试场景详解

### 场景1：基准性能测试

**目的**：建立无延迟注入时的性能基准

```bash
python scripts/performance_test.py --count 1000
```

**预期结果**（Windows系统）：
- 平均响应时间：<100ms
- 95分位响应时间：<200ms
- 99分位响应时间：<300ms
- 成功率：100%

**预期结果**（Linux/Mac系统）：
- 平均响应时间：<50ms
- 95分位响应时间：<100ms
- 99分位响应时间：<150ms
- 成功率：100%

### 场景2：延迟注入测试

**目的**：测试服务器在延迟环境下的表现

```bash
# 小延迟：50-100ms
python scripts/performance_test.py --scenario delay --delay-min 50 --delay-max 100

# 中等延迟：100-200ms
python scripts/performance_test.py --scenario delay --delay-min 100 --delay-max 200

# 大延迟：500-1000ms
python scripts/performance_test.py --scenario delay --delay-min 500 --delay-max 1000
```

**预期结果**（100-200ms延迟）：
- 平均响应时间：150-300ms
- 95分位响应时间：250-400ms
- 99分位响应时间：300-500ms
- 成功率：100%

### 场景3：故障注入测试

**目的**：测试服务器的错误处理能力

```bash
# 低故障率：10%
python scripts/performance_test.py --scenario fault --fault-prob 0.1

# 中等故障率：30%
python scripts/performance_test.py --scenario fault --fault-prob 0.3

# 高故障率：50%
python scripts/performance_test.py --scenario fault --fault-prob 0.5
```

**预期结果**（30%故障率）：
- 平均响应时间：<100ms
- 成功率：约70%
- 错误率：约30%

### 场景4：组合压力测试

**目的**：模拟真实复杂环境

```bash
# 正常网络环境
python scripts/performance_test.py --scenario combined --delay-min 50 --delay-max 100 --fault-prob 0.05

# 不稳定网络环境
python scripts/performance_test.py --scenario combined --delay-min 100 --delay-max 300 --fault-prob 0.15

# 恶劣网络环境
python scripts/performance_test.py --scenario combined --delay-min 500 --delay-max 1000 --fault-prob 0.3
```

### 场景5：并发测试

**目的**：测试服务器的并发处理能力

```bash
# 低并发：5个并发
python scripts/performance_test.py --concurrency 5 --count 100

# 中等并发：10个并发
python scripts/performance_test.py --concurrency 10 --count 200

# 高并发：50个并发
python scripts/performance_test.py --concurrency 50 --count 1000
```

### 场景6：流式响应测试

**目的**：测试流式响应的性能和稳定性

```bash
# 流式响应基准测试
python scripts/performance_test.py --stream --count 100

# 流式响应并发测试
python scripts/performance_test.py --stream --concurrency 10 --count 500

# 流式响应+延迟注入
python scripts/performance_test.py --stream --scenario delay --delay-min 100 --delay-max 200
```

### 场景7：日志系统性能测试

**目的**：测试日志记录对性能的影响

```bash
# 启用日志记录的基准测试
python scripts/performance_test.py --enable-logging --count 1000

# 日志记录+高并发
python scripts/performance_test.py --enable-logging --concurrency 20 --count 1000

# 日志查询性能测试
python scripts/performance_test.py --test-log-query --query-count 100
```

## 📈 结果分析

### 正常性能指标

**优秀性能**：
- 平均响应时间：<50ms
- 95分位响应时间：<100ms
- 99分位响应时间：<150ms
- 成功率：>99%

**良好性能**：
- 平均响应时间：50-100ms
- 95分位响应时间：100-200ms
- 99分位响应时间：150-300ms
- 成功率：>95%

**可接受性能**：
- 平均响应时间：100-200ms
- 95分位响应时间：200-400ms
- 99分位响应时间：300-500ms
- 成功率：>90%

### 性能问题诊断

**问题1：响应时间过长**
- 可能原因：系统负载高、网络延迟、代码性能问题
- 解决方案：检查系统资源、优化代码、减少并发数

**问题2：错误率过高**
- 可能原因：服务器配置错误、网络问题、代码bug
- 解决方案：检查服务器日志、修复代码bug、增加重试机制

**问题3：响应时间波动大**
- 可能原因：系统调度不稳定、资源竞争
- 解决方案：优化系统配置、增加资源、减少并发

## 🔧 压测策略

### 渐进式压测

```bash
# 阶段1：基准测试
python scripts/performance_test.py --count 100

# 阶段2：增加负载
python scripts/performance_test.py --count 500

# 阶段3：高负载
python scripts/performance_test.py --count 1000

# 阶段4：并发测试
python scripts/performance_test.py --concurrency 10 --count 500

# 阶段5：高并发
python scripts/performance_test.py --concurrency 50 --count 1000
```

### 场景化压测

```bash
# 场景1：正常使用
python scripts/performance_test.py --scenario delay --delay-min 50 --delay-max 100

# 场景2：网络波动
python scripts/performance_test.py --scenario combined --delay-min 100 --delay-max 500 --fault-prob 0.1

# 场景3：网络恶劣
python scripts/performance_test.py --scenario combined --delay-min 500 --delay-max 1000 --fault-prob 0.3
```

### 持续监控

```bash
# 持续监控脚本
while true; do
    echo "=== $(date) ==="
    python scripts/performance_test.py --count 100 --scenario delay --delay-min 100 --delay-max 200
    sleep 60
done
```

## 🎯 性能优化建议

### 1. 基于测试结果的优化

**如果平均响应时间>200ms**：
- 检查系统资源使用情况
- 优化数据库查询（如果使用）
- 减少不必要的计算
- 考虑使用缓存

**如果错误率>5%**：
- 检查服务器日志
- 增加错误处理和重试机制
- 优化网络配置
- 增加服务器资源

**如果响应时间波动大**：
- 优化系统调度
- 增加服务器资源
- 使用连接池
- 实现请求队列

### 2. 针对Windows系统的优化

**已知问题**：
- Windows系统时间精度较低
- asyncio.sleep()存在10-20%偏差
- 系统调度开销较大

**优化建议**：
- 放宽测试断言范围（已实施）
- 使用更高精度的计时器
- 优化协程调度
- 考虑使用Linux/Mac进行关键测试

## 📝 测试报告模板

```markdown
# LLM Mock Server 性能测试报告

## 测试环境
- 操作系统: Windows 10
- Python版本: 3.13.13
- 测试时间: 2026-04-20
- 测试工具: performance_test.py

## 测试场景

### 场景1：基准性能测试
- 测试次数: 1000
- 延迟注入: 无
- 故障注入: 无

**结果**:
- 平均响应时间: 85ms
- 95分位响应时间: 150ms
- 99分位响应时间: 220ms
- 成功率: 100%

### 场景2：延迟注入测试
- 测试次数: 1000
- 延迟注入: 100-200ms
- 故障注入: 无

**结果**:
- 平均响应时间: 250ms
- 95分位响应时间: 380ms
- 99分位响应时间: 480ms
- 成功率: 100%

### 场景3：并发测试
- 测试次数: 1000
- 并发数: 10
- 延迟注入: 100-200ms

**结果**:
- 平均响应时间: 280ms
- 95分位响应时间: 420ms
- 99分位响应时间: 550ms
- 成功率: 99.8%

## 结论
服务器在基准测试下表现良好，延迟注入功能正常工作。
在并发测试下，性能略有下降但仍在可接受范围内。
建议在Linux系统上进行进一步测试以获得更准确的结果。
```

## 🔍 故障排查

### 常见问题

**1. 连接被拒绝**
```
requests.exceptions.ConnectionError: [Errno 61] Connection refused
```
**解决**: 确保服务器正在运行：`python scripts/start_server.py`

**2. 请求超时**
```
requests.exceptions.Timeout: HTTPConnectionPool
```
**解决**: 增加超时时间或检查服务器负载

**3. 所有请求都失败**
```
success_rate: 0%
```
**解决**: 检查服务器配置和网络连接

## 📚 相关资源

- [性能分析文档](performance_analysis.md)
- [测试体系说明](test_system.md)
- [API文档](api.md)
- [部署指南](deployment.md)