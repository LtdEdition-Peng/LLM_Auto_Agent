from typing import List, Dict, Any, Optional
from AgentConfig import AgentConfig
import json
import re



class ConversationManager:
    """对话管理类，处理消息的存储"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.messages: List[Dict[str, Any]] = []
        self.interaction_count = 0
        
    def add_message(self, role: str, content: str) -> None:
        """添加消息到对话历史"""
        message = {"role": role, "parts": [{"text": content}]}
        print(f"[对话管理] 添加消息: {role} - {content}")
        self.messages.append(message)
        
    def add_system_message(self, user_question: str, system_prompt: str) -> None:
        """添加包含系统提示的消息"""
        content = f"{system_prompt}\n\nquestion: {user_question}"
        self.add_message("user", content)
        
    def add_observation(self, observation: str) -> None:
        """添加工具执行观察结果"""
        obs_msg = f'{{"observation": "{observation}"}}'
        self.add_message("user", obs_msg)
        
    def add_error_observation(self, error_msg: str) -> None:
        """添加错误观察结果"""
        error_obs = f'{{"observation": "错误: {error_msg}"}}'
        self.add_message("user", error_obs)
        
    def increment_interaction(self) -> int:
        """增加交互计数,每次final_answer后调用"""
        self.interaction_count += 1
        return self.interaction_count
        
    def should_refresh_prompt(self) -> bool:
        """检查是否需要刷新系统提示"""
        return self.interaction_count % self.config.refresh_prompt_interval == 0

    def refresh_context_with_prompt(self, user_question: str, system_prompt: str) -> None:
        """刷新上下文并添加新的系统提示"""
        # self.manage_context() 调用上下文截断总结
        self.add_system_message(user_question, system_prompt)

