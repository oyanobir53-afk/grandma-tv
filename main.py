import requests
import datetime
import json

def get_bilibili_videos():
    # 保持抓取逻辑，抓取最新的热门短剧
    url = "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=短剧全集+一口气看完&order=click&duration=4"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if 'data' in data and 'result' in data['data']:
            return data['data']['result'][:20] # 抓20个，管够看一天
        else:
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(videos):
    js_video_list = []
    for v in videos:
        title = v['title'].replace('<em class="keyword">','').replace('</em>','').replace('"', "'")
        js_video_list.append({
            "bvid": v['bvid'],
            "title": title
        })
    
    js_data = json.dumps(js_video_list, ensure_ascii=False)
    
    # 获取当前日期，用于判断列表是否更新了
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>姥姥的电视</title>
    <style>
        body {{ background-color: #000; color: #fff; font-family: sans-serif; margin: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
        .header {{ height: 8%; display: flex; align-items: center; justify-content: center; font-size: 1rem; color: #888; background: #111; }}
        .screen-container {{ flex: 1; width: 100%; background: #000; position: relative; }}
        iframe {{ width: 100%; height: 100%; border: none; }}
        
        .video-info {{ height: 12%; padding: 0 15px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 1.1rem; color: #ffff00; font-weight: bold; background: #1a1a1a; border-bottom: 1px solid #333; }}
        
        .controls {{ height: 20%; display: flex; gap: 10px; padding: 10px; box-sizing: border-box; background: #000; }}
        .btn {{ flex: 1; border: none; border-radius: 10px; font-size: 1.4rem; font-weight: bold; display: flex; align-items: center; justify-content: center; }}
        .btn-prev {{ background-color: #333; color: #ccc; }}
        .btn-next {{ background-color: #ffff00; color: #000; font-size: 1.6rem; }} /* 下一个按钮更大更亮 */
    </style>
    </head>
    <body>

        <div class="header">📅 今日节目单 ({today_str})</div>

        <div class="screen-container">
            <iframe id="tv-screen" src="" allowfullscreen="true" allow="autoplay"></iframe>
        </div>

        <div class="video-info" id="tv-title">正在加载...</div>

        <div class="controls">
            <button class="btn btn-prev" onclick="changeChannel(-1)">上一个</button>
            <button class="btn btn-next" onclick="changeChannel(1)">下一个 ▶️</button>
        </div>

        <script>
            var playlist = {js_data};
            var currentIndex = 0;
            
            // 【核心功能】读取记忆
            function loadMemory() {{
                var savedIndex = localStorage.getItem('grandma_tv_index');
                var savedDate = localStorage.getItem('grandma_tv_date');
                var todayDate = "{today_str}";

                // 如果是同一天，就恢复进度
                if (savedDate === todayDate && savedIndex !== null) {{
                    currentIndex = parseInt(savedIndex);
                    // 防止记录的索引超出了今天的列表长度
                    if (currentIndex >= playlist.length) currentIndex = 0;
                }} else {{
                    // 如果是新的一天，重置为0，并更新日期
                    currentIndex = 0;
                    localStorage.setItem('grandma_tv_date', todayDate);
                }}
            }}

            // 【核心功能】保存记忆
            function saveMemory() {{
                localStorage.setItem('grandma_tv_index', currentIndex);
            }}

            function loadVideo(index) {{
                var video = playlist[index];
                document.getElementById('tv-title').innerText = (index + 1) + ". " + video.title;
                
                // 拼接B站播放器链接
                // t=0 从头播放
                var src = "https://player.bilibili.com/player.html?bvid=" + video.bvid + "&page=1&high_quality=1&autoplay=1";
                document.getElementById('tv-screen').src = src;
                
                // 每次换台都保存一下进度
                saveMemory();
            }}

            function changeChannel(direction) {{
                var newIndex = currentIndex + direction;
                if (newIndex >= playlist.length) newIndex = 0; // 循环到底回开头
                if (newIndex < 0) newIndex = playlist.length - 1;
                currentIndex = newIndex;
                loadVideo(currentIndex);
            }}

            window.onload = function() {{
                if (playlist.length > 0) {{
                    loadMemory(); // 网页一打开，先读记忆
                    loadVideo(currentIndex);
                }}
            }};
        </script>
    </body></html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    vids = get_bilibili_videos()
    if vids:
        generate_html(vids)
