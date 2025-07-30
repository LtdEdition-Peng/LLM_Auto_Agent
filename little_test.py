"""
简化版测试代码，可独立运行
"""

import ast
import re
from google import genai
import os
import platform
from string import Template
import ast
import inspect
import os
import re
from string import Template
from typing import List, Callable, Tuple
from prompt_template import react_system_prompt_template

API_KEY = os.getenv("GOOGLE_API_KEY")
# 初始化客户端
google_client = genai.Client(api_key=API_KEY)
project_directory = "D:/"


def read_file(file_path):
    """
    读取指定文件的全部内容
    
    Args:
        file_path (str): 要读取的文件的绝对路径或相对路径，支持各种文本文件格式
                        例如: "D:/example.txt", "/home/user/data.json", "config.ini"
    
    Returns:
        str: 文件的完整文本内容，保持原有的换行符和格式
    
    Raises:
        FileNotFoundError: 当指定的文件不存在时抛出
        PermissionError: 当没有读取文件权限时抛出
        UnicodeDecodeError: 当文件编码不是UTF-8时可能抛出
    
    Example:
        content = read_file("D:/test.txt")
        # 返回文件的完整内容字符串
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_to_file(file_path, content):
    """
    将指定内容写入文件，如果文件不存在则创建，如果存在则覆盖
    
    Args:
        file_path (str): 目标文件的绝对路径，支持创建新文件
                        例如: "D:/output.txt", "/home/user/result.json", 
        content (str): 要写入文件的文本内容，支持包含换行符的多行文本
                      函数会自动将转义的换行符 "\\n" 转换为实际的换行符
    
    Returns:
        str: 成功时返回 "写入成功"，用于确认操作完成
    
    Raises:
        PermissionError: 当没有写入文件权限时抛出
        FileNotFoundError: 当指定的目录不存在时抛出
        OSError: 当磁盘空间不足或其他IO错误时抛出
    
    Example:
        result = write_to_file("D:/output.txt", "Hello\\nWorld")
        # 会在文件中写入两行：Hello 和 World
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.replace("\\n", "\n"))
    return "写入成功"


def run_terminal_command(command):
    """
    执行系统终端命令并返回详细的执行结果
    
    Args:
        command (str): 要执行的终端命令字符串，支持各种系统命令和参数
                      例如: "ls -la", "dir", "python --version", "git status"
                      注意：命令会在shell环境中执行，支持管道和重定向
    
    Returns:
        dict: 包含执行结果的字典，根据执行状态返回不同格式：
            成功时: {"status": "success", "output": "命令的标准输出"}
            失败时: {"status": "error", "returncode": 错误码, "error": "错误信息"}
            异常时: {"status": "exception", "error": "异常描述"}
    
    Raises:
        无直接异常抛出，所有异常都被捕获并在返回值中体现
    
    Examples:
        # 成功执行
        result = run_terminal_command("echo Hello")
        # 返回: {"status": "success", "output": "Hello\n"}
        
        # 命令失败
        result = run_terminal_command("nonexistent_command")
        # 返回: {"status": "error", "returncode": 127, "error": "command not found"}
        
        # 列出文件
        result = run_terminal_command("dir" if platform.system() == "Windows" else "ls")
        # 返回当前目录的文件列表
    """
    import subprocess

    try:
        # 执行命令并捕获输出
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        # 如果需要，可以根据具体需求调整返回值格式
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        # 命令执行失败时，返回错误码和错误输出
        return {"status": "error", "returncode": e.returncode, "error": e.stderr}
    except Exception as e:
        # 捕获其他可能的异常，比如命令不存在等
        return {"status": "exception", "error": str(e)}


tools = {func.__name__: func for func in [read_file, write_to_file, run_terminal_command]}


def render_system_prompt(system_prompt_template: str) -> str:
    """渲染系统提示模板，替换变量"""
    tool_list = get_tool_list()
    file_list = ", ".join(
        os.path.abspath(os.path.join(project_directory, f))
        for f in os.listdir(project_directory)
    )
    return Template(system_prompt_template).substitute(
        operating_system=get_operating_system_name(),
        tool_list=tool_list,
        file_list=file_list
    )


def get_operating_system_name() -> str:
    os_map = {
        "Darwin": "macOS",
        "Windows": "Windows",
        "Linux": "Linux"
    }
    return os_map.get(platform.system(), "Unknown")


def get_tool_list() -> str:
    """生成工具列表字符串，包含函数签名和简要说明"""
    tool_descriptions = []
    for func in tools.values():
        name = func.__name__
        signature = str(inspect.signature(func))
        doc = inspect.getdoc(func)
        tool_descriptions.append(f"- {name}{signature}: {doc}")
    return "\n".join(tool_descriptions)


def create_system_message(user_question: str) -> dict:
    """创建包含系统提示的消息"""
    system_prompt = render_system_prompt(react_system_prompt_template)
    content = f"{system_prompt}\n\nquestion: {user_question}"
    return {"role": "user", "parts": [{"text": content}]}


def manage_message_context(messages: list, max_context_length: int = 10) -> list:
    """管理消息上下文长度，保留最重要的消息"""
    if len(messages) <= max_context_length:
        return messages
    
    # 保留最近的消息，确保上下文连贯性
    # 优先保留: 最新的用户问题、AI回答、工具执行结果
    important_messages = []
    recent_messages = messages[-max_context_length:]
    
    for msg in recent_messages:
        # 保留包含observation的消息（工具执行结果）
        if "observation" in str(msg.get("parts", [{}])[0].get("text", "")):
            important_messages.append(msg)
        # 保留最近的用户问题和AI回答
        elif msg["role"] in ["user", "model"]:
            important_messages.append(msg)
    
    return important_messages[-max_context_length:]



# 配置参数
REFRESH_PROMPT_INTERVAL = 3  # 每3轮交互后重新添加系统提示
interaction_count = 0  # 交互轮次计数器

user_input = input("请输入你的问题: ")

# 将 system prompt 拼接到 user input 中
system_prompt = render_system_prompt(react_system_prompt_template)
initial_input = f"{system_prompt}\n\nquestion: {user_input}"

messages = [
    {"role": "user", "parts": [{"text": initial_input}]}
]

max_steps = 10  # 防止无限循环，适当增加步骤数

for _ in range(max_steps):
    try:
        response = google_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages
        )
        content = response.text
        messages.append({"role": "model", "parts": [{"text":content}]})

        print("Agent:", content)
        
        # 解析 JSON 格式的响应
        try:
            import json
            # 尝试解析 JSON
            response_json = json.loads(content)
            
            if "final_answer" in response_json:
                print(f"最终答案: {response_json['final_answer']}")
                interaction_count += 1  # 完成一轮交互
                print(f"[系统] 完成第 {interaction_count} 轮交互")
                
                # 检查是否需要刷新系统提示
                if interaction_count % REFRESH_PROMPT_INTERVAL == 0:
                    print(f"[系统] 达到 {REFRESH_PROMPT_INTERVAL} 轮交互，重新添加系统提示")
                    
                    user_input = input("请输入你的问题: ")
                    
                    # 管理消息上下文，避免过长
                    messages = manage_message_context(messages, max_context_length=8)
                    
                    # 添加新的系统提示消息
                    system_message = create_system_message(user_input)
                    messages.append(system_message)
                    
                    print(f"[系统] 系统提示已刷新，保留 {len(messages)} 条上下文消息")
                else:
                    user_input = input("请输入你的问题: ")
                    messages.append({"role": "user", "parts": [{"text": f"question: {user_input}"}]})
            elif "action" in response_json:
                action_str = response_json["action"]
                print(f"执行动作: {action_str}")
                
                # 解析函数调用
                try:
                    # 使用正则表达式解析函数调用格式：function_name(arg1, arg2, ...)
                    func_match = re.match(r'(\w+)\((.*)\)', action_str)
                    if func_match:
                        func_name = func_match.group(1)
                        args_str = func_match.group(2)
                        
                        # 解析参数
                        if args_str.strip():
                            # 使用 ast.literal_eval 安全解析参数
                            args = ast.literal_eval(f"({args_str})")
                            # 如果只有一个参数，确保它是元组格式
                            if not isinstance(args, tuple):
                                args = (args,)
                        else:
                            args = ()
                        
                        if func_name in tools:
                            try:
                                result = tools[func_name](*args)
                                observation_msg = f'{{"observation": "{result}"}}'
                                messages.append({"role": "user", "parts": [{"text": observation_msg}]})
                                print(f"观察结果: {result}")
                                print(f"[系统] 当前消息数: {len(messages)}")
                            except Exception as tool_error:
                                # 工具执行失败，将错误信息返回给AI
                                error_msg = f'{{"observation": "工具执行失败: {str(tool_error)}"}}'
                                messages.append({"role": "user", "parts": [{"text": error_msg}]})
                                print(f"工具执行出错: {tool_error}")
                                print(f"[系统] 已将错误信息返回给AI")
                        else:
                            # 未知函数，也要告知AI
                            error_msg = f'{{"observation": "错误: 未知的工具函数 {func_name}"}}'
                            messages.append({"role": "user", "parts": [{"text": error_msg}]})
                            print(f"未知的工具函数: {func_name}")
                    else:
                        # 函数调用格式解析失败，告知AI
                        error_msg = f'{{"observation": "错误: 无法解析函数调用格式 {action_str}"}}'
                        messages.append({"role": "user", "parts": [{"text": error_msg}]})
                        print(f"无法解析函数调用格式: {action_str}")
                except Exception as e:
                    # 参数解析失败，告知AI
                    error_msg = f'{{"observation": "错误: 函数参数解析失败 - {str(e)}"}}'
                    messages.append({"role": "user", "parts": [{"text": error_msg}]})
                    print(f"执行工具函数时出错: {e}")
                    print(f"[系统] 已将参数解析错误返回给AI")
            else:
                print("[系统] AI响应中没有找到 'final_answer' 或 'action' 字段")
                print(f"[系统] 响应内容: {response_json}")
        except json.JSONDecodeError:
            print("无法解析 JSON 响应，可能是格式错误")
            print(f"原始响应: {content}")
            # 如果JSON解析失败，尝试提取可能的action内容
            action_match = re.search(r'"action":\s*"([^"]*)"', content)
            if action_match:
                print(f"[备用] 尝试提取到action: {action_match.group(1)}")
    except Exception as e:
        print(f"API 调用失败: {e}")
        break
else:
    print("任务未完成，已达到最大步骤")