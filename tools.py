import json
import re

# 解析AI响应内容，将字符串形式返回转化为json
def fix_string_values(content: str, show_debug: bool = False) -> str:
    """
    修复JSON字符串值中的特殊字符
    只处理字符串值，不影响JSON结构
    """
    # 清理可能的markdown标记
    content = content.strip()
    content = re.sub(r'^```json\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\s*```$', '', content)
    
    if show_debug:
        print(f"清理markdown后: {content[:100]}...")
    
    # 改进的修复方法：只处理明显破坏JSON结构的情况
    # 找到所有字符串值并修复
    def fix_string_value(match):
        key_part = match.group(1)  # "key": "
        value = match.group(2)     # 原始值
        
        original_value = value
        
        # 检查是否已经是正确转义的JSON字符串
        try:
            # 构造一个简单的JSON来测试这个值是否合法
            test_json = f'{{"test": "{value}"}}'
            json.loads(test_json)
            # 如果能解析成功，说明这个值本身是合法的，不需要修复
            return match.group(0)
        except json.JSONDecodeError:
            # 解析失败，需要修复
            pass
        
        # 修复策略：先还原可能的转义，然后重新转义
        fixed_value = value
        
        # 处理最常见的问题：未转义的双引号
        # 但要小心不要破坏已经正确转义的内容
        if '"' in fixed_value and '\\"' not in fixed_value:
            fixed_value = fixed_value.replace('"', '\\"')
        
        # 处理换行符（这是最常见的问题）
        if '\n' in fixed_value:
            fixed_value = fixed_value.replace('\n', '\\n')
        if '\r' in fixed_value:
            fixed_value = fixed_value.replace('\r', '\\r')
        if '\t' in fixed_value:
            fixed_value = fixed_value.replace('\t', '\\t')
        
        # 处理反斜杠（比较复杂，需要小心处理）
        # 只处理单独出现的反斜杠，不处理已经转义的
        fixed_value = re.sub(r'(?<!\\)\\(?!["\\/bfnrtul])', r'\\\\', fixed_value)
        
        if show_debug and original_value != fixed_value:
            print(f"修复字符串: '{original_value[:30]}...' -> '{fixed_value[:30]}...'")
        
        return f'{key_part}{fixed_value}"'
    
    # 更精确的正则表达式，匹配JSON字符串字段
    # 改进版本：支持更多类型的key名称
    pattern = r'("[\w\-_]+"\s*:\s*")([^"]*(?:\\.[^"]*)*)"'
    
    # 多次应用，确保嵌套的情况也能处理
    prev_content = ""
    iteration = 0
    while prev_content != content and iteration < 3:  # 最多3次迭代，避免死循环
        prev_content = content
        content = re.sub(pattern, fix_string_value, content)
        iteration += 1
        if show_debug and prev_content != content:
            print(f"第{iteration}次修复完成")
    
    return content
