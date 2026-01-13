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
    # --- 关键修改：搜索关键词专攻“竖屏”和“快手” ---
    # 加上 "竖屏" 关键词，B站会优先给手机比例的视频
    url = "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=竖屏短剧+快手+全集&order=click&duration=4"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if 'data' in data and 'result' in data['data']:
            all_videos = data['data']['result']
            
            # 去重逻辑
            seen_ids = load_history()
            new_videos = []
            
            for v in all_videos:
                if v['bvid'] not in seen_ids:
                    new_videos.append(v)
            
            print(f"搜到 {len(all_videos)} 个，去重后剩余 {len(new_videos)} 个")
            
            # 如果去重后太少，就用旧的补一点，保证能刷
            if len(new_videos) < 5:
                final_list = (new_videos + all_videos)[:15]
            else:
                final_list = new_videos[:15]
            
            # 记录历史
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
        title = v['title'].replace('<em class="keyword">','').replace('</em>','').replace('"', "'")
        js_video_list.append({
            "bvid": v['bvid'],
            "title": title,
            "pic": v['pic'] # 把封面图也存下来，用于加载前的占位
        })
    
    js_data = json.dumps(js_video_list, ensure_ascii=False)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>姥姥的短剧台</title>
    <style>
        /* 1. 基础设置：黑色背景，禁止页面多余滚动 */
        html, body {{
            margin: 0;
            padding: 0;
            background-color: #000;
            color: #fff;
            height: 100%;
            overflow: hidden; /* 防止整个页面乱动 */
            font-family: sans-serif;
        }}

        /* 2. 抖音模式的核心容器：使用 Snap Scroll */
        .video-container {{
            height: 100%;
            width: 100%;
            overflow-y: scroll; /* 允许垂直滚动 */
            scroll-snap-type: y mandatory; /* 强制吸附：一滑就整页翻 */
            scroll-behavior: smooth;
        }}

        /* 3. 每一个视频的盒子：强制占满一屏 */
        .video-slide {{
            height: 100%;
            width: 100%;
            scroll-snap-align: start; /* 每次滚动必须停在开头 */
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #000;
        }}

        /* 4. 视频播放器：拉伸占满 */
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
            /* 解决由于B站横屏视频导致的黑边，虽然不能完全消除，但尽量占满 */
            display: block; 
        }}

        /* 5. 提示遮罩：第一次进入提示点击 */
        #start-mask {{
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 999;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-size: 20px;
            color: yellow;
            text-align: center;
        }}
        
        .title-overlay {{
            position: absolute;
            bottom: 60px;
            left: 10px;
            right: 10px;
            color: #fff;
            text-shadow: 1px 1px 2px black;
            font-size: 16px;
            pointer-events: none; /* 让点击穿透，不影响点视频 */
            z-index: 10;
        }}
        
        /* 加载中的占位图 */
        .placeholder {{
            position: absolute;
            width: 100%;
            height: 100%;
            background-size: cover;
            background-position: center;
            opacity: 0.5;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
    </style>
    </head>
    <body>

        <div class="video-container" id="container">
            </div>

        <div id="start-mask" onclick="startApp()">
            <h1>👆 点击屏幕开始看戏</h1>
            <p>像刷抖音一样</p>
            <p>往上划动换台</p>
        </div>

        <script>
            var videoList = {js_data};
            var container = document.getElementById('container');
            
            // 1. 初始化：把所有视频的“坑位”先挖好
            // 我们不直接加载iframe，因为15个iframe会把手机卡死
            // 我们只生成 div，等滑到了再加载 iframe
            videoList.forEach(function(v, index) {{
                var slide = document.createElement('div');
                slide.className = 'video-slide';
                slide.id = 'slide-' + index;
                slide.dataset.bvid = v.bvid; // 把视频ID存在标签里
                
                // 放入封面图和标题
                slide.innerHTML = `
                    <div class="placeholder" style="background-image: url(${{v.pic}})">
                        <span>加载中...</span>
                    </div>
                    <div class="title-overlay">${{v.title}}</div>
                `;
                container.appendChild(slide);
            }});

            // 2. 核心魔法：IntersectionObserver (监视器)
            // 这个东西会盯着屏幕，看哪个视频滑到了屏幕中间
            var observer = new IntersectionObserver(function(entries) {{
                entries.forEach(function(entry) {{
                    var slide = entry.target;
                    var bvid = slide.dataset.bvid;
                    
                    if (entry.isIntersecting) {{
                        // === 视频进入屏幕：开始播放 ===
                        console.log('播放:', bvid);
                        
                        // 创建 iframe
                        var iframe = document.createElement('iframe');
                        // danmaku=0 关闭弹幕
                        // autoplay=1 自动播放
                        iframe.src = "https://player.bilibili.com/player.html?bvid=" + bvid + "&page=1&high_quality=1&danmaku=0&autoplay=1";
                        iframe.allow = "autoplay; fullscreen";
                        
                        // 把它插进去，顶替掉占位符
                        // 为了防止重复插入，先清空
                        // slide.innerHTML = ''; // 不能清空，否则标题没了，只清空placeholder?
                        // 简单粗暴：直接追加 iframe，通过CSS覆盖
                        if (!slide.querySelector('iframe')) {{
                            slide.appendChild(iframe);
                        }}
                        
                    }} else {{
                        // === 视频划出屏幕：销毁 ===
                        // 为了省流量和不串音，滑走的视频直接杀掉
                        var iframe = slide.querySelector('iframe');
                        if (iframe) {{
                            iframe.remove();
                        }}
                    }}
                }});
            }}, {{
                threshold: 0.5 // 只要视频露出50%就算它“进来了”
            }});

            // 3. 启动应用
            function startApp() {{
                document.getElementById('start-mask').style.display = 'none';
                
                // 开始监视所有的坑位
                var slides = document.querySelectorAll('.video-slide');
                slides.forEach(function(slide) {{
                    observer.observe(slide);
                }});
                
                // 自动播放第一个（有的浏览器需要用户先交互一次才能有声自动播放，所以放在点击事件里）
                // 稍微延时一点点让Observer生效
                setTimeout(() => {{
                   // 触发一下滚动让Observer检测到
                   container.scrollTop = 1; 
                   container.scrollTop = 0; 
                }}, 100);
            }}
        </script>
    </body></html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    vids = get_bilibili_videos()
    if vids:
        generate_html(vids)
