#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import json
import time
import requests
from config import FOFA_API_KEY, REQUEST_INTERVAL, MAX_RETRIES

class FofaAPI:
    def __init__(self):
        self.key = FOFA_API_KEY
        self.base_url = "https://fofa.info/api/v1/search/all"
        self.interval = REQUEST_INTERVAL
        self.max_retries = MAX_RETRIES
        
    def query(self, query_str, size=10000, fields="host,ip,port"):
        """
        执行FOFA查询
        :param query_str: 查询语句
        :param size: 返回结果数量
        :param fields: 返回字段
        :return: 查询结果
        """
        encoded_query = base64.b64encode(query_str.encode()).decode()
        params = {
            'key': self.key,
            'qbase64': encoded_query,
            'size': size,
            'fields': fields
        }
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get('error'):
                    print(f"查询错误: {data.get('errmsg')}")
                    return None
                
                return data.get('results', [])
            except Exception as e:
                print(f"查询失败 (尝试 {attempt+1}/{self.max_retries+1}): {str(e)}")
                if attempt < self.max_retries:
                    time.sleep(self.interval)
                else:
                    print("达到最大重试次数，放弃查询")
                    return None
            
            time.sleep(self.interval)
        
        return None 