import yaml
import os
import re
from typing import Optional, List, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field


class ResponseRule(BaseModel):
    trigger: str
    response: str
    match_type: str = Field(default="contains", pattern="^(exact|contains|regex)$")
    enabled: bool = True


class ResponseConfig(BaseModel):
    default_response: str = "这是一个模拟响应。"
    rules: List[ResponseRule] = []
    metadata: Dict[str, Any] = {}


class ResponseConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config: ResponseConfig = ResponseConfig()
        self._regex_cache = {}
        self._rule_index = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "config"
        
        # 检查是否在测试环境中
        is_test = os.getenv('PYTEST_XDIST_WORKER') is not None or \
                  os.getenv('PYTEST_CURRENT_TEST') is not None or \
                  os.getenv('TESTING') == '1'
        
        # 根据环境选择配置文件
        if is_test:
            config_file = "test_responses.yaml"
        else:
            config_file = "responses.yaml"
        
        config_path = config_dir / config_file
        
        # 如果测试配置不存在，使用默认配置
        if is_test and not config_path.exists():
            print(f"警告: 测试配置文件不存在，使用默认配置")
            config_path = config_dir / "responses.yaml"
        
        return str(config_path)
    
    def _validate_config(self, data: dict) -> bool:
        try:
            if "responses" not in data:
                print("配置验证失败: 缺少 'responses' 键")
                return False
            
            responses = data["responses"]
            if "default_response" not in responses:
                print("配置验证失败: 缺少 'default_response' 键")
                return False
            
            if "rules" not in responses:
                print("配置验证失败: 缺少 'rules' 键")
                return False
            
            for i, rule in enumerate(responses["rules"]):
                if not self._validate_rule(rule):
                    print(f"配置验证失败: 规则 {i} 验证失败")
                    return False
            
            return True
        except Exception as e:
            print(f"配置验证异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _validate_rule(self, rule: dict) -> bool:
        required_fields = ["trigger", "response", "match_type"]
        for field in required_fields:
            if field not in rule:
                return False
        
        if rule["match_type"] not in ["exact", "contains", "regex"]:
            return False
        
        if rule["match_type"] == "regex":
            try:
                re.compile(rule["trigger"])
            except re.error:
                return False
        
        return True
    
    def _load_config(self) -> None:
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    
                    if not self._validate_config(data):
                        print("配置文件验证失败，使用默认配置")
                        self.config = ResponseConfig()
                    else:
                        self.config = ResponseConfig(**data["responses"])
            else:
                print("配置文件不存在，使用默认配置")
                self.config = ResponseConfig()
        except yaml.YAMLError as e:
            print(f"YAML解析错误: {e}，使用默认配置")
            self.config = ResponseConfig()
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            self.config = ResponseConfig()
        
        self._build_rule_index()
    
    def _build_rule_index(self):
        self._rule_index = {
            "exact": [],
            "contains": [],
            "regex": []
        }
        
        for i, rule in enumerate(self.config.rules):
            if rule.enabled:
                self._rule_index[rule.match_type].append((i, rule))
    
    def reload_config(self) -> None:
        self._load_config()
    
    def get_response(self, user_input: str) -> str:
        if not user_input or not user_input.strip():
            return self.config.default_response
        
        if not self.config.rules:
            return self.config.default_response
        
        for match_type in ["exact", "contains", "regex"]:
            for index, rule in self._rule_index[match_type]:
                if self._match_trigger(rule, user_input):
                    return rule.response
        
        return self.config.default_response
    
    def _get_compiled_regex(self, pattern: str) -> re.Pattern:
        if pattern not in self._regex_cache:
            self._regex_cache[pattern] = re.compile(pattern)
        return self._regex_cache[pattern]
    
    def _match_trigger(self, rule: ResponseRule, user_input: str) -> bool:
        try:
            if rule.match_type == "exact":
                return rule.trigger.strip() == user_input.strip()
            elif rule.match_type == "contains":
                return rule.trigger in user_input
            elif rule.match_type == "regex":
                compiled_regex = self._get_compiled_regex(rule.trigger)
                return bool(compiled_regex.search(user_input))
            return False
        except Exception as e:
            print(f"匹配规则时出错: {e}")
            return False
    
    def get_config(self) -> ResponseConfig:
        return self.config
    
    def update_config(self, config: ResponseConfig) -> None:
        self.config = config
        self._save_config()
        self._build_rule_index()
    
    def _save_config(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config.model_dump(), f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def add_rule(self, rule: ResponseRule) -> None:
        self.config.rules.append(rule)
        self._save_config()
        self._build_rule_index()
    
    def remove_rule(self, index: int) -> bool:
        if 0 <= index < len(self.config.rules):
            self.config.rules.pop(index)
            self._save_config()
            self._build_rule_index()
            return True
        return False
    
    def update_rule(self, index: int, rule: ResponseRule) -> bool:
        if 0 <= index < len(self.config.rules):
            self.config.rules[index] = rule
            self._save_config()
            self._build_rule_index()
            return True
        return False
    
    def enable_rule(self, index: int, enabled: bool) -> bool:
        if 0 <= index < len(self.config.rules):
            self.config.rules[index].enabled = enabled
            self._save_config()
            self._build_rule_index()
            return True
        return False
    
    def search_rules(self, keyword: str, match_type: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        
        for index, rule in enumerate(self.config.rules):
            if match_type and rule.match_type != match_type:
                continue
            
            if keyword.lower() in rule.trigger.lower() or keyword.lower() in rule.response.lower():
                results.append({
                    "index": index,
                    "rule": rule.model_dump()
                })
        
        return results
    
    def validate_rule(self, rule: ResponseRule) -> tuple[bool, Optional[str]]:
        if not rule.trigger or not rule.trigger.strip():
            return False, "触发词不能为空"
        
        if not rule.response or not rule.response.strip():
            return False, "响应不能为空"
        
        if rule.match_type == "regex":
            try:
                re.compile(rule.trigger)
            except re.error as e:
                return False, f"正则表达式错误: {str(e)}"
        
        return True, None