import requests
import datetime
import json

def get_bilibili_videos():
    # 保持搜索逻辑不变
    url = "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=短剧全集+一口气看完&order=click&duration=4"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if 'data' in data and 'result' in data['data']:
            return data['data']['result'][:10] # 为了页面流畅，只取前10个
        else:
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(videos):
    html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>姥姥的电视</title>
    <style>
        body { background-color: #000000; color: #ffff00; font-family: sans-serif; margin: 0; padding: 10px; }
        h1 { text-align: center; font-size: 2rem; margin-bottom: 20px; color: #fff; }
        
        .card { 
            background: #1a1a1a; 
            margin-bottom: 40px; 
            border: 2px solid #333; 
            border-radius: 15px;
            overflow: hidden;
            padding-bottom: 10px;
        }
        
        /* 视频容器，确保比例正确 */
        .video-container {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%; /* 16:9 比例 */
            height: 0;
            background: #000;
        }
        
        .video-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0;
        }
        
        .title { 
            font-size: 1.5rem; 
            font-weight: bold; 
            padding: 15px; 
            color: #fff;
            line-height: 1.3;
        }
    </style>
    </head>
    <body>
        <h1>📺 今日推荐</h1>
    """
    
    for v in videos:
        # 这里的 bvid 就是视频的身份证
        bvid = v['bvid']
        title = v['title'].replace('<em class="keyword">','').replace('</em>','')
        
        # 嵌入代码核心：
        # high_quality=1 (尝试高画质)
        # danmaku=0 (关闭弹幕，防止遮挡)
        # autoplay=0 (不自动播放，省流量)
        iframe_src = f"https://player.bilibili.com/player.html?bvid={bvid}&page=1&high_quality=1&danmaku=0&autoplay=0"
        
        html += f"""
        <div class="card">
            <div class="video-container">
                <iframe src="{iframe_src}" allowfullscreen="true"></iframe>
            </div>
            <div class="title">{title}</div>
        </div>
        """
        
    html += f"""
        <p style="text-align:center;color:#666;margin-top:30px">
            更新时间: {datetime.datetime.now().strftime("%Y-%m-%d")}
        </p>
    </body></html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    vids = get_bilibili_videos()
    if vids:
        generate_html(vids)
