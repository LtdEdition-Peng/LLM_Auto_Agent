

import json
import os
import platform

from string import Template
from typing import List, Dict, Any, Optional
from google import genai
from prompt_template import react_system_prompt_template
import tools
from Toolmanager import ToolManager
from AgentConfig import AgentConfig
from ConversationManager import ConversationManager


class ReactAgent:
    """ReAct Agent主类，整合所有功能"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.client = genai.Client(api_key=self.config.api_key)
        self.conversation = ConversationManager(self.config)
        self.tool_manager = ToolManager()
        
    def get_operating_system_name(self) -> str:
        """获取操作系统名称"""
        os_map = {
            "Darwin": "macOS",
            "Windows": "Windows", 
            "Linux": "Linux"
        }
        return os_map.get(platform.system(), "Unknown")
        
    def render_system_prompt(self) -> str:
        """渲染系统提示模板"""
        tool_list = self.tool_manager.get_tool_list()
        file_list = ", ".join(
            os.path.abspath(os.path.join(self.config.project_directory, f))
            for f in os.listdir(self.config.project_directory)
        )
        return Template(react_system_prompt_template).substitute(
            operating_system=self.get_operating_system_name(),
            tool_list=tool_list,
            file_list=file_list
        )
        
    def parse_ai_response(self, content: str) -> Dict[str, Any]:
        """解析AI响应内容，将字符串形式返回转化为json"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            if self.config.show_system_messages:
                print("无法解析 JSON 响应，可能是格式错误")
                print(f"原始响应: {content}")
            # 这里考虑添加手动解析？
            raise
            
    def handle_final_answer(self, response_json: Dict[str, Any]) -> str:
        """处理最终答案"""
        final_answer = response_json['final_answer']
        print(f"Answer: {final_answer}")
            
        interaction_count = self.conversation.increment_interaction()
        if self.config.show_system_messages:
            print(f"[系统] 完成第 {interaction_count} 轮交互（final_answer）")
            
        return final_answer
        
    def handle_action(self, response_json: Dict[str, Any]) -> None:
        """处理AI动作执行"""
        action_str = response_json["action"]
        if self.config.show_system_messages:
            print(f"[系统] 执行动作: {action_str}")
            
        try:
            if self.config.show_system_messages:
                print(f"[系统] 正在解析函数调用: {action_str}")
            func_name = self.tool_manager.parse_action_list(action_str)
            result = self.tool_manager.execute_action_list(func_name)
            self.conversation.add_observation(str(result))
            
            if self.config.show_system_messages:
                print(f"观察结果: {result}")
                print(f"[系统] 当前发送总请求数量: {len(self.conversation.messages)}")
                
        except ValueError as e:
            self.conversation.add_error_observation(str(e))
            if self.config.show_system_messages:
                print(f"工具调用错误: {e}")
                print("[系统] 已将错误信息返回给AI")
                
        except Exception as e:
            error_msg = f"工具执行失败: {str(e)}"
            self.conversation.add_error_observation(error_msg)
            if self.config.show_system_messages:
                print(f"工具执行出错: {e}")
                print("[系统] 已将错误信息返回给AI")
                
    def get_user_input(self, prompt: str = "Question: ") -> str:
        """获取用户输入"""
        return input(prompt)
        
    def process_turn(self) -> bool:
        """处理一轮对话，返回是否继续"""
        try:
            # 调用AI模型
            response = self.client.models.generate_content(
                model=self.config.model_name,
                contents=self.conversation.messages
            )
            content = response.text
            self.conversation.add_message("model", content)
            
            if self.config.show_system_messages:
                print("Agent:", content)
                
            # 解析AI响应
            response_json = self.parse_ai_response(content)
            
            if "final_answer" in response_json:
                self.handle_final_answer(response_json)
                return True  # 需要新的用户输入
                
            elif "action" in response_json:
                self.handle_action(response_json)
                return False  # 继续AI推理
                
            else:
                if self.config.show_system_messages:
                    print("[系统] AI响应中没有找到 'final_answer' 或 'action' 字段")
                    print(f"[系统] 响应内容: {response_json}")
                return False
                
        except json.JSONDecodeError:
            return False
        except Exception as e:
            if self.config.show_system_messages:
                print(f"API 调用失败: {e}")
            return True  # 出错时退出
            
    def run(self) -> None:
        """运行Agent主循环"""
        print("=== ReAct Agent 启动 ===")
        
        # 初始用户输入
        user_input = self.get_user_input()
        system_prompt = self.render_system_prompt()
        self.conversation.add_system_message(user_input, system_prompt)
        
        step_count = 0 # 步数，非final结果数，执行一次action算一次
        while step_count < self.config.max_steps:
            step_count += 1
            
            need_new_input = self.process_turn()
            
            if need_new_input:
                # 检查是否需要刷新系统提示
                if self.conversation.should_refresh_prompt():
                    if self.config.show_system_messages:
                        print(f"[系统] 达到 {self.config.refresh_prompt_interval} 轮交互，重新添加系统提示")
                        
                    user_input = self.get_user_input()
                    system_prompt = self.render_system_prompt()
                    self.conversation.refresh_context_with_prompt(user_input, system_prompt)
                    
                    if self.config.show_system_messages:
                        print(f"[系统] 系统提示已刷新，当前 {len(self.conversation.messages)} 条上下文消息")
                else:
                    user_input = self.get_user_input()
                    self.conversation.add_message("user", f"question: {user_input}")
                    
                step_count = 0  # 重置步骤计数
                
        print("任务未完成，已达到最大步骤")


