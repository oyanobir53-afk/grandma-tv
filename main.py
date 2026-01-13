import requests
import datetime
import json
import os

# 历史记录文件
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history_list):
    if len(history_list) > 500:
        history_list = history_list[-500:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_list, f)

def get_bilibili_videos():
    # --- 修改 1: 搜索关键词更“俗”更直接 ---
    # 加上 "逆袭"、"霸总"、"言情"，这样出来的绝对是剧情，不是教程
    # 加上 "一口气" 确保是合集，不是几秒钟的预告
    url = "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=竖屏短剧+一口气+逆袭&order=click&duration=4"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # --- 修改 2: 定义“黑名单” (垃圾词库) ---
    # 凡是标题里有这些词的，统统不要
    blacklist_words = [
        "教程", "运镜", "拍摄", "剪辑", "教学", "实操", "变现", "赚钱", 
        "分析", "解说", "花絮", "预告", "素材", "摄影", "文案", "怎么做", "第一集"
    ]
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if 'data' in data and 'result' in data['data']:
            all_videos = data['data']['result']
            seen_ids = load_history()
            new_videos = []
            
            for v in all_videos:
                title = v['title']
                
                # --- 核心过滤逻辑 ---
                # 1. 检查是不是看过的
                if v['bvid'] in seen_ids:
                    continue
                
                # 2. 检查有没有黑名单词汇 (最关键的一步)
                is_garbage = False
                for bad_word in blacklist_words:
                    if bad_word in title:
                        is_garbage = True
                        break
                if is_garbage:
                    continue # 如果是垃圾词，直接跳过，看下一个
                
                # 3. 只有通过了层层筛选的，才算合格的剧
                new_videos.append(v)
            
            # 这里的逻辑不变：不够就凑数，存历史
            if len(new_
