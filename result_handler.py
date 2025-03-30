#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import tldextract
from urllib.parse import urlparse
from colorama import Fore, Style

# 定义颜色常量
INFO = Fore.CYAN
SUCCESS = Fore.GREEN
WARNING = Fore.YELLOW
ERROR = Fore.RED
HIGHLIGHT = Fore.MAGENTA
RESET = Style.RESET_ALL

class ResultHandler:
    def __init__(self, result_dir="result"):
        """
        初始化结果处理器
        :param result_dir: 结果保存目录
        """
        self.result_dir = result_dir
        self.ensure_result_dir()
        
        # 结果文件路径
        self.domain_file = os.path.join(self.result_dir, "domain.txt")
        self.subdomain_file = os.path.join(self.result_dir, "subdomain.txt")
        self.ip_file = os.path.join(self.result_dir, "ip.txt")
        self.url_file = os.path.join(self.result_dir, "url.txt")
    
    def ensure_result_dir(self):
        """确保结果目录存在"""
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
            print(f"{SUCCESS}[✓] 创建结果目录: {self.result_dir}{RESET}")
    
    def process_results(self, results, verbose=False):
        """
        处理查询结果并保存到对应文件
        :param results: FOFA API返回的结果列表
        :param verbose: 是否输出详细信息
        """
        if not results:
            print(f"{WARNING}[!] 没有结果可处理{RESET}")
            return
        
        # 用于保存所有从result中提取的数据
        all_domains = set()
        all_subdomains = set()
        all_ips = set()
        all_urls = set()
        
        # 从现有文件中加载已有结果
        if verbose:
            print(f"{INFO}[*] 加载已有结果文件...{RESET}")
            
        existing_domains = self.load_existing_results(self.domain_file)
        existing_subdomains = self.load_existing_results(self.subdomain_file)
        existing_ips = self.load_existing_results(self.ip_file)
        existing_urls = self.load_existing_results(self.url_file)
        
        if verbose:
            print(f"{INFO}[*] 已有主域名: {len(existing_domains)}个{RESET}")
            print(f"{INFO}[*] 已有子域名: {len(existing_subdomains)}个{RESET}")
            print(f"{INFO}[*] 已有IP地址: {len(existing_ips)}个{RESET}")
            print(f"{INFO}[*] 已有URL地址: {len(existing_urls)}个{RESET}")
            print(f"{INFO}[*] 开始处理新数据...{RESET}")
        
        # 处理每个结果
        result_count = 0
        for result in results:
            if isinstance(result, list) and len(result) >= 1:
                result_count += 1
                # 第一列作为原始URL
                original_url = result[0]
                all_urls.add(original_url)
                
                # 从URL提取域名和IP信息
                self.extract_domain_and_ip(original_url, all_domains, all_subdomains, all_ips)
                
                # 如果有IP列(第二列)，也添加到IP集合
                if len(result) >= 2 and self.is_valid_ip(result[1]):
                    all_ips.add(result[1])
        
        # 计算重复数据（与已有文件中数据的重复）
        duplicate_domains = all_domains.intersection(existing_domains)
        duplicate_subdomains = all_subdomains.intersection(existing_subdomains)
        duplicate_ips = all_ips.intersection(existing_ips)
        duplicate_urls = all_urls.intersection(existing_urls)
        
        # 计算新数据（在当前结果中有但在已有文件中没有的）
        new_domains = all_domains - existing_domains
        new_subdomains = all_subdomains - existing_subdomains
        new_ips = all_ips - existing_ips
        new_urls = all_urls - existing_urls
        
        # 显示数据统计
        if verbose:
            print(f"{SUCCESS}[✓] 处理完成! 从{result_count}条结果中提取:{RESET}")
            print(f"{SUCCESS}  - 总提取主域名: {len(all_domains)}个{RESET}")
            print(f"{SUCCESS}  - 总提取子域名: {len(all_subdomains)}个{RESET}")
            print(f"{SUCCESS}  - 总提取IP地址: {len(all_ips)}个{RESET}")
            print(f"{SUCCESS}  - 总提取URL地址: {len(all_urls)}个{RESET}")
            print(f"{INFO}[*] 开始合并去重...{RESET}")
        
        # 合并并保存结果
        final_domains = all_domains.union(existing_domains)
        final_subdomains = all_subdomains.union(existing_subdomains)
        final_ips = all_ips.union(existing_ips)
        final_urls = all_urls.union(existing_urls)
        
        self.save_results(self.domain_file, final_domains)
        self.save_results(self.subdomain_file, final_subdomains)
        self.save_results(self.ip_file, final_ips)
        self.save_results(self.url_file, final_urls)
        
        # 显示重复统计和最终结果
        if verbose:
            print(f"{WARNING}[!] 重复数据统计 (与已有文件重复):{RESET}")
            print(f"{WARNING}  - 重复主域名: {len(duplicate_domains)}个{RESET}")
            print(f"{WARNING}  - 重复子域名: {len(duplicate_subdomains)}个{RESET}")
            print(f"{WARNING}  - 重复IP地址: {len(duplicate_ips)}个{RESET}")
            print(f"{WARNING}  - 重复URL地址: {len(duplicate_urls)}个{RESET}")
            
            print(f"{SUCCESS}[+] 新增数据统计:{RESET}")
            print(f"{SUCCESS}  - 新增主域名: {len(new_domains)}个{RESET}")
            print(f"{SUCCESS}  - 新增子域名: {len(new_subdomains)}个{RESET}")
            print(f"{SUCCESS}  - 新增IP地址: {len(new_ips)}个{RESET}")
            print(f"{SUCCESS}  - 新增URL地址: {len(new_urls)}个{RESET}")
            
            print(f"{HIGHLIGHT}[✓] 最终结果统计:{RESET}")
            print(f"{HIGHLIGHT}  - 总主域名: {len(final_domains)}个{RESET}")
            print(f"{HIGHLIGHT}  - 总子域名: {len(final_subdomains)}个{RESET}")
            print(f"{HIGHLIGHT}  - 总IP地址: {len(final_ips)}个{RESET}")
            print(f"{HIGHLIGHT}  - 总URL地址: {len(final_urls)}个{RESET}")
            print(f"{SUCCESS}[✓] 结果已保存到 {self.result_dir} 目录{RESET}")
    
    def is_valid_ip(self, ip_str):
        """检查是否为有效的IP地址"""
        return re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_str) is not None
    
    def extract_domain_and_ip(self, item, domains, subdomains, ips):
        """
        从URL提取域名和IP信息
        :param item: URL或主机名
        :param domains: 主域名集合
        :param subdomains: 子域名集合
        :param ips: IP地址集合
        """
        # 检查是否为IP地址
        if self.is_valid_ip(item):
            ips.add(item)
            return
            
        # 检查是否为IP:PORT格式
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$', item):
            ip = item.split(':')[0]
            ips.add(ip)
            return
            
        # 构建URL并提取域名
        if '://' not in item:
            parsed_url = urlparse(f"http://{item}")
        else:
            parsed_url = urlparse(item)
        
        # 提取域名信息
        netloc = parsed_url.netloc
        if ':' in netloc:
            netloc = netloc.split(':')[0]
            
        # 使用tldextract准确提取域名各部分
        extracted = tldextract.extract(netloc)
        
        # 如果没有提取到有效的域名部分，则跳过
        if not extracted.domain or not extracted.suffix:
            return
            
        # 构建主域名和子域名
        main_domain = f"{extracted.domain}.{extracted.suffix}"
        
        if extracted.subdomain:
            full_domain = f"{extracted.subdomain}.{main_domain}"
            domains.add(main_domain)
            subdomains.add(full_domain)
        else:
            domains.add(main_domain)
    
    def load_existing_results(self, file_path):
        """
        加载现有结果文件
        :param file_path: 文件路径
        :return: 结果集合
        """
        results = set()
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            results.add(line)
            except Exception as e:
                print(f"{ERROR}[✗] 读取文件 {file_path} 失败: {str(e)}{RESET}")
        return results
    
    def save_results(self, file_path, results):
        """
        保存结果到文件
        :param file_path: 文件路径
        :param results: 结果集合
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for result in sorted(results):
                    f.write(f"{result}\n")
        except Exception as e:
            print(f"{ERROR}[✗] 保存文件 {file_path} 失败: {str(e)}{RESET}") 