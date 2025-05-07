import os
from flask_restful import Resource,abort
from flask import jsonify, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from scraper import fetch_playlist_html, extract_video_details_from_html

from common.tg import sendTGNotify
from common.line import sendLINENotify

if not firebase_admin._apps:
  firebase_path = os.getenv('FIREBASE_CREDENTIALS_PATH', './etc/secrets/firebase.json')
  cred = credentials.Certificate(firebase_path)
  firebase_admin.initialize_app(cred)
db = firestore.client()

class siLing(Resource):
    def get(self):
        playlist_id = "PLHgQI3BbD7KuxpVksCw13N0oePpJQ0kei"

        html = fetch_playlist_html(playlist_id)
        new_videos = extract_video_details_from_html(html)

        # 使用 Firestore 儲存資料
        ref = db.collection('playlists').document(playlist_id)

        # 取得已存在的影片 ID 清單
        existing_data = ref.get().to_dict() or {}
        existing_ids = set(existing_data.get('ids', []))

        inserted_count = 0
        for video in new_videos:
            vid = str(video["id"]).strip()
            if vid not in existing_ids:
                ref.collection("videos").document(vid).set(video)
                existing_ids.add(vid)
                inserted_count += 1

                # 發送 Telegram 通知
                message = f"道友們，有新影片上傳了!\n第【{video['start']} ~ {video['end']}】集，\n連結: https://www.youtube.com/watch?v={video['id']}"
                sendLINENotify(message)
        # 更新 `ids` 文件
        ref.set({"ids": list(existing_ids)}, merge=True)

        return {
            "message": f"檢查完成，共新增 {inserted_count} 部影片。",
            "updated": inserted_count,
            "total": len(new_videos),
        }