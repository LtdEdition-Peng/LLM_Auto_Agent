import subprocess
from typing import List, Dict, Any, Optional



# 简单地读取文件
def read_file(file_path: str) -> str:
    """
    读取指定文件的全部内容
    
    Args:
        file_path (str): 要读取的文件的绝对路径或相对路径，支持各种文本文件格式
                        例如: "D:/example.txt", "/home/user/data.json", "config.ini"
    
    Returns:
        str: 文件的完整文本内容，保持原有的换行符和格式
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# 简单地写文件
def write_to_file(file_path: str, content: str) -> str:
    """
    将指定内容写入文件，如果文件不存在则创建，如果存在则覆盖
    
    Args:
        file_path (str): 目标文件的绝对路径，支持创建新文件
        content (str): 要写入文件的文本内容，支持包含换行符的多行文本
    
    Returns:
        str: 成功时返回 "写入成功"，用于确认操作完成
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.replace("\\n", "\n"))
    return "写入成功"

# 简答地执行系统命令
def run_terminal_command(command: str, level: str = "dangerous") -> Dict[str, Any]:
    """
    执行系统终端命令并返回详细的执行结果，如果指令不危险，请添加 "safe" 级别

    Args:
        command (str): 要执行的终端命令字符串，支持各种系统命令和参数
        level (str): 命令的安全级别，默认为 "dangerous"，可选 "safe" 表示安全命令，高危指令执行前会提示用户确认

    Returns:
        dict: 包含执行结果的字典，根据执行状态返回不同格式
    """
    if level == "dangerous":
        confirm = input(f"警告：即将执行系统命令 '{command}'，请确认是否继续 (y/n): ").strip().lower()
        if confirm != "y":
            return {"status": "aborted", "message": "用户取消执行"}

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True,encoding='utf-8',errors='replace',)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "returncode": e.returncode, "error": e.stderr}
    except Exception as e:
        return {"status": "exception", "error": str(e)}

# 三个网页搜索函数
def search_web(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    使用搜索引擎搜索网络内容
    
    Args:
        query (str): 搜索关键词或问题
        num_results (int): 返回的搜索结果数量，默认为5
        
    Returns:
        dict: 包含搜索结果的字典，包含标题、链接和摘要
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        import urllib.parse
        
        # 使用DuckDuckGo搜索（无需API key）
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        search_results = soup.find_all('div', class_='result')[:num_results]
        
        for result in search_results:
            title_elem = result.find('a', class_='result__a')
            snippet_elem = result.find('a', class_='result__snippet')
            
            if title_elem:
                title = title_elem.get_text().strip()
                link = title_elem.get('href', '')
                snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"搜索失败: {str(e)}"
        }


def fetch_webpage_content(url: str, max_length: int = 2000) -> Dict[str, Any]:
    """
    获取网页内容并提取主要文本
    
    Args:
        url (str): 要获取内容的网页URL
        max_length (int): 返回内容的最大长度，默认2000字符
        
    Returns:
        dict: 包含网页标题和内容的字典
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 移除脚本和样式元素
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.extract()
        
        # 获取标题
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "无标题"
        
        # 获取主要内容
        content_selectors = [
            'article', 'main', '.content', '.post', '.entry',
            'div[class*="content"]', 'div[class*="article"]'
        ]
        
        content_text = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content_text = content_elem.get_text(separator=' ', strip=True)
                break
        
        # 如果没找到特定内容区域，使用body
        if not content_text:
            body = soup.find('body')
            if body:
                content_text = body.get_text(separator=' ', strip=True)
        
        # 限制长度
        if len(content_text) > max_length:
            content_text = content_text[:max_length] + "..."
        
        return {
            "status": "success",
            "url": url,
            "title": title_text,
            "content": content_text,
            "length": len(content_text)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "url": url,
            "error": f"获取网页内容失败: {str(e)}"
        }


def search_and_summarize(query: str, num_results: int = 3) -> Dict[str, Any]:
    """
    搜索网络内容并获取详细信息的组合函数
    
    Args:
        query (str): 搜索查询
        num_results (int): 要深入获取内容的结果数量
        
    Returns:
        dict: 包含搜索结果和详细内容的字典
    """
    try:
        # 先搜索
        search_result = search_web(query, num_results)
        
        if search_result["status"] != "success":
            return search_result
        
        detailed_results = []
        
        # 获取每个搜索结果的详细内容
        for i, result in enumerate(search_result["results"][:num_results]):
            if result["link"]:
                content_result = fetch_webpage_content(result["link"], 1500)
                
                detailed_result = {
                    "rank": i + 1,
                    "title": result["title"],
                    "link": result["link"],
                    "snippet": result["snippet"],
                    "content_status": content_result["status"]
                }
                
                if content_result["status"] == "success":
                    detailed_result["content"] = content_result["content"]
                else:
                    detailed_result["content_error"] = content_result.get("error", "无法获取内容")
                
                detailed_results.append(detailed_result)
        
        return {
            "status": "success",
            "query": query,
            "summary": f"找到 {len(detailed_results)} 个相关结果",
            "results": detailed_results
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"搜索和总结失败: {str(e)}"
        }

# 创建和运行Python文件，默认会使用conda环境，使用此工具前请先创建一个conda环境
def create_and_run_python_file(file_path: str, file_name: str, code: str, conda_env: str = "New", auto_delete: bool = True) -> Dict[str, Any]:
    """
    创建Python文件，写入代码并在指定conda环境中执行
    
    Args:
        file_path (str): 文件保存的目录路径，如 "D:/projects" 或 "."
        file_name (str): Python文件名（不含.py扩展名），如 "data_analysis"
        code (str): 要写入文件的Python代码
        conda_env (str, optional): conda环境名称，默认为"New"
        auto_delete (bool): 是否在执行完成后自动删除文件，默认为True
        
    Returns:
        dict: 包含执行结果的详细信息
    """
    import os
    import tempfile
    import sys
    
    try:
        # 确保文件名以.py结尾
        if not file_name.endswith('.py'):
            file_name += '.py'
        
        # 构建完整文件路径
        full_file_path = os.path.join(file_path, file_name)
        
        # 确保目录存在
        os.makedirs(file_path, exist_ok=True)
        
        # 写入代码到文件（覆盖策略）
        with open(full_file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # 构建执行命令
        if conda_env:
            # 使用conda环境执行
            if os.name == 'nt':  # Windows
                command = f'conda activate {conda_env} && python "{full_file_path}"'
            else:  # Linux/Mac
                command = f'conda activate {conda_env} && python "{full_file_path}"'
        else:
            # 使用当前Python环境执行
            command = f'python "{full_file_path}"'
        
        # 执行文件
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=file_path,  # 设置工作目录
            encoding='utf-8',
            errors='replace',
            timeout=60  # 60秒超时
        )
        
        # 准备返回结果
        execution_result = {
            "status": "success" if result.returncode == 0 else "error",
            "file_path": full_file_path,
            "file_name": file_name,
            "conda_env": conda_env or "current",
            "returncode": result.returncode,
            "output": result.stdout.strip() if result.stdout else "",
            "error": result.stderr.strip() if result.stderr else "",
            "command": command
        }
        
        # 如果有错误输出，添加到结果中
        if result.returncode != 0:
            execution_result["status"] = "error"
            execution_result["error_details"] = f"代码执行失败，返回码: {result.returncode}"
        
        # 处理文件删除逻辑
        if auto_delete:
            try:
                os.remove(full_file_path)
                execution_result["file_deleted"] = True
                execution_result["delete_status"] = "文件已自动删除"
            except Exception as delete_error:
                execution_result["file_deleted"] = False
                execution_result["delete_error"] = f"删除文件失败: {str(delete_error)}"
        else:
            execution_result["file_deleted"] = False
            execution_result["delete_status"] = "文件已保留（根据参数设置）"
        
        return execution_result
        
    except subprocess.TimeoutExpired:
        # 超时情况下也尝试删除文件
        cleanup_result = {}
        if auto_delete and 'full_file_path' in locals():
            try:
                os.remove(full_file_path)
                cleanup_result = {"file_deleted": True, "delete_status": "超时后文件已清理"}
            except:
                cleanup_result = {"file_deleted": False, "delete_status": "超时后文件清理失败"}
        
        return {
            "status": "timeout",
            "error": "代码执行超时（60秒），可能存在无限循环或长时间运行的操作",
            "file_path": full_file_path if 'full_file_path' in locals() else None,
            **cleanup_result
        }
    except FileNotFoundError as e:
        return {
            "status": "error",
            "error": f"文件操作失败: {str(e)}",
            "suggestion": "请检查文件路径是否正确，确保有写入权限"
        }
    except Exception as e:
        # 异常情况下也尝试删除文件
        cleanup_result = {}
        if auto_delete and 'full_file_path' in locals():
            try:
                os.remove(full_file_path)
                cleanup_result = {"file_deleted": True, "delete_status": "异常后文件已清理"}
            except:
                cleanup_result = {"file_deleted": False, "delete_status": "异常后文件清理失败"}
        
        return {
            "status": "exception",
            "error": f"创建或执行Python文件时发生异常: {str(e)}",
            "file_path": full_file_path if 'full_file_path' in locals() else None,
            **cleanup_result
        }

