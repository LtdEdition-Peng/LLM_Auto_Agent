import tools
import re
import ast
import subprocess
import inspect
from typing import List, Dict, Any,Tuple


class ToolManager:
    """工具管理类，处理工具的注册、调用和错误处理"""
    
    def __init__(self):
        self.tools = {}
        self._register_tools_from_module()
        
    def _register_tools_from_module(self):
        """从tools模块注册工具函数"""
        # 获取tools模块中的所有函数
        for attr_name in dir(tools):
            attr = getattr(tools, attr_name)
            # 检查是否是函数且不是私有函数，并且是在tools模块中定义的
            if (callable(attr) and 
                not attr_name.startswith('_') and 
                hasattr(attr, '__module__') and 
                attr.__module__ == 'tools'):
                self.tools[attr_name] = attr

    def parse_action_list(self, action_list: List[Dict[str, Any]]) -> List[Tuple[str, Dict[str, Any]]]:
        """
        解析JSON格式的动作列表
        
        Args:
            action_list (List[Dict]): 动作列表，每个动作包含tool和参数
            格式：[{"tool": "tool_name", "param1": "value1", "param2": "value2"}, ...]
            
        Returns:
            List[Tuple[str, Dict[str, Any]]]: [(工具名, 参数字典), ...]
        """
        if not isinstance(action_list, list):
            raise ValueError("action必须是一个列表")
        
        if not action_list:
            raise ValueError("action列表不能为空")
        
        parsed_actions = []
        for i, action in enumerate(action_list):
            if not isinstance(action, dict):
                raise ValueError(f"第{i+1}个action必须是字典格式")
            
            if "tool" not in action:
                raise ValueError(f"第{i+1}个action缺少'tool'字段")
            
            tool_name = action["tool"]
            if not isinstance(tool_name, str):
                raise ValueError(f"第{i+1}个action的'tool'字段必须是字符串")
            
            # 提取除了'tool'之外的所有参数
            params = {k: v for k, v in action.items() if k != "tool"}
            
            parsed_actions.append((tool_name, params))
        
        return parsed_actions
        
    def execute_tool(self, func_name: str, params: Dict[str, Any]) -> Any:
        """
        执行工具函数，使用关键字参数
        
        Args:
            func_name (str): 函数名
            params (Dict[str, Any]): 参数字典
            
        Returns:
            Any: 函数执行结果
        """
        if func_name not in self.tools:
            raise ValueError(f"未知的工具函数: {func_name}")
        
        try:
            return self.tools[func_name](**params)
        except TypeError as e:
            # 提供更友好的参数错误信息
            sig = inspect.signature(self.tools[func_name])
            raise ValueError(f"工具'{func_name}'参数错误: {e}。期望参数: {sig}")
    
    def execute_action_list(self, action_list: List[Dict[str, Any]]) -> List[Any]:
        """
        执行多个工具调用
        
        Args:
            action_list (List[Dict]): 动作列表
            
        Returns:
            List[Any]: 所有工具执行结果的列表
        """
        # parsed_actions = self.parse_action_list(action_list) 这个有点问题
        results = []
        
        for tool_name, params in action_list:
            try:
                result = self.execute_tool(tool_name, params)
                results.append(result)
            except Exception as e:
                # 记录错误但继续执行其他工具
                error_msg = f"工具'{tool_name}'执行失败: {e}"
                results.append({"error": error_msg})
        
        return results
    
    def execute_parsed_actions(self, parsed_actions: List[Tuple[str, Dict[str, Any]]]) -> List[Any]:
        """
        执行已解析的工具调用
        
        Args:
            parsed_actions (List[Tuple[str, Dict[str, Any]]]): 已解析的动作列表
            
        Returns:
            List[Any]: 所有工具执行结果的列表
        """
        results = []
        
        for tool_name, params in parsed_actions:
            try:
                result = self.execute_tool(tool_name, params)
                results.append(result)
            except Exception as e:
                # 记录错误但继续执行其他工具
                error_msg = f"工具'{tool_name}'执行失败: {e}"
                results.append({"error": error_msg})
        
        return results
    
    def get_tool_list(self) -> str:
        """获取工具列表的描述信息，用于生成系统提示词"""
        tool_descriptions = []
        
        for tool_name, tool_func in self.tools.items():
            # 获取函数签名和文档字符串
            sig = inspect.signature(tool_func)
            doc = inspect.getdoc(tool_func)
            signature = f"{tool_name}{sig}"
            tool_descriptions.append(f"- {signature}: {doc}")
        
        return "\n".join(tool_descriptions)
    
    def register_tool(self, name: str, func: callable) -> None:
        """注册新的工具函数"""
        self.tools[name] = func
    
    def unregister_tool(self, name: str) -> bool:
        """注销工具函数"""
        if name in self.tools:
            del self.tools[name]
            return True
        return False
    
    def list_tools(self) -> List[str]:
        """返回所有已注册工具的名称列表"""
        return list(self.tools.keys())

