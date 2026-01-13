import requests
import datetime
import json
import os

# 历史记录文件（机器人的小本本）
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
    # 只保留最近的 500 条记录，防止文件无限变大
    if len(history_list) > 500:
        history_list = history_list[-500:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_list, f)

def get_bilibili_videos():
    # 既然要防重复，我们要多抓一点视频来筛选（抓50个）
    url = "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=短剧全集+一口气看完&order=click&duration=4"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if 'data' in data and 'result' in data['data']:
            all_videos = data['data']['result'] # 获取搜到的所有视频
            
            # --- 去重逻辑开始 ---
            seen_ids = load_history() # 读取历史
            new_videos = []
            
            for v in all_videos:
                if v['bvid'] not in seen_ids:
                    new_videos.append(v)
            
            print(f"搜到 {len(all_videos)} 个，去重后剩余 {len(new_videos)} 个")
            
            # 如果去重后不够15个，就拿旧的凑数（防止开天窗），但优先用新的
            if len(new_videos) < 15:
                return (new_videos + all_videos)[:15]
            
            # 取前15个最新鲜的
            final_list = new_videos[:15]
            
            # 把这15个记入小本本
            for v in final_list:
                seen_ids.append(v['bvid'])
            save_history(seen_ids)
            
            return final_list
            # --- 去重逻辑结束 ---
            
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
        .btn-next {{ background-color: #ffff00; color: #000; font-size: 1.6rem; }}
    </style>
    </head>
    <body>
        <div class="header">📅 今日新剧 ({today_str})</div>
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
            
            function loadMemory() {{
                var savedIndex = localStorage.getItem('grandma_tv_index');
                var savedDate = localStorage.getItem('grandma_tv_date');
                var todayDate = "{today_str}";
                if (savedDate === todayDate && savedIndex !== null) {{
                    currentIndex = parseInt(savedIndex);
                    if (currentIndex >= playlist.length) currentIndex = 0;
                }} else {{
                    currentIndex = 0;
                    localStorage.setItem('grandma_tv_date', todayDate);
                }}
            }}

            function saveMemory() {{
                localStorage.setItem('grandma_tv_index', currentIndex);
            }}

            function loadVideo(index) {{
                var video = playlist[index];
                document.getElementById('tv-title').innerText = (index + 1) + ". " + video.title;
                
                // 【核心修改】danmaku=0 关闭弹幕
                var src = "https://player.bilibili.com/player.html?bvid=" + video.bvid + "&page=1&high_quality=1&autoplay=1&danmaku=0";
                document.getElementById('tv-screen').src = src;
                
                saveMemory();
            }}

            function changeChannel(direction) {{
                var newIndex = currentIndex + direction;
                if (newIndex >= playlist.length) newIndex = 0;
                if (newIndex < 0) newIndex = playlist.length - 1;
                currentIndex = newIndex;
                loadVideo(currentIndex);
            }}

            window.onload = function() {{
                if (playlist.length > 0) {{
                    loadMemory();
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
