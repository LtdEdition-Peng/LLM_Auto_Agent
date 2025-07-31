from agent import ReactAgent
from AgentConfig import AgentConfig
def main():
    """主函数"""
    # 创建自定义配置
    config = AgentConfig()
    config.max_steps = 10
    config.refresh_prompt_interval = 30
    config.show_system_messages = False  # 显示中间信息，如果不需要可以设置为False
    config.conda = "New"  # 请提前安装anaconda，并且创建名字为New环境，如果有其他环境，请修改agenttools里面的调用python的默认环境（在此处修改无效，这是一个bug）

    # 创建并运行Agent
    agent = ReactAgent(config)
    agent.run()


if __name__ == "__main__":
    main()
