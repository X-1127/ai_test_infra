#!/usr/bin/env python3
"""
LLM Mock Server 性能测试脚本
用于测试服务器在不同负载下的性能表现
"""

import time
import statistics
import requests
import argparse
from typing import Dict, List, Tuple
import concurrent.futures


class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    def single_request(self, messages: List[Dict]) -> Tuple[int, float, str]:
        """
        执行单个请求
        
        返回: (状态码, 响应时间ms, 错误信息)
        """
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={"messages": messages},
                timeout=30
            )
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            return response.status_code, response_time_ms, ""
            
        except requests.exceptions.Timeout:
            return 0, 30000, "Timeout"
        except Exception as e:
            return 0, 0, str(e)
    
    def configure_injection(self, delay_enabled: bool = False, 
                         fault_enabled: bool = False,
                         delay_min: int = 100, 
                         delay_max: int = 200,
                         fault_probability: float = 0.0):
        """配置延迟和故障注入"""
        config = {
            "delay": {
                "enabled": delay_enabled,
                "min_delay_ms": delay_min,
                "max_delay_ms": delay_max
            },
            "fault": {
                "enabled": fault_enabled,
                "fault_type": "http_error",
                "http_status_code": 500,
                "error_message": "Internal server error",
                "probability": fault_probability
            }
        }
        
        response = requests.put(
            f"{self.base_url}/v1/config/injection",
            json=config
        )
        
        if response.status_code != 200:
            print(f"配置注入失败: {response.status_code}")
            return False
        
        return True
    
    def reset_injection(self):
        """重置注入配置"""
        response = requests.post(f"{self.base_url}/v1/config/injection/reset")
        return response.status_code == 200
    
    def run_sequential_test(self, count: int = 100, 
                          messages: List[Dict] = None) -> Dict:
        """
        顺序测试
        
        Args:
            count: 测试次数
            messages: 请求消息
        
        Returns:
            测试结果字典
        """
        if messages is None:
            messages = [{"role": "user", "content": "test"}]
        
        print(f"开始顺序测试: {count} 次请求")
        
        success_times = []
        errors = []
        
        for i in range(count):
            status_code, response_time, error = self.single_request(messages)
            
            if status_code == 200:
                success_times.append(response_time)
            else:
                errors.append({
                    "index": i,
                    "status_code": status_code,
                    "error": error,
                    "time": response_time
                })
            
            if (i + 1) % 10 == 0:
                print(f"进度: {i + 1}/{count}")
        
        return self._calculate_stats(success_times, errors, count)
    
    def run_concurrent_test(self, count: int = 100, 
                         concurrency: int = 10,
                         messages: List[Dict] = None) -> Dict:
        """
        并发测试
        
        Args:
            count: 总测试次数
            concurrency: 并发数
            messages: 请求消息
        
        Returns:
            测试结果字典
        """
        if messages is None:
            messages = [{"role": "user", "content": "test"}]
        
        print(f"开始并发测试: {count} 次请求, 并发数: {concurrency}")
        
        success_times = []
        errors = []
        
        def worker():
            status_code, response_time, error = self.single_request(messages)
            return status_code, response_time, error
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker) for _ in range(count)]
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                status_code, response_time, error = future.result()
                
                if status_code == 200:
                    success_times.append(response_time)
                else:
                    errors.append({
                        "index": i,
                        "status_code": status_code,
                        "error": error,
                        "time": response_time
                    })
                
                if (i + 1) % 10 == 0:
                    print(f"进度: {i + 1}/{count}")
        
        return self._calculate_stats(success_times, errors, count)
    
    def _calculate_stats(self, success_times: List[float], 
                        errors: List[Dict], total_count: int) -> Dict:
        """计算统计数据"""
        success_count = len(success_times)
        error_count = len(errors)
        
        if success_count > 0:
            stats = {
                "total_requests": total_count,
                "success_count": success_count,
                "error_count": error_count,
                "success_rate": (success_count / total_count) * 100,
                "error_rate": (error_count / total_count) * 100,
                "avg_ms": statistics.mean(success_times),
                "median_ms": statistics.median(success_times),
                "min_ms": min(success_times),
                "max_ms": max(success_times),
                "std_dev_ms": statistics.stdev(success_times) if len(success_times) > 1 else 0,
            }
            
            # 计算百分位数
            if len(success_times) >= 20:
                sorted_times = sorted(success_times)
                stats["p50_ms"] = sorted_times[int(len(sorted_times) * 0.5)]
                stats["p90_ms"] = sorted_times[int(len(sorted_times) * 0.9)]
                stats["p95_ms"] = sorted_times[int(len(sorted_times) * 0.95)]
                stats["p99_ms"] = sorted_times[int(len(sorted_times) * 0.99)]
            
            return stats
        else:
            return {
                "total_requests": total_count,
                "success_count": 0,
                "error_count": error_count,
                "success_rate": 0,
                "error_rate": 100,
                "error": "所有请求都失败了"
            }
    
    def print_stats(self, stats: Dict, test_name: str = "测试"):
        """打印统计结果"""
        print(f"\n{'='*60}")
        print(f"{test_name} 结果")
        print(f"{'='*60}")
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求数: {stats['success_count']}")
        print(f"失败请求数: {stats['error_count']}")
        print(f"成功率: {stats['success_rate']:.2f}%")
        print(f"错误率: {stats['error_rate']:.2f}%")
        
        if stats['success_count'] > 0:
            print(f"\n响应时间统计:")
            print(f"  平均: {stats['avg_ms']:.2f}ms")
            print(f"  中位数: {stats['median_ms']:.2f}ms")
            print(f"  最小: {stats['min_ms']:.2f}ms")
            print(f"  最大: {stats['max_ms']:.2f}ms")
            print(f"  标准差: {stats['std_dev_ms']:.2f}ms")
            
            if 'p50_ms' in stats:
                print(f"\n百分位数:")
                print(f"  P50: {stats['p50_ms']:.2f}ms")
                print(f"  P90: {stats['p90_ms']:.2f}ms")
                print(f"  P95: {stats['p95_ms']:.2f}ms")
                print(f"  P99: {stats['p99_ms']:.2f}ms")
        
        if stats['error_count'] > 0:
            print(f"\n错误详情:")
            for error in stats.get('errors', [])[:5]:  # 只显示前5个错误
                print(f"  请求 {error['index']}: {error['error']}")
            if stats['error_count'] > 5:
                print(f"  ... 还有 {stats['error_count'] - 5} 个错误")
        
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='LLM Mock Server 性能测试')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='服务器URL')
    parser.add_argument('--count', type=int, default=100,
                       help='测试次数')
    parser.add_argument('--concurrency', type=int, default=1,
                       help='并发数 (默认1，表示顺序测试)')
    parser.add_argument('--delay', action='store_true',
                       help='启用延迟注入')
    parser.add_argument('--delay-min', type=int, default=100,
                       help='最小延迟ms')
    parser.add_argument('--delay-max', type=int, default=200,
                       help='最大延迟ms')
    parser.add_argument('--fault', action='store_true',
                       help='启用故障注入')
    parser.add_argument('--fault-prob', type=float, default=0.0,
                       help='故障概率 (0.0-1.0)')
    parser.add_argument('--scenario', choices=['basic', 'delay', 'fault', 'combined'],
                       default='basic', help='测试场景')
    
    args = parser.parse_args()
    
    tester = PerformanceTester(args.url)
    
    # 根据场景配置
    if args.scenario == 'basic':
        print("场景: 基础性能测试 (无延迟，无故障)")
        tester.reset_injection()
    elif args.scenario == 'delay':
        print(f"场景: 延迟注入测试 ({args.delay_min}-{args.delay_max}ms)")
        tester.configure_injection(delay_enabled=True, 
                              delay_min=args.delay_min, 
                              delay_max=args.delay_max)
    elif args.scenario == 'fault':
        print(f"场景: 故障注入测试 (故障率: {args.fault_prob*100:.0f}%)")
        tester.configure_injection(fault_enabled=True, 
                              fault_probability=args.fault_prob)
    elif args.scenario == 'combined':
        print(f"场景: 组合测试 (延迟: {args.delay_min}-{args.delay_max}ms, 故障率: {args.fault_prob*100:.0f}%)")
        tester.configure_injection(delay_enabled=True, 
                              fault_enabled=True,
                              delay_min=args.delay_min, 
                              delay_max=args.delay_max,
                              fault_probability=args.fault_prob)
    
    # 执行测试
    if args.concurrency > 1:
        stats = tester.run_concurrent_test(args.count, args.concurrency)
        tester.print_stats(stats, f"并发测试 (并发数: {args.concurrency})")
    else:
        stats = tester.run_sequential_test(args.count)
        tester.print_stats(stats, "顺序测试")
    
    # 清理
    tester.reset_injection()
    print("测试完成，配置已重置")


if __name__ == "__main__":
    main()