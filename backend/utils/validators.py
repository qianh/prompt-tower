import re
from pathlib import Path
from typing import List


def validate_title(title: str) -> bool:
    """验证标题格式"""
    if not title or len(title) < 1 or len(title) > 100:
        return False
    # 标题只允许字母、数字、中文、下划线、连字符和空格
    pattern = r"^[\w\s\-\u4e00-\u9fa5]+$"
    return bool(re.match(pattern, title))


def validate_tags(tags: List[str]) -> bool:
    """验证标签列表"""
    if not isinstance(tags, list):
        return False
    for tag in tags:
        if not tag or len(tag) > 20:
            return False
        # 标签只允许字母、数字、中文、下划线、连字符
        pattern = r"^[\w\-\u4e00-\u9fa5]+$"
        if not re.match(pattern, tag):
            return False
    return True


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    # 移除路径分隔符和其他不安全字符
    unsafe_chars = ["/", "\\", "..", "~", "|", ":", "*", "?", '"', "<", ">", "\n", "\r"]
    for char in unsafe_chars:
        filename = filename.replace(char, "")
    return filename.strip()


def validate_content(content: str) -> bool:
    """验证内容"""
    if not content or len(content) < 1:
        return False
    # 内容最大长度限制为10000字符
    if len(content) > 10000:
        return False
    return True


def is_safe_path(path: Path, base_path: Path) -> bool:
    """检查路径是否安全（防止路径遍历攻击）"""
    try:
        # 解析为绝对路径
        resolved_path = path.resolve()
        resolved_base = base_path.resolve()
        # 检查是否在基础路径内
        return resolved_path.is_relative_to(resolved_base)
    except Exception:
        return False
