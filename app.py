
# encoding: utf-8
#heroku buildpacks:clear

from flask import Flask, request, abort
import json
import tempfile, os, sys
from datetime import datetime
import time
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,VideoSendMessage,ImageSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)

from cht_package.config import line_channel_secret, line_channel_access_token
from bot.template import skip_list, btn_template, carousel_template, main_carosel, get_totalFishStatus
from text_input.olami import OLAMI_textInput
from audio_input.olami_audio import OLAMI_audioInput
from dialogflow.nlp import get_intent, get_district

from cht_package.db_postgres import register_User

from cht_package.audioConvert import toWAV

from bot.cht_sensor import get_do_value, get_ph_value, get_tmp_value
from bot.get_userFishType import get_userFishType
from cht_package.db_postgres import user_notify_open, user_notify_close, user_notify_query

from sp2tx.convert import get_sp2tx
app = Flask(__name__)

handler = WebhookHandler(line_channel_secret) 
line_bot_api = LineBotApi(line_channel_access_token) 

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

#user id
user_id = ''
#first add
first_add = False



@app.route('/')
def index():
    return "<p>Hello cht!</p>"

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

# ================= 機器人區塊 Start =================
@handler.add(MessageEvent, message=(TextMessage, ImageMessage, AudioMessage))
def handle_message(event):
    
    
    if isinstance(event.source, SourceUser) or isinstance(event.source, SourceGroup) or isinstance(event.source, SourceRoom):
        profile = line_bot_api.get_profile(event.source.user_id)
        user_id = profile.user_id
     # Text 
    if isinstance(event.message, TextMessage):
        msg = event.message.text #message from user

        
        global first_add
        if first_add == True:
            
            #register
            first_addFriend(msg, profile.user_id, profile.display_name, profile.picture_url)

            #intro
            line_bot_api.reply_message(event.reply_token, main_carosel(profile.display_name))
            return 0

       
        
        if msg == '檢視魚塭狀態':
                mlist = get_userFishType(profile.user_id)
                do = get_do_value()
                ph = get_ph_value()
                tmp = get_tmp_value()

                if len(mlist) < 1:
                    line_single_push(profile.user_id, '您還沒新增魚種唷~\n快去功能表新增吧！')
                    return 0
                
                message = get_totalFishStatus(len(mlist),mlist, ph, do, tmp, user_id)

                line_bot_api.reply_message(
                    event.reply_token,
                    message
                )
                return 0
        
        elif msg == '設定定時推播':
            confirm_template = ConfirmTemplate(text='要開啟定時推播嗎?', actions=[
            PostbackAction(label='開啟', data='開啟'),
            PostbackAction(label='關閉', data='關閉'),
            ])
            template_message = TemplateSendMessage(
            alt_text='設定定時推播', template=confirm_template)
            line_bot_api.reply_message(event.reply_token, template_message)
        
        elif msg == '近期天氣查詢':

            line_single_push(profile.user_id, '系統建置中')
        
            return 0
        
        elif msg == '異常現象':
            line_single_img(profile.user_id,'https://www.cwb.gov.tw/V7/prevent/typhoon/Data/PTA_NEW/imgs/products/2018102706_PTA_0_download.png')
  
        #get user intent
        elif get_userIntent(profile.user_id, profile.display_name, msg) == 'wakeup':
            
            line_single_push(profile.user_id,profile.display_name+' 主人您好!')
            line_bot_api.reply_message(
                event.reply_token,
                main_carosel(profile.display_name)
            )
            return 0


        

    #Audio
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
        #print("Audio message id:" + event.message.id)
        #waiting for recognition
        if isinstance(event.source, SourceUser) or isinstance(event.source, SourceGroup) or isinstance(event.source, SourceRoom):
            profile = line_bot_api.get_profile(event.source.user_id)
            
            line_single_push(profile.user_id, '解析中...')
        
        audio_content = line_bot_api.get_message_content(event.message.id)
        
    
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in audio_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
        #print('static_tmp_path: '+static_tmp_path)
        #print('tempfile_path: '+tempfile_path) /app/static/tmp/m4a-48lboo6w new
        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        #print('dist_path: '+dist_path) /app/static/tmp/m4a-48lboo6w.m4a old
        #print('distname: '+dist_name) m4a-48lboo6w.m4a

        new_dist_path = tempfile_path + '.wav'
        new_dist_name = os.path.basename(new_dist_path)
        new_path = os.path.join('static', 'tmp', new_dist_name)
        
        os.rename(tempfile_path, dist_path)

        path = os.path.join('static', 'tmp', dist_name)
        print('.m4a path: '+path)

        new_path = toWAV(path, new_path)
        print('.wav path:'+new_path)

        #OLAMI Audio
        # olamiJson = json.loads(OLAMI_audioInput(new_path))
        # response = olamiJson["data"]["asr"]["result"]

        #google
        response = get_sp2tx(new_path)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='你說的是: '+response))
            
        #get user intent
        get_userIntent(profile.user_id, profile.display_name, response)

        os.remove(new_path)
        print('.wav audio file remove ok')
    #Image
    elif isinstance(event.message, ImageMessage):
        ext = 'jpg'
        print("Image message")



@handler.add(FollowEvent)
def handle_follow(event):

    global first_add
    first_add = True

    #Register
    if isinstance(event.source, SourceUser) or isinstance(event.source, SourceGroup) or isinstance(event.source, SourceRoom):
        profile = line_bot_api.get_profile(event.source.user_id)
        #print(profile.display_name)
       
        line_bot_api.reply_message(event.reply_token,[
            TextSendMessage(text='為了提供更精確的服務\n需要您的所在地\n(例:新竹市)',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="臺北市", text="臺北市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="桃園市", text="桃園市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="新竹市", text="新竹市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="臺中市", text="臺中市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="臺南市", text="臺南市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="高雄市", text="高雄市")
                        )
                    ]))
            ] )


#handle postback
@handler.add(PostbackEvent)
def handle_postback(event):

    msg = event.postback.data
    print('post back:'+msg)

    if msg == '開啟':
        user_notify_open(user_id)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='定時推播已開啟'))
  
    elif msg == '關閉':
        user_notify_close(user_id)
        line_bot_api.reply_message(

            event.reply_token, TextSendMessage(text='定時推播已關閉'))
#push text
def line_single_push(id,txt):
    line_bot_api.push_message(id, 
        TextSendMessage(text=txt))
    


#push sticker    
def line_single_sticker(id, packed_id, sticker_id):
    line_bot_api.push_message(id, 
        StickerSendMessage(package_id=packed_id,
    sticker_id=sticker_id))

#push video    
def line_single_video(id, content, preview):
    line_bot_api.push_message(id, 
        VideoSendMessage(original_content_url=content,
    preview_image_url=preview))
#push img    
def line_single_img(id,content):
    line_bot_api.push_message(id, 
        ImageSendMessage(
    original_content_url=content,
    preview_image_url=content
))
#multicast
def line_multicast(mlist, txt):
    line_bot_api.multicast(mlist, TextSendMessage(text=txt))

#register
def first_addFriend(msg, id , name, url):

    area_code = 100
    global first_add

    while True:
        
        area_code = get_district(msg)

        if area_code != 100 and area_code != 'none':
            print(name+' district code: '+ str(area_code))
            first_add = False

             #註冊完給intro
            if register_User(id, name, url, int(area_code)):
                first_add = False
                line_single_push(id, '感謝您提供的資訊')
                line_single_sticker(id, 1, 106)
                
            break

        else:
            line_single_push(id, '為了提供更精確的服務，以獲得完善的體驗\n需要您的所在地\n(例:新竹市)')
            line_single_sticker(id, 1, 4)
        return
        
#get user intent
def get_userIntent(id, name, msg):
    
    intent = get_intent(msg)

    #特定text不進入OLAMI
    if msg in skip_list: 
        return 0
    
    elif intent == '喚醒':
        
        return 'wakeup'

    elif intent == '水質資訊':

        do = get_do_value()
        ph = get_ph_value()
        tmp = get_tmp_value()

        line_single_push(id, '溫度:'+tmp+'°C\n'+  '溶氧量:'+do+'mg/L\n' + '酸鹼度:'+ph)
            
    elif intent == '溫度':
        tmp = get_tmp_value()
        line_single_push(id, '溫度:'+tmp+'°C')

    elif intent == '酸鹼度':
        ph = get_ph_value()
        line_single_push(id, '酸鹼度:'+ph)
        
    elif intent == '溶氧量':
        do = get_do_value()
        line_single_push(id, '溶氧量:'+do+'mg/L')
    
    elif intent == 'help':
        line_single_push(id, '可以試著跟我打招呼叫出功能表或是直接說出您想要的東西唷～')
    

    # intent: none >> OLAMI(天氣、閒聊...)
    else:
        try:
            #OLAMI TEXT
            olamiJson = json.loads(OLAMI_textInput(msg))
            response = olamiJson["data"]["nli"][0]["desc_obj"]["result"]
            
            line_single_push(id, response)
        except Exception as e:
            print('nlp exception:'+str(e))
            line_single_push(id, '對不起，您的說法我還不懂，能換個說法嗎？')
        return 0 
    




# ================= 機器人區塊 End =================

import os
if __name__ == "__main__":
    #app.run(host='0.0.0.0',port=os.environ['PORT'])
    app.run(host='0.0.0.0',port='1000')