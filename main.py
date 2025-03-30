#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
from fofa_api import FofaAPI
from result_handler import ResultHandler
from config import FOFA_API_KEY, REQUEST_INTERVAL
from colorama import init, Fore, Back, Style

# 初始化colorama
init(autoreset=True)

# 定义颜色常量
INFO = Fore.CYAN
SUCCESS = Fore.GREEN
WARNING = Fore.YELLOW
ERROR = Fore.RED
HIGHLIGHT = Fore.MAGENTA
DEBUG = Fore.BLUE
RESET = Style.RESET_ALL

def print_banner():
    """打印程序横幅"""
    banner = f"""
{Fore.CYAN}┌───────────────────────────────────────┐
{Fore.CYAN}│       {Fore.GREEN}FOFA API 信息收集工具{Fore.CYAN}            │
{Fore.CYAN}│       {Fore.YELLOW}批量查询 · 信息收集 · 结果去重{Fore.CYAN}    │
{Fore.CYAN}└───────────────────────────────────────┘{RESET}
"""
    print(banner)

def check_config():
    """检查配置是否有效"""
    print(f"{INFO}[*] 检查配置信息...{RESET}")
    if not FOFA_API_KEY:
        print(f"{ERROR}[✗] FOFA_API_KEY 未配置！{RESET}")
        print(f"{INFO}[i] 请在 config.py 文件中配置您的 FOFA API KEY。{RESET}")
        return False
    print(f"{SUCCESS}[✓] 配置检查通过{RESET}")
    return True

def read_file_lines(file_path):
    """读取文件内容，每行作为一个元素返回"""
    if not os.path.exists(file_path):
        print(f"{ERROR}[✗] 文件不存在: {file_path}{RESET}")
        print(f"{INFO}[i] 当前工作目录: {os.getcwd()}{RESET}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            print(f"{SUCCESS}[✓] 成功读取文件，共 {len(lines)} 行有效内容{RESET}")
            return lines
    except Exception as e:
        print(f"{ERROR}[✗] 读取文件失败: {str(e)}{RESET}")
        return []

def process_single_query(query_str):
    """处理单条查询"""
    print(f"\n{HIGHLIGHT}[→] 执行查询: {query_str}{RESET}")
    
    fofa = FofaAPI()
    handler = ResultHandler()
    
    print(f"{INFO}[*] 正在发送查询请求...{RESET}")
    results = fofa.query(query_str)
    if results:
        print(f"{SUCCESS}[✓] 查询成功! 共获取到 {len(results)} 条结果{RESET}")
        print(f"{INFO}[*] 开始处理结果数据...{RESET}")
        handler.process_results(results, verbose=True)
    else:
        print(f"{ERROR}[✗] 查询未返回任何结果{RESET}")

def process_batch_query(field, file_path):
    """处理批量查询
    :param field: 查询字段，例如 'org'
    :param file_path: 包含多个查询值的文件路径
    """
    print(f"\n{HIGHLIGHT}[→] 批量查询模式{RESET}")
    print(f"{INFO}[*] 尝试从文件加载查询: {file_path}{RESET}")
    
    # 尝试不同的路径组合
    possible_paths = [
        file_path,                                      # 原始路径
        os.path.join(os.getcwd(), file_path),           # 从当前工作目录
        os.path.abspath(file_path)                      # 绝对路径
    ]
    
    file_found = False
    actual_path = None
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isfile(path):
            file_found = True
            actual_path = path
            print(f"{SUCCESS}[✓] 找到文件: {actual_path}{RESET}")
            break
    
    if not file_found:
        print(f"{ERROR}[✗] 批量查询文件不存在，请检查文件路径:{RESET}")
        for path in possible_paths:
            print(f"{INFO}  - 尝试路径: {path}{RESET}")
        print(f"{INFO}[i] 请确保文件存在并且路径正确。{RESET}")
        return
    
    lines = read_file_lines(actual_path)
    if not lines:
        print(f"{ERROR}[✗] 批量查询文件为空{RESET}")
        return
    
    print(f"{SUCCESS}[✓] 从文件 '{actual_path}' 中加载了 {len(lines)} 条数据{RESET}")
    
    fofa = FofaAPI()
    handler = ResultHandler()
    
    total_results = 0
    successful_queries = 0
    
    for i, line in enumerate(lines, 1):
        # 构造正确的FOFA查询语句，使用双引号包裹查询值
        query = f'{field}="{line}"'
        print(f"\n{HIGHLIGHT}[{i}/{len(lines)}] 查询: {query}{RESET}")
        
        print(f"{INFO}[*] 正在发送查询请求...{RESET}")
        results = fofa.query(query)
        if results:
            count = len(results)
            total_results += count
            successful_queries += 1
            print(f"{SUCCESS}[✓] 查询成功! 获取到 {count} 条结果{RESET}")
            print(f"{INFO}[*] 开始处理结果数据...{RESET}")
            handler.process_results(results, verbose=True)
        else:
            print(f"{ERROR}[✗] 查询 '{query}' 未返回任何结果{RESET}")
        
        if i < len(lines):
            wait_time = REQUEST_INTERVAL
            print(f"{INFO}[*] 等待 {wait_time} 秒后进行下一次查询...{RESET}")
            # 倒计时显示
            for remaining in range(wait_time, 0, -1):
                sys.stdout.write(f"\r{INFO}[*] 倒计时: {remaining}秒{RESET}")
                sys.stdout.flush()
                time.sleep(1)
            print("\r" + " " * 30 + "\r", end="")  # 清除倒计时行
    
    # 批量查询完成，显示统计信息
    print(f"\n{HIGHLIGHT}{'='*50}{RESET}")
    print(f"{HIGHLIGHT}[✓] 批量查询完成!{RESET}")
    print(f"{SUCCESS}[i] 总查询数: {len(lines)}{RESET}")
    print(f"{SUCCESS}[i] 成功查询数: {successful_queries}{RESET}")
    print(f"{SUCCESS}[i] 总结果数: {total_results}{RESET}")
    print(f"{HIGHLIGHT}{'='*50}{RESET}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="FOFA API 信息收集工具")
    parser.add_argument("query", help="查询语句或文件路径 (如: domain=example.com 或 org=info.txt)")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 检查配置
    if not check_config():
        return
    
    query = args.query.strip()
    
    if args.debug:
        print(f"{DEBUG}[DEBUG] 查询参数: {query}{RESET}")
        print(f"{DEBUG}[DEBUG] 当前工作目录: {os.getcwd()}{RESET}")
    
    # 判断是单条查询还是批量查询
    if "=" in query:
        field, value = query.split("=", 1)
        
        if args.debug:
            print(f"{DEBUG}[DEBUG] 字段: {field}, 值: {value}{RESET}")
        
        # 检查是否是批量查询（值为文件路径且文件可能存在）
        if value.endswith(".txt"):
            # 尝试批量查询
            process_batch_query(field, value)
        else:
            # 单条查询，重新构造完整的查询语句
            # 如果值未被引号包裹，则自动添加双引号
            if not (value.startswith('"') and value.endswith('"')):
                query = f'{field}="{value}"'
            process_single_query(query)
    else:
        # 没有使用'='的查询直接传递
        process_single_query(query)

if __name__ == "__main__":
    main() 