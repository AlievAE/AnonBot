# -*- coding: utf-8 -*-

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from collections import *
from functools import *
import json
import sys

token = "1117367323:AAG-cYd0Po4RO5XeJu3lF5jn535dOE2BW38"

chats = {}  # token -> [id1, id2]
id_num = {}  # id -> token
state = {}  # 0 - no token ; 1 - sending token; 2 - token sent
all_ids = []
confirmed = {}  # 0 - no confirmation yet ; 1 - OK

DATA_FILE = "data.txt"

# string constants
notokenreply = "Ты еще не состоишь в чате. Пожалуйста, напиши '/start' и следуй дальнейшим указаниям."
waitingreply = "Все, ты зарегистрирован. Ждем твоего собеседника."
waitingreply2 = "Ждем твоего собеседника."
readyreply = "Твой собеседник подключился, можете писать друг другу."
startreply = "Чтобы подключиться к чату, напиши '/token'."
allcommandsreply = "/start - Чтобы получить инструкции для начала переписки, напиши эту команду.\n" \
                   "/help - Выводит список команд и их описание.\n" \
                   "/token - Команда для ввода токена чата.\n" \
                   "/exit - Напиши, чтобы выйти из чата.\n" \
                   "/feedback - Выводит контакты для обратной связи."
sendtokenreply = "Отлично, теперь пришли токен. Напоминаю, что это должна быть строка из цифр и латинских букв."
errorreply = "Либо эта команда еще не написана, либо ее вообще не существует. На всякий случай проверь правильность написания."
feedbackreply = "Пишите мне в телеграм @AlenAliev"
ineedconfirmreply = "Мне нужно твое подтверждение, если ты уверен, то напиши '/exit' еще раз. Если ты передумал, то просто продолжай общаться."
nochatreply = "Упс, ты еще не состоишь в чате. Напиши '/start', чтобы начать новый чат."
deletedchatreply = "Твой собеседник вышел из чата."
confirmeddeletereply = "Всё, чат удален. Напиши '/start', чтобы начать новый чат."
alreadyinachatreply = "Упс, ты уже состоишь в чате. Чтобы выйти из чата, напиши '/exit'"
needastringreply = "Введи, пожалуйста, строку из цифр и букв."

updater = Updater(token=token)

def save_data():
    with open(DATA_FILE, "w") as fileout:
        print(json.dumps(chats), file=fileout)
        print(json.dumps(id_num), file=fileout)
        print(json.dumps(state), file=fileout)
        print(json.dumps(all_ids), file=fileout)
        print(json.dumps(confirmed), file=fileout)
        
        
def load_data():
    with open(DATA_FILE, "r") as filein:
        s = filein.readlines()
        s = [el.strip() for el in s]
        global chats
        global id_num
        global all_ids
        global state
        global confirmed
        chats = json.loads(s[0])
        id_num = json.loads(s[1])
        state = json.loads(s[2])
        all_ids = json.loads(s[3])
        confirmed = json.loads(s[4])


def data_keeper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ans = func(*args, **kwargs)
        save_data()
        return ans
    return wrapper

def send(bot, id, text):
    bot.sendMessage(id, text)

@data_keeper
def check_ids(current_id):
    if current_id not in all_ids:
        all_ids.append(current_id)
        state[current_id] = 0

@data_keeper
def check_exit(current_id):
    if confirmed.get(current_id) == None:
        return
    if confirmed[current_id] == 1:
        confirmed[current_id] = 0

@data_keeper
def handle_text(bot, update):
    current_id = str(update.message.chat_id)
    message_text = update.message.text
    check_exit(current_id)
    if current_id not in all_ids:  # first message
        all_ids.append(current_id)
        state[current_id] = 0
        send(bot, current_id, notokenreply)
    elif state[current_id] == 0:  # no token id yet
        send(bot, current_id, notokenreply)
    elif state[current_id] == 1:
        id_num[current_id] = message_text
        if chats.get(message_text) == None:
            chats[message_text] = [current_id]
            send(bot, current_id, waitingreply)
        else:
            chats[message_text].append(current_id)
            send(bot, current_id, readyreply)
        state[current_id] = 2
    elif state[current_id] == 2:
        sys.stdout.flush()
        if len(chats[id_num[current_id]]) == 1:
            send(bot, current_id, waitingreply2)
        else:
            if (current_id == chats[id_num[current_id]][0]):
                send(bot, chats[id_num[current_id]][1], message_text)
            else:
                send(bot, chats[id_num[current_id]][0], message_text)
    return

@data_keeper
def handle_not_text(bot, update, message_text, message_func):
    current_id = str(update.message.chat_id)
    check_exit(current_id)
    if current_id not in all_ids:  # first message
        all_ids.append(current_id)
        state[current_id] = 0
        send(bot, current_id, notokenreply)
    elif state[current_id] == 0:  # no token id yet
        send(bot, current_id, notokenreply)
    elif state[current_id] == 1:
        send(bot, current_id, needastringreply)
    elif state[current_id] == 2:
        if len(chats[id_num[current_id]]) == 1:
            send(bot, current_id, waitingreply2)
        else:
            if (current_id == chats[id_num[current_id]][0]):
                message_func(chats[id_num[current_id]][1], message_text.file_id)
            else:
                message_func(chats[id_num[current_id]][0], message_text.file_id)

def handle_sticker(bot, update):
    message_text = update.message.sticker
    handle_not_text(bot, update, message_text, bot.sendSticker)

def handle_vox(bot, update):
    message_text = update.message.voice
    handle_not_text(bot, update, message_text, bot.sendVoice)

def handle_photo(bot, update):
    message_text = update.message.photo[-1]
    handle_not_text(bot, update, message_text, bot.sendPhoto)

def send_command(bot, update, message : 'String'):
    current_id = str(update.message.chat_id)
    check_exit(current_id)
    check_ids(current_id)
    send(bot, current_id, message)    
    
def handle_start(bot, update):
    send_command(bot, update, startreply)

def handle_help(bot, update):
    send_command(bot, update, allcommandsreply)

def handle_error(bot, update):
    send_command(bot, update, errorreply)

def handle_feedback(bot, update):
    send_command(bot, update, feedbackreply)

@data_keeper
def handle_exit(bot, update):
    current_id = str(update.message.chat_id)
    check_ids(current_id)
    if state[current_id] != 2:
        send(bot, current_id, nochatreply)
    elif confirmed.get(current_id) == None or confirmed[current_id] == 0:
        send(bot, current_id, ineedconfirmreply)
        confirmed[current_id] = 1
    elif confirmed[current_id] == 1:
        state[current_id] = 0
        if len(chats[id_num[current_id]]) == 1:
            tmp = 0
        elif chats[id_num[current_id]][0] == current_id:
            send(bot, chats[id_num[current_id]][1], deletedchatreply)
            state[chats[id_num[current_id]][1]] = 0
            id_num.pop(chats[id_num[current_id]][1])
        else:
            send(bot, chats[id_num[current_id]][0], deletedchatreply)
            state[chats[id_num[current_id]][0]] = 0
            id_num.pop(chats[id_num[current_id]][0])
        chats.pop(id_num[current_id])
        id_num.pop(current_id)
        send(bot, current_id, confirmeddeletereply)
        check_exit(current_id)

@data_keeper
def handle_token(bot, update):
    current_id = str(update.message.chat_id)
    check_exit(current_id)
    check_ids(current_id)
    if state.get(current_id) != None and state[current_id] == 2:
        send(bot, current_id, alreadyinachatreply)
        return
    state[current_id] = 1
    send(bot, current_id, sendtokenreply)


load_data()

text_handler = MessageHandler(~Filters.command & Filters.text, handle_text)  # text
sticker_handler = MessageHandler(~Filters.command & Filters.sticker, handle_sticker)  # sticker
vox_handler = MessageHandler(~Filters.command & Filters.voice, handle_vox)  # audio
photo_handler = MessageHandler(~Filters.command & Filters.photo, handle_photo)  # photo
start_handler = CommandHandler("start", handle_start)
help_handler = CommandHandler("help", handle_help)
token_handler = CommandHandler("token", handle_token)
feedback_handler = CommandHandler("feedback", handle_feedback)
exit_handler = CommandHandler("exit", handle_exit)
error_handler = MessageHandler(Filters.command, handle_error)

updater.dispatcher.add_handler(text_handler)
updater.dispatcher.add_handler(start_handler)
updater.dispatcher.add_handler(help_handler)
updater.dispatcher.add_handler(token_handler)
updater.dispatcher.add_handler(feedback_handler)
updater.dispatcher.add_handler(exit_handler)
updater.dispatcher.add_handler(sticker_handler)
updater.dispatcher.add_handler(vox_handler)
updater.dispatcher.add_handler(photo_handler)
updater.dispatcher.add_handler(error_handler)

updater.start_polling()