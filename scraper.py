import re
import time
import csv
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

import logging

def fetch_playlist_html(playlist_id, max_scroll_attempts=3):
    PLAYLIST_URL = f"https://www.youtube.com/playlist?list={playlist_id}"
    print(f"Fetching playlist HTML from: {PLAYLIST_URL}", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-setuid-sandbox"
        ])
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        page.goto(PLAYLIST_URL, timeout=60000)
        page.wait_for_selector('ytd-playlist-video-renderer', timeout=120000)

        # 初始化影片計數與嘗試次數
        previous_video_count = len(page.query_selector_all('#content ytd-playlist-video-renderer'))
        scroll_attempts = 0

                # 立即顯示第一次載入的 HTML
        print(f"\n\n[HTML SNAPSHOT]", flush=True)
        print(page.content(), flush=True)  # 只顯示前 1000 字元
        print("\n[...HTML END...]\n\n", flush=True)

        while scroll_attempts < max_scroll_attempts:
            print(f"正在嘗試第 {scroll_attempts + 1} 次滾動...", flush=True)
            # 滾動到底部
            page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            
            # 確認高度是否有變化
            new_height = page.evaluate("document.documentElement.scrollHeight")
            print(f"頁面高度: {new_height}", flush=True)

            # 檢查新的影片是否加載進來
            current_video_count = len(page.query_selector_all('#content ytd-playlist-video-renderer'))
            print(f"目前影片數量: {current_video_count}", flush=True)
            
            if current_video_count == previous_video_count:
                scroll_attempts += 1
                print(f"沒有載入新影片，第 {scroll_attempts} 次嘗試失敗...", flush=True)
            else:
                scroll_attempts = 0  # 如果有新資料，重置計數
                print(f"沒有載入新影片，第 {scroll_attempts} 次嘗試失敗...", flush=True)
            
            previous_video_count = current_video_count

        print("完成所有滾動動作，開始擷取 HTML...", flush=True)
        html = page.content()
        browser.close()
    return html

def extract_video_details_from_html(html):
    pattern = r'<div id="meta" class="style-scope ytd-playlist-video-renderer">.*?<h3.*?aria-label="(.*?)".*?<a.*?href="(/watch\?v=[^&]+).*?</a>.*?</h3>'
    matches = re.findall(pattern, html, re.DOTALL)

    video_details = []
    for title, href in matches:
        video_id = href.split('=')[1]
        video_url = f"https://www.youtube.com{href}"
        start = end = None
        match_range = re.search(r"第(\d+)~(\d+)集", title)
        if match_range:
            start, end = int(match_range.group(1)), int(match_range.group(2))

        video_details.append({
            "log_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id": video_id,
            "start": start,
            "end": end,
            "title": title,
            "link": video_url
        })

    return video_details