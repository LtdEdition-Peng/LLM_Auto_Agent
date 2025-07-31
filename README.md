# Python ReAct Agent 自动化助手

## 项目简介

这是一个基于 ReAct（Reasoning and Acting）模式的智能代理系统，该系统结合了推理和行动能力，能够通过多种工具与环境交互，同时结合CodeAct自动完成复杂任务。

## 核心特性

- 🤖 **智能推理**: 基于 Google Gemini 模型的智能对话和推理能力
- 🔧 **多工具集成**: 支持文件操作、网页搜索、系统命令执行等多种工具
- 💬 **对话管理**: 智能的上下文管理和对话状态维护
- 🔄 **自动循环**: 支持多步推理和工具调用的自动化流程
- ⚙️ **灵活配置**: 可配置的参数和环境设置

## 系统架构

### 核心组件

```
├── agent.py               # 主要的 ReAct Agent 类
├── AgentConfig.py         # 配置管理类
├── ConversationManager.py # 对话管理类
├── Toolmanager.py         # 工具管理类
├── agent_tools.py         # 工具函数集合
├── tools.py               # 系统函数
├── prompt_template.py     # 提示词模板
├── runagent.py            # 运行入口
└── little_test.py         # 简化版测试代码
```

### 工作流程

1. **用户输入** → 接收用户问题
2. **推理阶段** → AI 分析问题并制定行动计划
3. **检测阶段** → AI返回格式修正（AI自行处理）
4. **行动阶段** → 执行相应的工具调用
5. **观察阶段** → 获取工具执行结果
6. **循环或结束** → 根据结果决定继续推理或给出最终答案

## 安装和配置

### 环境要求

- Python 3.8+
- Conda 环境管理器(python 相关指令会需要激活环境)
- Google API Key
- 需要科学上网


### 环境变量配置

在系统环境变量中设置：
谷歌API秘钥可在此申请https://aistudio.google.com/apikey
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

## 快速开始

### 基础使用

```bash
conda activate yourenv
python runagent.py
```


### 基础版测试

```bash
python little_test.py
```


## 配置选项

### AgentConfig 参数

```python
class AgentConfig:
    api_key: str                    # Google API Key
    model_name: str                 # 模型名称 (默认: "gemini-2.5-flash")
    max_steps: int                  # 最大推理步数 (默认: 10)
    refresh_prompt_interval: int    # 提示词刷新间隔 (默认: 3)
    project_directory: str          # 项目目录 (默认: "D:/")
    show_system_messages: bool      # 是否显示系统消息 (默认: False)
    conda: str                      # Conda 环境名称 (默认: "New")
```


## 高级功能

### 多工具协作
Agent 支持在单次行动中调用多个工具，实现复杂任务的自动化处理。

### 上下文管理
自动管理对话历史，在达到设定轮次后智能刷新上下文，保持对话的连贯性。

### 错误处理
完善的错误处理机制，能够捕获工具执行错误并反馈给 AI 进行调整。

### 安全机制
对于危险系统命令，会要求用户确认后再执行。

## 开发和扩展

### 添加新工具

1. 在 `tools.py` 中定义新函数
2. 添加详细的文档字符串
3. 工具会自动注册到系统中

```python
def your_new_tool(param1: str, param2: int) -> str:
    """
    工具功能描述
    
    Args:
        param1: 参数1描述
        param2: 参数2描述
    
    Returns:
        返回值描述
    """
    # 实现代码
    return "结果"
```

### 自定义配置

创建自定义配置文件，覆盖默认设置：

```python
config = AgentConfig()
config.max_steps = 20
config.refresh_prompt_interval = 5
config.show_system_messages = True
```

## 注意事项

1. 确保 Google API Key 已正确配置(对话时需要科学上网)
2. 某些工具需要网络连接
3. 系统命令执行需要相应权限
4. Conda 环境需要预先配置

## 项目结构详解

- **agent.py**: 核心 ReAct Agent 实现
- **AgentConfig.py**: 配置管理，包含所有可调参数
- **ConversationManager.py**: 对话历史管理
- **Toolmanager.py**: 工具注册、解析和执行管理
- **tools.py**: 各种实用工具函数的实现
- **prompt_template.py**: ReAct 模式的提示词模板
- **runagent.py**: 主要运行入口
- **little_test.py**: 简化版本，用于快速测试

## 致谢

本项目的实现受到以下项目和研究的启发：

- 感谢项目教程 [MarkTechStation/VideoCode](https://github.com/MarkTechStation/VideoCode)
- 感谢 Google Gemini API 提供的强大语言模型支持


如果您在使用本项目时发现任何问题或有改进建议，欢迎提交 Issue 或 Pull Request！

## 许可证

本项目基于 MIT 许可证开源，详情请参见 [LICENSE](LICENSE) 文件。

