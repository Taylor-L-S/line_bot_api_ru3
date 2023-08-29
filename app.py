from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

from database import db_session, init_db

from linebot.models import *
## pip install sqlalchemy==1.3.5
## pip install line-bot-sdk
## pip install 
## 

app = Flask(__name__)

line_bot_api = LineBotApi('DX8K+3OThP2vbtYoebijLy7gosZVVSDxZAVVfvNilq6+t4yZ10g1HK74dMF3lglMlOXdSO7e9uFH4306LoYVEDQ+SW0web3KggvUFS94ciyQIX4aGgSBi8UicNe2Nr6p9KVMAlIvKGRPj1BB1YF+agdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('880545b3fef970a1460a69447feee723')


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #event有什麼資料？詳見補充

    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Hi! Welcome to LSTORE.'))
    
if __name__ == "__main__":
    init_db()
    app.run()