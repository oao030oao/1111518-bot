from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    StickerSendMessage, ImageSendMessage, VideoSendMessage,
    LocationSendMessage, StickerMessage, ImageMessage,
    VideoMessage, LocationMessage
)
import google.generativeai as genai
import os

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_msg = event.message.text.lower()
    reply_token = event.reply_token

    if user_msg == 'hello':
        reply = TextSendMessage(text='你好')
    elif user_msg == 'ok':
        reply = TextSendMessage(text='ok')
    elif user_msg == 'sticker':
        reply = StickerSendMessage(package_id='6359', sticker_id='11069850')
    elif user_msg == 'image':
        reply = ImageSendMessage(
            original_content_url='https://st3.depositphotos.com/30152186/37144/i/450/depositphotos_371445966-stock-photo-funny-kitten-grass-summer.jpg',
            preview_image_url='https://st3.depositphotos.com/30152186/37144/i/450/depositphotos_371445966-stock-photo-funny-kitten-grass-summer.jpg'
        )
    elif user_msg == 'video':
        reply = VideoSendMessage(
            original_content_url='https://res.cloudinary.com/dmfcmhhqs/video/upload/v1747371086/lcdmu7smgili7vdbewwc.mp4',
            #preview_image_url='https://2024-dailyview.s3.ap-northeast-1.amazonaws.com/Content/Upload/Popular/Images/2017-06/e99e6b5e-ca6c-4c19-87b7-dfd63db6381a_m.jpg'
        )
        
    elif user_msg == 'location':
        reply = LocationSendMessage(
            title="總統府",
            address="台北市中正區重慶南路一段122號",
            latitude=25.040319,
            longitude=121.511695
        )

    else:
        try:
            response = model.generate_content(user_msg)
            reply = TextSendMessage(text=response.text)
        except Exception as e:
            reply = TextSendMessage(text=f"AI 回覆錯誤：{e}")

    line_bot_api.reply_message(reply_token, reply)

# 主程式執行
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
