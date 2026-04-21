import os
import shutil

# 必须在导入app之前设置环境变量
os.environ['TESTING'] = '1'

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.api.chat import mock_service


@pytest.fixture(autouse=True)
def reset_mock_service():
    """每个测试前自动重置mock_service和测试配置"""
    # 从模板恢复测试配置
    test_config_path = Path("config/test_responses.yaml")
    template_path = Path("config/test_responses.yaml.template")
    
    if template_path.exists():
        shutil.copy(template_path, test_config_path)
    
    # 重置mock_service（会自动使用测试配置）
    mock_service.reset_all()
    
    yield
    
    # 测试后不需要恢复配置，因为下一个测试会从模板恢复


class TestYAMLConfigAPI:
    def test_get_yaml_config(self):
        client = TestClient(app)
        response = client.get("/v1/config/yaml")
        
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "config" in data
        assert "default_response" in data["config"]
        assert "rules" in data["config"]
    
    def test_enable_yaml_config(self):
        client = TestClient(app)
        response = client.put("/v1/config/yaml/enable")
        
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        
        # 验证配置已启用
        response = client.get("/v1/config/yaml")
        data = response.json()
        assert data["enabled"] is True
    
    def test_disable_yaml_config(self):
        client = TestClient(app)
        
        # 先启用
        client.put("/v1/config/yaml/enable")
        
        # 再禁用
        response = client.put("/v1/config/yaml/disable")
        
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False
    
    def test_reload_yaml_config(self):
        client = TestClient(app)
        response = client.post("/v1/config/yaml/reload")
        
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "config" in data
    
    def test_add_yaml_rule(self):
        client = TestClient(app)
        
        new_rule = {
            "trigger": "测试",
            "response": "测试响应",
            "match_type": "exact",
            "enabled": True
        }
        
        response = client.post("/v1/config/yaml/rules", json=new_rule)
        
        assert response.status_code == 200
        data = response.json()
        assert "config" in data
        assert "rules" in data["config"]
        
        # 验证规则已添加
        rules = data["config"]["rules"]
        assert any(rule["trigger"] == "测试" for rule in rules)
    
    def test_delete_yaml_rule(self):
        client = TestClient(app)
        
        # 先添加一个规则
        new_rule = {
            "trigger": "临时规则",
            "response": "临时响应",
            "match_type": "exact",
            "enabled": True
        }
        client.post("/v1/config/yaml/rules", json=new_rule)
        
        # 获取当前规则数量
        response = client.get("/v1/config/yaml")
        rules = response.json()["config"]["rules"]
        initial_count = len(rules)
        
        # 删除第一个规则
        response = client.delete("/v1/config/yaml/rules/0")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["config"]["rules"]) == initial_count - 1
    
    def test_delete_invalid_rule_index(self):
        client = TestClient(app)
        response = client.delete("/v1/config/yaml/rules/999")
        
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_update_yaml_rule(self):
        client = TestClient(app)
        
        # 先添加一个规则
        new_rule = {
            "trigger": "原始规则",
            "response": "原始响应",
            "match_type": "exact",
            "enabled": True
        }
        client.post("/v1/config/yaml/rules", json=new_rule)
        
        # 获取当前规则
        response = client.get("/v1/config/yaml")
        rules = response.json()["config"]["rules"]
        rule_index = len(rules) - 1
        
        # 更新规则
        updated_rule = {
            "trigger": "更新后的规则",
            "response": "更新后的响应",
            "match_type": "exact",
            "enabled": True
        }
        
        response = client.put(f"/v1/config/yaml/rules/{rule_index}", json=updated_rule)
        
        assert response.status_code == 200
        data = response.json()
        updated_rules = data["config"]["rules"]
        assert updated_rules[rule_index]["trigger"] == "更新后的规则"
        assert updated_rules[rule_index]["response"] == "更新后的响应"
    
    def test_update_invalid_rule_index(self):
        client = TestClient(app)
        
        updated_rule = {
            "trigger": "更新后的规则",
            "response": "更新后的响应",
            "match_type": "exact",
            "enabled": True
        }
        
        response = client.put("/v1/config/yaml/rules/999", json=updated_rule)
        
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_enable_yaml_rule(self):
        client = TestClient(app)
        
        # 添加一个禁用的规则
        new_rule = {
            "trigger": "禁用规则",
            "response": "禁用响应",
            "match_type": "exact",
            "enabled": False
        }
        client.post("/v1/config/yaml/rules", json=new_rule)
        
        # 获取规则索引
        response = client.get("/v1/config/yaml")
        rules = response.json()["config"]["rules"]
        rule_index = len(rules) - 1
        
        # 启用规则
        response = client.put(f"/v1/config/yaml/rules/{rule_index}/enable")
        
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["rules"][rule_index]["enabled"] is True
    
    def test_disable_yaml_rule(self):
        client = TestClient(app)
        
        # 添加一个启用的规则
        new_rule = {
            "trigger": "启用规则",
            "response": "启用响应",
            "match_type": "exact",
            "enabled": True
        }
        client.post("/v1/config/yaml/rules", json=new_rule)
        
        # 获取规则索引
        response = client.get("/v1/config/yaml")
        rules = response.json()["config"]["rules"]
        rule_index = len(rules) - 1
        
        # 禁用规则
        response = client.put(f"/v1/config/yaml/rules/{rule_index}/disable")
        
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["rules"][rule_index]["enabled"] is False
    
    def test_enable_invalid_rule_index(self):
        client = TestClient(app)
        response = client.put("/v1/config/yaml/rules/999/enable")
        
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_chat_with_yaml_config_enabled(self):
        client = TestClient(app)
        
        # 启用YAML配置
        client.put("/v1/config/yaml/enable")
        
        # 发送匹配规则的请求
        response = client.post("/v1/chat/completions", json={
            "messages": [
                {"role": "user", "content": "你好"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "你好！有什么可以帮助你的吗？" in data["choices"][0]["message"]["content"]
    
    def test_chat_with_yaml_config_disabled(self):
        client = TestClient(app)
        
        # 禁用YAML配置
        client.put("/v1/config/yaml/disable")
        
        # 发送请求
        response = client.post("/v1/chat/completions", json={
            "messages": [
                {"role": "user", "content": "你好"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
        # 应该返回默认响应（settings.mock_response）
        assert "mock response" in data["choices"][0]["message"]["content"].lower()
    
    def test_chat_with_contains_match(self):
        client = TestClient(app)
        
        # 启用YAML配置
        client.put("/v1/config/yaml/enable")
        
        # 发送包含触发词的请求
        response = client.post("/v1/chat/completions", json={
            "messages": [
                {"role": "user", "content": "今天天气怎么样"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "天气不错" in data["choices"][0]["message"]["content"]
    
    def test_chat_with_regex_match(self):
        client = TestClient(app)
        
        # 启用YAML配置
        client.put("/v1/config/yaml/enable")
        
        # 发送匹配正则的请求
        response = client.post("/v1/chat/completions", json={
            "messages": [
                {"role": "user", "content": "系统错误"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "错误" in data["choices"][0]["message"]["content"]
    
    def test_chat_with_no_match(self):
        client = TestClient(app)
        
        # 启用YAML配置
        client.put("/v1/config/yaml/enable")
        
        # 发送不匹配任何规则的请求
        response = client.post("/v1/chat/completions", json={
            "messages": [
                {"role": "user", "content": "随机内容123"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        # 应该返回默认响应（测试环境的默认响应）
        assert "测试响应" in data["choices"][0]["message"]["content"]
    
    def test_validate_yaml_config_valid(self):
        client = TestClient(app)
        
        valid_config = {
            "responses": {
                "default_response": "默认响应",
                "rules": [
                    {
                        "trigger": "测试",
                        "response": "测试响应",
                        "match_type": "exact",
                        "enabled": True
                    }
                ]
            }
        }
        
        response = client.post("/v1/config/yaml/validate", json=valid_config)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "message" in data
    
    def test_validate_yaml_config_invalid(self):
        client = TestClient(app)
        
        invalid_config = {
            "invalid_key": "value"
        }
        
        response = client.post("/v1/config/yaml/validate", json=invalid_config)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
    
    def test_validate_yaml_rule_valid(self):
        client = TestClient(app)
        
        valid_rule = {
            "trigger": "测试",
            "response": "测试响应",
            "match_type": "exact",
            "enabled": True
        }
        
        response = client.post("/v1/config/yaml/rules/validate", json=valid_rule)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "message" in data
    
    def test_validate_yaml_rule_empty_trigger(self):
        client = TestClient(app)
        
        invalid_rule = {
            "trigger": "",
            "response": "测试响应",
            "match_type": "exact",
            "enabled": True
        }
        
        response = client.post("/v1/config/yaml/rules/validate", json=invalid_rule)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "触发词不能为空" in data["message"]
    
    def test_validate_yaml_rule_empty_response(self):
        client = TestClient(app)
        
        invalid_rule = {
            "trigger": "测试",
            "response": "",
            "match_type": "exact",
            "enabled": True
        }
        
        response = client.post("/v1/config/yaml/rules/validate", json=invalid_rule)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "响应不能为空" in data["message"]
    
    def test_validate_yaml_rule_invalid_regex(self):
        client = TestClient(app)
        
        invalid_rule = {
            "trigger": "[invalid(",
            "response": "测试响应",
            "match_type": "regex",
            "enabled": True
        }
        
        response = client.post("/v1/config/yaml/rules/validate", json=invalid_rule)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "正则表达式错误" in data["message"]
    
    def test_search_yaml_rules_by_keyword(self):
        client = TestClient(app)
        
        # 添加一些规则
        rules = [
            {"trigger": "你好", "response": "你好！", "match_type": "exact", "enabled": True},
            {"trigger": "天气", "response": "天气不错", "match_type": "contains", "enabled": True},
            {"trigger": "测试", "response": "测试响应", "match_type": "exact", "enabled": True}
        ]
        
        for rule in rules:
            client.post("/v1/config/yaml/rules", json=rule)
        
        # 搜索规则
        response = client.get("/v1/config/yaml/rules/search?keyword=你好")
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert data["count"] >= 1
        assert any(result["rule"]["trigger"] == "你好" for result in data["results"])
    
    def test_search_yaml_rules_by_match_type(self):
        client = TestClient(app)
        
        # 添加一些规则
        rules = [
            {"trigger": "你好", "response": "你好！", "match_type": "exact", "enabled": True},
            {"trigger": "天气", "response": "天气不错", "match_type": "contains", "enabled": True},
            {"trigger": "测试", "response": "测试响应", "match_type": "exact", "enabled": True}
        ]
        
        for rule in rules:
            client.post("/v1/config/yaml/rules", json=rule)
        
        # 按类型搜索
        response = client.get("/v1/config/yaml/rules/search?keyword=&match_type=exact")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 2
        for result in data["results"]:
            assert result["rule"]["match_type"] == "exact"
    
    def test_search_yaml_rules_no_results(self):
        client = TestClient(app)
        
        # 搜索不存在的规则
        response = client.get("/v1/config/yaml/rules/search?keyword=不存在的关键词")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert len(data["results"]) == 0
    
    def test_search_yaml_rules_case_insensitive(self):
        client = TestClient(app)
        
        # 添加规则
        rule = {"trigger": "HELLO", "response": "你好", "match_type": "exact", "enabled": True}
        client.post("/v1/config/yaml/rules", json=rule)
        
        # 搜索小写
        response = client.get("/v1/config/yaml/rules/search?keyword=hello")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
    
    def test_empty_input_with_yaml_enabled(self):
        client = TestClient(app)
        
        # 启用YAML配置
        client.put("/v1/config/yaml/enable")
        
        # 发送空输入
        response = client.post("/v1/chat/completions", json={
            "messages": [
                {"role": "user", "content": ""}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        # 空输入应该返回默认的mock response（不是YAML配置中的默认响应）
        assert "mock response" in data["choices"][0]["message"]["content"].lower()
    
    def test_whitespace_input_with_yaml_enabled(self):
        client = TestClient(app)
        
        # 启用YAML配置
        client.put("/v1/config/yaml/enable")
        
        # 发送空白输入
        response = client.post("/v1/chat/completions", json={
            "messages": [
                {"role": "user", "content": "   "}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        # 应该返回默认响应（测试环境的默认响应）
        assert "测试响应" in data["choices"][0]["message"]["content"]
    
    def test_special_characters_in_trigger(self):
        client = TestClient(app)
        
        # 添加包含特殊字符的规则
        rule = {
            "trigger": "测试@#$%",
            "response": "特殊字符匹配",
            "match_type": "exact",
            "enabled": True
        }
        client.post("/v1/config/yaml/rules", json=rule)
        
        # 启用YAML配置
        client.put("/v1/config/yaml/enable")
        
        # 发送包含特殊字符的输入
        response = client.post("/v1/chat/completions", json={
            "messages": [
                {"role": "user", "content": "测试@#$%"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "特殊字符匹配" in data["choices"][0]["message"]["content"]