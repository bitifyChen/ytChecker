import requests
from dotenv import load_dotenv
import os

def sendTGNotify(message):
  TG_TOKEN = os.getenv('TG_TOKEN')
  TG_CHAT_ID = os.getenv('TG_CHAT_ID')
  requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={'chat_id':TG_CHAT_ID,'text':message})