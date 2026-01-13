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
    # 关键词优化：找竖屏、快手风格、高播放量的短剧
    url = "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=竖屏短剧+快手+全集&order=click&duration=4"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if 'data' in data and 'result' in data['data']:
            all_videos = data['data']['result']
            seen_ids = load_history()
            new_videos = []
            
            for v in all_videos:
                if v['bvid'] not in seen_ids:
                    new_videos.append(v)
            
            # 如果不够5个，拿旧的凑数，保证能滑
            if len(new_videos) < 5:
                final_list = (new_videos + all_videos)[:15]
            else:
                final_list = new_videos[:15]
            
            # 存入历史
            for v in final_list:
                seen_ids.append(v['bvid'])
            save_history(seen_ids)
            
            return final_list
        else:
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(videos):
    js_video_list = []
    for v in videos:
        # 清理标题里的乱码
        title = v['title'].replace('<em class="keyword">','').replace('</em>','').replace('"', "'")
        js_video_list.append({
            "bvid": v['bvid'],
            "title": title,
            "pic": "https:" + v['pic'] if v['pic'].startswith('//') else v['pic']
        })
    
    js_data = json.dumps(js_video_list, ensure_ascii=False)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>姥姥的电视</title>
    <style>
        html, body {{
            margin: 0; padding: 0; background-color: #000;
            color: #fff; height: 100%; overflow: hidden;
            font-family: sans-serif;
        }}
        .video-container {{
            height: 100%; width: 100%;
            overflow-y: scroll;
            scroll-snap-type: y mandatory; /* 强制吸附，一滑一格 */
            -webkit-overflow-scrolling: touch;
        }}
        .video-slide {{
            height: 100%; width: 100%;
            scroll-snap-align: start;
            position: relative;
            display: flex; justify-content: center; align-items: center;
            background: #000;
        }}
        iframe {{
            width: 100%; height: 100%; border: none; display: block;
        }}
        .placeholder {{
            position: absolute; width: 100%; height: 100%;
            background-size: cover; background-position: center;
            display: flex; justify-content: center; align-items: center;
            z-index: 1;
        }}
        .loading-text {{
            background: rgba(0,0,0,0.5); padding: 10px 20px; border-radius: 20px;
        }}
        /* 简单的标题遮罩，显示在视频下方 */
        .title-bar {{
            position: absolute; bottom: 40px; left: 10px; right: 10px;
            z-index: 10; font-size: 16px; text-shadow: 1px 1px 2px #000;
            pointer-events: none; opacity: 0.8;
        }}
    </style>
    </head>
    <body>

        <div class="video-container" id="container"></div>

        <script>
            var videoList = {js_data};
            var container = document.getElementById('container');
            
            // 1. 生成所有视频坑位
            videoList.forEach(function(v, index) {{
                var slide = document.createElement('div');
                slide.className = 'video-slide';
                slide.id = 'slide-' + index;
                slide.dataset.bvid = v.bvid;
                
                // 默认显示封面图，不仅好看，还能省流量
                slide.innerHTML = `
                    <div class="placeholder" style="background-image: url('${{v.pic}}')">
                        <div class="loading-text">即将播放...</div>
                    </div>
                    <div class="title-bar">${{v.title}}</div>
                `;
                container.appendChild(slide);
            }});

            // 2. 核心：IntersectionObserver 自动检测滑动
            var observer = new IntersectionObserver(function(entries) {{
                entries.forEach(function(entry) {{
                    var slide = entry.target;
                    var bvid = slide.dataset.bvid;
                    
                    if (entry.isIntersecting) {{
                        // === 滑到了这个视频：立刻加载并播放 ===
                        console.log('加载视频:', bvid);
                        
                        // 只有当这里没有iframe时才创建，防止重复刷新
                        if (!slide.querySelector('iframe')) {{
                            var iframe = document.createElement('iframe');
                            // 核心参数：
                            // autoplay=1 : 试图自动播放
                            // danmaku=0 : 关弹幕
                            // high_quality=1 : 高画质
                            iframe.src = "https://player.bilibili.com/player.html?bvid=" + bvid + "&page=1&high_quality=1&danmaku=0&autoplay=1";
                            iframe.allow = "autoplay; fullscreen";
                            
                            // 稍微延时一点点插入，让滑动更顺滑
                            setTimeout(() => {{
                                slide.appendChild(iframe);
                                // 隐藏封面图
                                var ph = slide.querySelector('.placeholder');
                                if(ph) ph.style.display = 'none';
                            }}, 300);
                        }}
                        
                    }} else {{
                        // === 滑走了：立刻销毁 ===
                        var iframe = slide.querySelector('iframe');
                        if (iframe) {{
                            iframe.remove(); // 拔掉电源，声音立马停，省电
                            var ph = slide.querySelector('.placeholder');
                            if(ph) ph.style.display = 'flex'; // 恢复封面
                        }}
                    }}
                }});
            }}, {{
                threshold: 0.5 // 露出50%就开始播
            }});

            // 3. 页面一加载，立刻开始监视
            window.onload = function() {{
                var slides = document.querySelectorAll('.video-slide');
                slides.forEach(function(slide) {{
                    observer.observe(slide);
                }});
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
