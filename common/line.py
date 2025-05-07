import requests
import json
from dotenv import load_dotenv
import os


def sendLINENotify(message):
  LINE_TOKEN = os.getenv('LINE_TOKEN')
  LINE_CHAT_ID  = os.getenv('LINE_CHAT_ID')

  if not LINE_TOKEN or not LINE_CHAT_ID:
        print("LINE_TOKEN 或 LINE_CHAT_ID 沒有正確讀取，請檢查 .env 檔案")
        return
  
  # 發送訊息的 API URL
  url = 'https://api.line.me/v2/bot/message/push'

  # 設定要發送的訊息內容
  message_data = {
      "to": LINE_CHAT_ID,
      "messages": [
          {
              "type": "text",
              "text": message
          }
      ]
  }

  # 設定 headers，包含 Authorization
  headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {LINE_TOKEN}'
  }

  # 發送 POST 請求到 LINE API
  requests.post(url, headers=headers, data=json.dumps(message_data))