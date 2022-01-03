import json
import os

import requests
from telegram.ext import Updater, MessageHandler, Filters
from pytube import YouTube

last_url = ""
authorised_users = []
login = "smalow"
password = "#Zebra2022"
telegram_bot_token = "1098449627:AAHaFcYmW2WoBdgXE1IJamhEuOigqN8G6ZU"
bot_password = "123"

def getVideoUrl(url):

    global last_url

    if url == last_url:  # Second attempt - trying another player
        yt = YouTube(url).streams.first()
        last_url = url
        return yt.url

    last_url = url

    if "https://www.youtube" in url:
        url = url.split("&")[0]  # Removing arguments

    if "https://youtu.be" in url:
        url = "https://www.youtube.com/watch?v=" + url.split("/")[-1]

    # Page parsing and getting video_url here
    return url


def extractUrl(message):
    return message.text  # TODO: getting url by entities info


def sendToScreen(video_url):
    # Auth and getting Session_id

    auth_data = {
        'login': login,
        'passwd': password
    }

    s = requests.Session()
    print(s)
    s.get("https://passport.yandex.ru/")
    s.post("https://passport.yandex.ru/passport?mode=auth&retpath=https://yandex.ru", data=auth_data)

    Session_id = s.cookies["Session_id"]

    # Getting x-csrf-token
    token = s.get('https://frontend.vh.yandex.ru/csrf_token').text
    print(token)

    # Detting devices info TODO: device selection here
    devices_online_stats = s.get("https://quasar.yandex.ru/devices_online_stats").text
    devices = json.loads(devices_online_stats)["items"]

    # Preparing request
    headers = {
        "x-csrf-token": token,
    }

    data = {
        "msg": {
            "provider_item_id": video_url
        },
        "device": devices[0]["id"]
    }

    if "youtu" in video_url:
        data["msg"]["player_id"] = "youtube"
        data["msg"]["type"] = "video"
        data["msg"]["provider_name"] = "Youtube"

    # Sending command with video to device
    res = s.post("https://yandex.ru/video/station", data=json.dumps(data), headers=headers)
    print(res)

    return res.text


def message_recieved(bot, update, context):

    chat_id = bot.message.chat_id
    # TODO: get yandex configs based on user_id

    print(chat_id)

    if bot.message.text == bot_password:
        authorised_users.append(chat_id)
        print(f"Authorised: {chat_id}")
        return

    if not chat_id in authorised_users:
        print("Unauthorised request blocked!")
        return

    url = extractUrl(bot.message)
    video_url = getVideoUrl(url)
    result = sendToScreen(video_url)

    context.bot.send_message("Message has been sent")

    print(result)

def main():

    updater = Updater(token=telegram_bot_token, use_context=True)

    message_handler = MessageHandler(Filters.all, message_recieved)
    updater.dispatcher.add_handler(message_handler)

    print("Start polling...")

    updater.start_webhook(listen="0.0.0.0",port=os.environ.get("PORT",443),
                          url_path=telegram_bot_token,
                          webhook_url="https://mimic-app.herokuapp.com/"+telegram_bot_token)
    updater.idle()

#start application with main function
if __name__ == '__main__':
    main()

