from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,VideoSendMessage,
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

#跳脫不進入olami (template's text save here)
skip_list = ['func1', 'func2', 'func3', '檢視魚塭狀態', '魚塭異常總覽' , '近期天氣查詢']

def btn_template(maintitle, subtitle, pic_url, label1, text1, pb1, label2, text2, pb2, label3, text3, pb3):

    msg = buttons_template_message = TemplateSendMessage(
    alt_text='請選擇',
    template=ButtonsTemplate(
        thumbnail_image_url= pic_url,
        title=maintitle,
        text=subtitle,
        actions=[
            PostbackAction(
                label=label1,
                text=text1,
                data=pb1
            ),
            PostbackAction(
                label=label2,
                text=text2,
                data=pb2
            ),
            PostbackAction(
                label=label3,
                text=text3,
                data=pb3
            ),
        ]
        )
    )
    return msg

def carousel_template():
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item1.jpg',
                    title='this is menu1',
                    text='description1',
                    actions=[
                        PostbackAction(
                            label='postback1',
                            text='postback text1',
                            data='action=buy&itemid=1'
                        ),
                        MessageAction(
                            label='message1',
                            text='message text1'
                        ),
                        URIAction(
                            label='uri1',
                            uri='http://example.com/1'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item2.jpg',
                    title='this is menu2',
                    text='description2',
                    actions=[
                        PostbackAction(
                            label='postback2',
                            text='postback text2',
                            data='action=buy&itemid=2'
                        ),
                        MessageAction(
                            label='message2',
                            text='message text2'
                        ),
                        URIAction(
                            label='uri2',
                            uri='http://example.com/2'
                        )
                    ]
                )
            ]
        )
    )
    return carousel_template_message


def main_carosel(name):
        carousel_template_message = TemplateSendMessage(
        alt_text='歡迎使用',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://i.imgur.com/Wiqlff7.png',
                    title=name+' 您好!',
                    text='歡迎使用Fish Farmer \n 請選擇以下的服務',
                    actions=[
                        MessageAction(
                            label='檢視魚塭狀態',
                            text='檢視魚塭狀態'
                        ),
                        MessageAction(
                            label='魚塭異常總覽',
                            text='魚塭異常總覽'
                        ),
                        MessageAction(
                            label='近期天氣查詢',
                            text='近期天氣查詢'
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://i.imgur.com/Wiqlff7.png',
                    title='設定',
                    text='請選擇以下的服務',
                    actions=[
                        URIAction(
                            label='魚種設定',
                            uri='http://example.com/2'
                        ),
                        MessageAction(
                            label='設定定時推播',
                            text='設定定時推播'
                        ),
                        MessageAction(
                            label='設定人生',
                            text='設定人生'
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item2.jpg',
                    title='關於我們',
                    text='一群為Hackthon而生的孩子們',
                    actions=[
                        URIAction(
                            label='Facebook',
                            uri='http://example.com/2'
                        ),
                        URIAction(
                            label='Instagram',
                            uri='http://example.com/2'
                        ),
                       URIAction(
                            label='作品集',
                            uri='http://example.com/2'
                        )
                    ]
                )
            ]
        )
        )
        return carousel_template_message


def get_totalFishStatus(count, list):
    if count == 1:
        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
            layout='vertical',
            contents=[                    
            # title
            BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text='魚塭狀態', weight='bold', size='sm', color='#1DB446'),
                TextComponent(text='魚塭資訊回傳', weight='bold', size='xxl', margin='md'),
                TextComponent(text='新北市板橋區', size='xs', color='#aaaaaa', margin='sm', wrap=True),
                SeparatorComponent(margin='xxl'),
                TextComponent(text='種類', size="md", weight="bold", wrap=True, spacing='sm', margin='md'),
                ]
            ),

            # fish 
            BoxComponent(
            layout='horizontal',
            margin='md',
            spacing='sm',
            contents=[             
            TextComponent(text="吳郭魚", size="xl", wrap=True, gravity="center"),
            SeparatorComponent(gravity="center"),
            ImageComponent(size= "xs", aspectRatio="20:13", aspectMode="fit", url="https://i.imgur.com/6C044b5.png", align="end", gravity="center") 
            ]
            ),
                            
            SeparatorComponent(margin='xxl'),
            TextComponent(text="水質資訊", size="md", weight="bold", wrap=True, spacing='sm', margin='md'),

            # water-ph
            BoxComponent(
                layout='horizontal',
                margin='md',
                spacing='sm',
                contents=[
                                    
                    TextComponent(text="ph值", size="sm", color="#555555", align="start"),
                    TextComponent(text="8.9", siz="sm", color="#111111", align="end")
                ]
            ),
            # water-do
            BoxComponent(
            layout='horizontal',
            margin='md',
            spacing='sm',
            contents=[
                TextComponent(text="溶氧量(mg/L)", size="sm", color="#555555", flex=0),
                TextComponent(text="3.5", siz="sm", color="#111111", align="end")
                ]
            ),

            # water-tmp
            BoxComponent(
                layout='horizontal',
                margin='md',
                spacing='sm',
                contents=[
                    TextComponent(text="水溫(°C)", size="sm", color="#555555", flex=0),
                    TextComponent(text="23", siz="sm", color="#111111", align="end")
                ]
                )
            ]
            ),

            #
            footer=BoxComponent(
                layout='vertical',
                margin='md',
                spacing='md',
                contents=[
                    TextComponent(text="日期時間", size="xs", color="#aaaaaa", flex=0),
                    TextComponent(text="2018-10-28 14:20", size="xs", color="#aaaaaa", align="end")
                ]
                )
        )
        message = FlexSendMessage(alt_text="魚塭狀態", contents=bubble)
        return message
        
'''    elif count == 2:
    elif count == 3:
    elif count == 4:
    elif count == 5:
    elif count == 6:
    elif count == 7:
    elif count == 8:
    elif count == 9:
    elif count == 10:'''