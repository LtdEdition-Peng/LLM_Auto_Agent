
## 中文版本 / Chinese Version

[中文 README](README.md)

# Python ReAct Agent Automation Assistant

## Project Overview

This is an intelligent agent system based on the ReAct (Reasoning and Acting) paradigm that combines reasoning and action capabilities. The system can interact with the environment through various tools while integrating CodeAct to automatically complete complex tasks.

## Core Features

- 🤖 **Intelligent Reasoning**: Smart conversation and reasoning capabilities based on Google Gemini model
- 🔧 **Multi-Tool Integration**: Supports file operations, web search, system command execution, and more
- 💬 **Conversation Management**: Intelligent context management and conversation state maintenance
- 🔄 **Automatic Loop**: Supports automated workflows with multi-step reasoning and tool invocation
- ⚙️ **Flexible Configuration**: Configurable parameters and environment settings

## System Architecture

### Core Components

```
├── agent.py               # Main ReAct Agent class
├── AgentConfig.py         # Configuration management class
├── ConversationManager.py # Conversation management class
├── Toolmanager.py         # Tool management class
├── agent_tools.py         # Tool function collection
├── tools.py               # System functions
├── prompt_template.py     # Prompt templates
├── runagent.py            # Main entry point
└── little_test.py         # Simplified test code
```

### Workflow

1. **User Input** → Receive user questions
2. **Reasoning Phase** → AI analyzes problems and formulates action plans
3. **Detection Phase** → AI response format correction (handled by AI automatically)
4. **Action Phase** → Execute corresponding tool calls
5. **Observation Phase** → Obtain tool execution results
6. **Loop or End** → Decide whether to continue reasoning or provide final answer based on results

## Installation and Configuration

### Requirements

- Python 3.8+
- Conda environment manager (Python-related commands require environment activation)
- Google API Key
- VPN required for network access

### Environment Variable Configuration

Set in system environment variables:
Google API key can be obtained from https://aistudio.google.com/apikey
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

## Quick Start

### Basic Usage

```bash
conda activate yourenv
python runagent.py
```

### Basic Version Test

```bash
python little_test.py
```

## Configuration Options

### AgentConfig Parameters

```python
class AgentConfig:
    api_key: str                    # Google API Key
    model_name: str                 # Model name (default: "gemini-2.5-flash")
    max_steps: int                  # Maximum reasoning steps (default: 10)
    refresh_prompt_interval: int    # Prompt refresh interval (default: 3)
    project_directory: str          # Project directory (default: "D:/")
    show_system_messages: bool      # Whether to show system messages (default: False)
    conda: str                      # Conda environment name (default: "New")
```

## Advanced Features

### Multi-Tool Collaboration
The Agent supports calling multiple tools in a single action, enabling automated processing of complex tasks.

### Context Management
Automatically manages conversation history and intelligently refreshes context after reaching the set number of rounds to maintain conversation coherence.

### Error Handling
Comprehensive error handling mechanism that can capture tool execution errors and provide feedback to AI for adjustments.

### Security Mechanism
For dangerous system commands, user confirmation is required before execution.

## Development and Extension

### Adding New Tools

1. Define new functions in `tools.py`
2. Add detailed docstrings
3. Tools will be automatically registered in the system

```python
def your_new_tool(param1: str, param2: int) -> str:
    """
    Tool function description
    
    Args:
        param1: Parameter 1 description
        param2: Parameter 2 description
    
    Returns:
        Return value description
    """
    # Implementation code
    return "result"
```

### Custom Configuration

Create custom configuration files to override default settings:

```python
config = AgentConfig()
config.max_steps = 20
config.refresh_prompt_interval = 5
config.show_system_messages = True
```

## Important Notes

1. Ensure Google API Key is properly configured (VPN required for conversations)
2. Some tools require network connection
3. System command execution requires appropriate permissions
4. Conda environment needs to be pre-configured

## Project Structure Details

- **agent.py**: Core ReAct Agent implementation
- **AgentConfig.py**: Configuration management with all adjustable parameters
- **ConversationManager.py**: Conversation history management
- **Toolmanager.py**: Tool registration, parsing, and execution management
- **agent_tools.py**: Implementation of Agent tool functions
- **tools.py**: System function implementation
- **prompt_template.py**: ReAct pattern prompt templates
- **runagent.py**: Main entry point
- **little_test.py**: Simplified version for quick testing

## Acknowledgments

This project is inspired by the following projects and research:

- Thanks to the project tutorial [MarkTechStation/VideoCode](https://github.com/MarkTechStation/VideoCode)
- Thanks to Google Gemini API for providing powerful language model support

If you encounter any issues while using this project or have suggestions for improvement, please feel free to submit an Issue or Pull Request!

## License

This project is open-sourced under the MIT License. Please see the [LICENSE](LICENSE) file for details.

---


