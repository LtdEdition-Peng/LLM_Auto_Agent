import os

class AgentConfig:
    """Agent配置类，管理所有超参数"""
    
    def __init__(self):
        # API配置
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = "gemini-2.5-flash"
        
        # 对话管理配置
        self.max_steps = 10  #单次ai最多执行步骤
        self.refresh_prompt_interval = 3 # 每N轮完整交互后将原始提示词重新发送给ai
    
         
        # 工作目录配置
        self.project_directory = "D:/"  # 这个用处不大，传入时候会将这个目录下的文件作为系统提示词一部分
        
        # 调试配置
        self.show_system_messages = False  # 是否显示系统消息
        self.conda = "New"  # conda环境名称,执行py指令时候会使用该环境
