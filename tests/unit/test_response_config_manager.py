import os
import shutil
from pathlib import Path

# 必须在导入app之前设置环境变量
os.environ['TESTING'] = '1'

import pytest
from app.services.response_config_manager import ResponseConfigManager, ResponseRule


@pytest.fixture(autouse=True)
def reset_test_config():
    """每个测试前自动重置测试配置"""
    # 从模板恢复测试配置
    test_config_path = Path("config/test_responses.yaml")
    template_path = Path("config/test_responses.yaml.template")
    
    if template_path.exists():
        shutil.copy(template_path, test_config_path)
    
    yield


class TestResponseConfigManager:
    def test_init_default_config(self):
        manager = ResponseConfigManager()
        assert manager.config.default_response == "这是一个测试响应。"
        assert len(manager.config.rules) == 5
    
    def test_load_config_from_file(self):
        manager = ResponseConfigManager()
        assert manager.config is not None
        assert manager.config.default_response is not None
    
    def test_empty_input(self):
        manager = ResponseConfigManager()
        result = manager.get_response("")
        assert result == manager.config.default_response
    
    def test_whitespace_input(self):
        manager = ResponseConfigManager()
        result = manager.get_response("   ")
        assert result == manager.config.default_response
    
    def test_empty_rules_list(self):
        manager = ResponseConfigManager()
        manager.config.rules = []
        result = manager.get_response("测试")
        assert result == manager.config.default_response
    
    def test_exact_match(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="你好", response="你好！", match_type="exact", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("你好")
        assert result == "你好！"
    
    def test_exact_match_with_whitespace(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="你好", response="你好！", match_type="exact", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response(" 你好 ")
        assert result == "你好！"
    
    def test_exact_match_not_found(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="你好", response="你好！", match_type="exact", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("你好吗")
        assert result == manager.config.default_response
    
    def test_contains_match(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="天气", response="天气不错", match_type="contains", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("今天天气怎么样")
        assert result == "天气不错"
    
    def test_contains_match_not_found(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="天气", response="天气不错", match_type="contains", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("今天怎么样")
        assert result == manager.config.default_response
    
    def test_regex_match(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger=r"\d+", response="检测到数字", match_type="regex", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("我有123个苹果")
        assert result == "检测到数字"
    
    def test_regex_match_not_found(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger=r"\d+", response="检测到数字", match_type="regex", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("我有苹果")
        assert result == manager.config.default_response
    
    def test_regex_compilation_error(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="[invalid(", response="错误", match_type="regex", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("测试")
        assert result == manager.config.default_response
    
    def test_disabled_rule(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="你好", response="你好！", match_type="exact", enabled=False)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("你好")
        assert result == manager.config.default_response
    
    def test_rule_priority(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="你好", response="第一个规则", match_type="exact", enabled=True),
            ResponseRule(trigger="你好", response="第二个规则", match_type="exact", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("你好")
        assert result == "第一个规则"
    
    def test_match_priority_order(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="测试", response="包含匹配", match_type="contains", enabled=True),
            ResponseRule(trigger="测试", response="精确匹配", match_type="exact", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("测试")
        assert result == "精确匹配"
    
    def test_special_characters(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="测试@#$%", response="特殊字符", match_type="exact", enabled=True)
        ]
        manager._build_rule_index()
        
        result = manager.get_response("测试@#$%")
        assert result == "特殊字符"
    
    def test_add_rule(self):
        manager = ResponseConfigManager()
        initial_count = len(manager.config.rules)
        
        new_rule = ResponseRule(trigger="测试", response="测试响应", match_type="exact", enabled=True)
        manager.add_rule(new_rule)
        
        assert len(manager.config.rules) == initial_count + 1
    
    def test_remove_rule(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="规则1", response="响应1", match_type="exact", enabled=True),
            ResponseRule(trigger="规则2", response="响应2", match_type="exact", enabled=True)
        ]
        
        success = manager.remove_rule(0)
        assert success is True
        assert len(manager.config.rules) == 1
        assert manager.config.rules[0].trigger == "规则2"
    
    def test_remove_invalid_index(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="规则1", response="响应1", match_type="exact", enabled=True)
        ]
        
        success = manager.remove_rule(10)
        assert success is False
        assert len(manager.config.rules) == 1
    
    def test_update_rule(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="规则1", response="响应1", match_type="exact", enabled=True)
        ]
        
        updated_rule = ResponseRule(trigger="新规则1", response="新响应1", match_type="exact", enabled=True)
        success = manager.update_rule(0, updated_rule)
        
        assert success is True
        assert manager.config.rules[0].trigger == "新规则1"
        assert manager.config.rules[0].response == "新响应1"
    
    def test_update_invalid_index(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="规则1", response="响应1", match_type="exact", enabled=True)
        ]
        
        updated_rule = ResponseRule(trigger="新规则1", response="新响应1", match_type="exact", enabled=True)
        success = manager.update_rule(10, updated_rule)
        
        assert success is False
        assert manager.config.rules[0].trigger == "规则1"
    
    def test_enable_rule(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="规则1", response="响应1", match_type="exact", enabled=False)
        ]
        
        success = manager.enable_rule(0, True)
        assert success is True
        assert manager.config.rules[0].enabled is True
    
    def test_disable_rule(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="规则1", response="响应1", match_type="exact", enabled=True)
        ]
        
        success = manager.enable_rule(0, False)
        assert success is True
        assert manager.config.rules[0].enabled is False
    
    def test_enable_invalid_index(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="规则1", response="响应1", match_type="exact", enabled=True)
        ]
        
        success = manager.enable_rule(10, False)
        assert success is False
        assert manager.config.rules[0].enabled is True
    
    def test_reload_config(self):
        manager = ResponseConfigManager()
        initial_rules_count = len(manager.config.rules)
        
        manager.reload_config()
        
        assert manager.config is not None
        assert len(manager.config.rules) == initial_rules_count
    
    def test_get_config(self):
        manager = ResponseConfigManager()
        config = manager.get_config()
        
        assert config is not None
        assert config.default_response is not None
        assert config.rules is not None
        assert config.metadata is not None
    
    def test_search_rules_by_keyword(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="你好", response="你好！有什么可以帮助你的吗？", match_type="exact", enabled=True),
            ResponseRule(trigger="天气", response="今天天气不错", match_type="contains", enabled=True),
            ResponseRule(trigger="测试", response="测试响应", match_type="exact", enabled=True)
        ]
        
        results = manager.search_rules("你好")
        assert len(results) == 1
        assert results[0]["index"] == 0
        assert results[0]["rule"]["trigger"] == "你好"
    
    def test_search_rules_by_keyword_case_insensitive(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="HELLO", response="你好", match_type="exact", enabled=True)
        ]
        
        results = manager.search_rules("hello")
        assert len(results) == 1
    
    def test_search_rules_by_match_type(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="你好", response="你好！", match_type="exact", enabled=True),
            ResponseRule(trigger="天气", response="天气不错", match_type="contains", enabled=True),
            ResponseRule(trigger="测试", response="测试响应", match_type="exact", enabled=True)
        ]
        
        results = manager.search_rules("", match_type="exact")
        assert len(results) == 2
    
    def test_search_rules_no_results(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="你好", response="你好！", match_type="exact", enabled=True)
        ]
        
        results = manager.search_rules("不存在的关键词")
        assert len(results) == 0
    
    def test_validate_rule_valid(self):
        manager = ResponseConfigManager()
        rule = ResponseRule(trigger="测试", response="测试响应", match_type="exact", enabled=True)
        
        is_valid, message = manager.validate_rule(rule)
        assert is_valid is True
        assert message is None
    
    def test_validate_rule_empty_trigger(self):
        manager = ResponseConfigManager()
        rule = ResponseRule(trigger="", response="测试响应", match_type="exact", enabled=True)
        
        is_valid, message = manager.validate_rule(rule)
        assert is_valid is False
        assert "触发词不能为空" in message
    
    def test_validate_rule_empty_response(self):
        manager = ResponseConfigManager()
        rule = ResponseRule(trigger="测试", response="", match_type="exact", enabled=True)
        
        is_valid, message = manager.validate_rule(rule)
        assert is_valid is False
        assert "响应不能为空" in message
    
    def test_validate_rule_invalid_regex(self):
        manager = ResponseConfigManager()
        rule = ResponseRule(trigger="[invalid(", response="测试响应", match_type="regex", enabled=True)
        
        is_valid, message = manager.validate_rule(rule)
        assert is_valid is False
        assert "正则表达式错误" in message
    
    def test_validate_rule_whitespace_trigger(self):
        manager = ResponseConfigManager()
        rule = ResponseRule(trigger="   ", response="测试响应", match_type="exact", enabled=True)
        
        is_valid, message = manager.validate_rule(rule)
        assert is_valid is False
        assert "触发词不能为空" in message
    
    def test_regex_cache_performance(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger=r"\d+", response="数字", match_type="regex", enabled=True)
        ]
        
        pattern = r"\d+"
        compiled1 = manager._get_compiled_regex(pattern)
        compiled2 = manager._get_compiled_regex(pattern)
        
        assert compiled1 is compiled2
    
    def test_rule_index_building(self):
        manager = ResponseConfigManager()
        manager.config.rules = [
            ResponseRule(trigger="规则1", response="响应1", match_type="exact", enabled=True),
            ResponseRule(trigger="规则2", response="响应2", match_type="contains", enabled=True),
            ResponseRule(trigger="规则3", response="响应3", match_type="regex", enabled=False)
        ]
        
        manager._build_rule_index()
        
        assert len(manager._rule_index["exact"]) == 1
        assert len(manager._rule_index["contains"]) == 1
        assert len(manager._rule_index["regex"]) == 0
    
    def test_performance_many_rules(self):
        import time
        import platform
        
        manager = ResponseConfigManager()
        
        for i in range(100):
            manager.config.rules.append(
                ResponseRule(
                    trigger=f"规则{i}",
                    response=f"响应{i}",
                    match_type="exact",
                    enabled=True
                )
            )
        
        manager._build_rule_index()
        
        start_time = time.time()
        for i in range(1000):
            manager.get_response(f"规则{i % 100}")
        end_time = time.time()
        
        # 根据系统平台调整性能期望
        if platform.system() == 'Windows':
            # Windows系统性能较低，放宽到3秒
            assert (end_time - start_time) < 3.0
        else:
            # Linux/Mac系统保持原有标准
            assert (end_time - start_time) < 1.0