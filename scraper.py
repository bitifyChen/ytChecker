import re
import time
import csv
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

import logging

def fetch_playlist_html(playlist_id, max_scroll_attempts=3):
    PLAYLIST_URL = f"https://www.youtube.com/playlist?list={playlist_id}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(PLAYLIST_URL, timeout=60000)
        page.wait_for_selector('ytd-playlist-video-renderer', timeout=120000)

        # 初始化影片計數與嘗試次數
        previous_video_count = len(page.query_selector_all('#content ytd-playlist-video-renderer'))
        scroll_attempts = 0

        while scroll_attempts < max_scroll_attempts:
            logging.info(f"正在嘗試第 {scroll_attempts + 1} 次滾動...")
            # 滾動到底部
            page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)

            # 檢查新的影片是否加載進來
            current_video_count = len(page.query_selector_all('#content ytd-playlist-video-renderer'))
            logging.info(f"目前影片數量: {current_video_count}")
            
            if current_video_count == previous_video_count:
                scroll_attempts += 1
            else:
                scroll_attempts = 0  # 如果有新資料，重置計數
            
            previous_video_count = current_video_count

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