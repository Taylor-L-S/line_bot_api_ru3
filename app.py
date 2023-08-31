from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import(
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerMessage, FollowEvent
)
from linebot.models import *
from models.database import db_session
from models.user import Users

from models.product import Products
from sqlalchemy.sql.expression import text
from models.database import db_session, init_db

from models.cart import Cart

## pip install sqlalchemy==1.3.5
## pip install line-bot-sdk
## pip install 
## 
app = Flask(__name__)

line_bot_api = LineBotApi('DX8K+3OThP2vbtYoebijLy7gosZVVSDxZAVVfvNilq6+t4yZ10g1HK74dMF3lglMlOXdSO7e9uFH4306LoYVEDQ+SW0web3KggvUFS94ciyQIX4aGgSBi8UicNe2Nr6p9KVMAlIvKGRPj1BB1YF+agdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('880545b3fef970a1460a69447feee723')

def get_or_create_user(user_id):
    user = db_session.query(Users).filter_by(id=user_id).first()
    if not user:
        profile = line_bot_api.get_profile(user_id)
        user = Users(id = user_id, nick_name = profile.display_name, image_url = profile.picture_url)
        db_session.add(user)
        db_session.commit()

    return user

def about_us_event(event):
    emoji = [
             {
                  "index":0,
                  "productId":"5ac21184040ab15980c9b43a", 
                  "emojiId":"225"
             },
             {
                  "index":17,
                  "productId":"5ac21184040ab15980c9b43a", 
                  "emojiId":"225"
             }
        ]
    text_message = TextSendMessage(text = '''$ Master RenderP $
    Hello! 您好，歡迎您成為Master RenderP 的好友!
    我是Master 支付小幫手 

    -這裡有商城，還可以購物喔~
    -直接點選下方【圖中】選單功能

    -期待您的光臨！''', emojis=emoji)
    sticker_message = StickerSendMessage(
        package_id='8522',
        sticker_id='16581271'
    )
    line_bot_api.reply_message(
        event.reply_token,
        [text_message, sticker_message])
    
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
    get_or_create_user(event.source.user_id)
    
    message_text = str(event.message.text).lower()
    cart = Cart(user_id=event.source.user_id)
    message = None
    
    ######################## 使用說明 選單 油價查詢################################
    if message_text == '@使用說明':
        about_us_event(event)
    elif message_text == '我想訂購商品':
        message = Products.list_all()

    elif "i'd like to have" in message_text:

        Product_name = message_text.split(',')[0]
        num_item = message_text.rsplit(':')[1]
        product = db_session.query(Products).fillter(Products.name.ilike(Product_name)).first()

        if product:
            cart.add(product=Product_name, num = num_item)
            confirm_template = ConfirmTemplate(
                text='Sure, {} {}, anything else?'.format(num_item, Product_name),
                actions=[
                    MessageAction(label='Add', text= 'add'),
                    MessageAction(label="That`s it", text = 'That`s it')
                ])
            message = TemplateSendMessage(alt_text = 'anything else?', template=confirm_template)
        else:
            message = TextSendMessage(alt_text = 'Sorry, We don`t have {}.'.format(Product_name))


        print(cart.bucket())

    elif message_text in ['my cart','cart','that`s it']:
        if cart.bucket():
            message = cart.display()
        else:
            message = TextSendMessage(text='Your cart is empty now.')

    if message:
        line_bot_api.reply_message(
        event.reply_token,
        message) 
#初始化產品資訊
@app.before_first_request
def init_products():
    # init db
    result = init_db()#先判斷資料庫有沒有建立，如果還沒建立就會進行下面的動作初始化產品
    if result:
        init_data = [Products(name='Coffee',
                              product_image_url='https://i.imgur.com/DKzbk3l.jpg',
                              price=150,
                              description='nascetur ridiculus mus. Donec quam felis, ultricies'),
                     Products(name='Tea',
                              product_image_url='https://i.imgur.com/PRTxyhq.jpg',
                              price=120,
                              description='adipiscing elit. Aenean commodo ligula eget dolor'),
                     Products(name='Cake',
                              price=180,
                              product_image_url='https://i.imgur.com/PRm22i8.jpg',
                              description='Aenean massa. Cum sociis natoque penatibus')]
        db_session.bulk_save_objects(init_data)#透過這個方法一次儲存list中的產品
        db_session.commit()#最後commit()才會存進資料庫
        #記得要from models.product import Products在app.py
        
    
@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg = """Hello! 您好，歡迎您成為 Master Finance 的好友！

我是Master 財經小幫手 

-這裡有股票，匯率資訊喔~
-直接點選下方【圖中】選單功能

-期待您的光臨！"""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_msg))
    
    # line_bot_api.reply_message(
    #     event.reply_token, TextSendMessage(text='Hi! Welcome to LSTORE.'))


if __name__ == "__main__":
    init_products()
    app.run()