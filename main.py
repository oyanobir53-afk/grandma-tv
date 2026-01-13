import requests
import datetime
import json

def get_bilibili_videos():
    # --- 核心修改在这里 ---
    # 关键词： "短剧全集" + "一口气看完" -> 确保是剧情合集
    # order=click -> 按点击量排序（保证是大家爱看的热门剧）
    # duration=4 -> 必须是60分钟以上的长视频
    url = "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=短剧全集+一口气看完&order=click&duration=4"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if 'data' in data and 'result' in data['data']:
            video_list = data['data']['result']
            return video_list[:20] # 取前20个最火的
        else:
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(videos):
    # 针对姥姥优化的：黑底、黄字（高对比度）、超大字体
    html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>姥姥的电视</title>
    <style>
        /* 页面背景全黑，保护眼睛，突出内容 */
        body { background-color: #000000; color: #ffff00; font-family: sans-serif; margin: 0; padding: 15px; }
        
        h1 { text-align: center; font-size: 2.5rem; margin-bottom: 30px; color: #fff; border-bottom: 2px solid #333; padding-bottom: 10px;}
        
        /* 每一个视频的大卡片 */
        .card { 
            display: block; 
            background: #1a1a1a; 
            margin-bottom: 50px; /* 卡片间距拉大，防止误触 */
            border: 4px solid #444; 
            text-decoration: none; 
            color: #f1c40f; /* 亮黄色字体 */
            border-radius: 25px;
            overflow: hidden;
        }
        
        /* 封面图撑满 */
        .card img { width: 100%; height: auto; display: block; opacity: 0.9; }
        
        .info { padding: 30px; }
        
        /* 标题字号极大 */
        .title { font-size: 2.2rem; font-weight: bold; line-height: 1.4; margin-bottom: 20px; color: #fff;}
        
        /* 辅助信息 */
        .time { font-size: 1.4rem; color: #aaa; }
        
        /* 底部提示 */
        .footer { text-align: center; color: #555; margin-top: 50px; font-size: 1.2rem; }
    </style>
    </head>
    <body>
        <h1>📺 今日好剧推荐</h1>
    """
    
    if not videos:
        html += "<p style='font-size:2rem;text-align:center;'>今日暂无更新，请稍后再试。</p>"
    
    for v in videos:
        # 点击跳转链接
        link = f"https://m.bilibili.com/video/{v['bvid']}"
        # 清理标题里的HTML标签
        title = v['title'].replace('<em class="keyword">','').replace('</em>','')
        # 封面图处理
        pic = v['pic']
        if not pic.startswith("http"): pic = "https:" + pic
        
        # 格式化时间，把 "duration" (比如 "120:00") 显示出来
        duration_str = v.get('duration', '')
        
        html += f"""
        <a href="{link}" class="card">
            <img src="{pic}" alt="封面">
            <div class="info">
                <div class="title">{title}</div>
                <div class="time">🕒 时长: {duration_str} | 🔥 很多人在看</div>
            </div>
        </a>
        """
        
    html += f"""
        <div class="footer">自动更新时间: {datetime.datetime.now().strftime("%Y-%m-%d")}</div>
    </body></html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    vids = get_bilibili_videos()
    if vids:
        generate_html(vids)
        print("网页已生成")
    else:
        print("未抓取到视频")
