from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from collections import *
from my_token import my_token
from functools import *
import json
import sys

class State:
    #chats = {}  # token -> [id1, id2]
    #id_num = {}  # id -> token
    #state = {}  # 0 - no token ; 1 - sending token; 2 - token sent
    #all_ids = []
    #confirmed = {}  # 0 - no confirmation yet ; 1 - OK
    
    info = {}
    
    def __init__(self):
        info = {'chats' : {}, 'id_num' : {}, 'state' : {}, 'all_ids' : [], 'confirmed' : {}}        
    
    def save_data(self, DATAFILE = "data.txt"):
        with open(DATAFILE, "w") as fileout:
            print(json.dumps(self.info), file=fileout)
        return
    
    def load_data(self, DATAFILE = "data.txt"):
        with open(DATAFILE, "r") as filein:
            s = filein.readline().strip()
            self.info = json.loads(s)  


# string constants
class Info:
    notokenreply = "Ты еще не состоишь в чате. Пожалуйста, напиши '/start' и следуй дальнейшим указаниям."
    waitingreply = "Все, ты зарегистрирован. Ждем твоего собеседника."
    waitingreply2 = "Ждем твоего собеседника."
    readyreply = "Твой собеседник подключился, можете писать друг другу."
    startreply = "Чтобы подключиться к чату, напиши '/token'."
    allcommandsreply = """/start - Чтобы получить инструкции для начала переписки, напиши эту команду.\n
/help - Выводит список команд и их описание.\n
/token - Команда для ввода токена чата.\n
/exit - Напиши, чтобы выйти из чата.\n
/feedback - Выводит контакты для обратной связи."""
    sendtokenreply = "Отлично, теперь пришли токен. Напоминаю, что это должна быть строка из цифр и латинских букв."
    errorreply = "Либо эта команда еще не написана, либо ее вообще не существует. На всякий случай проверь правильность написания."
    feedbackreply = "Пишите мне в телеграм @AlenAliev"
    ineedconfirmreply = "Мне нужно твое подтверждение, если ты уверен, то напиши '/exit' еще раз. Если ты передумал, то просто продолжай общаться."
    nochatreply = "Упс, ты еще не состоишь в чате. Напиши '/start', чтобы начать новый чат."
    deletedchatreply = "Твой собеседник вышел из чата."
    confirmeddeletereply = "Всё, чат удален. Напиши '/start', чтобы начать новый чат."
    alreadyinachatreply = "Упс, ты уже состоишь в чате. Чтобы выйти из чата, напиши '/exit'"
    needastringreply = "Введи, пожалуйста, строку из цифр и букв."

updater = Updater(token=my_token)

CS = State() # state of current session

def data_keeper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ans = func(*args, **kwargs)
        #CS.save_data("data.txt")
        return ans
    return wrapper

def message_handler(case):
    def wrap(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        handler = MessageHandler(case, wrapper)
        updater.dispatcher.add_handler(handler)            
        return wrapper
    return wrap

def command_handler(case):
    def wrap(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        handler = CommandHandler(case, wrapper)  
        updater.dispatcher.add_handler(handler)               
        return wrapper     
    return wrap 

def send(bot, id, text):
    bot.sendMessage(id, text)

@data_keeper
def check_ids(current_id):
    if current_id not in CS.info['all_ids']:
        CS.info['all_ids'].append(current_id)
        CS.info['state'][current_id] = 0

@data_keeper
def check_exit(current_id):
    if CS.info['confirmed'].get(current_id) == None:
        return
    if CS.info['confirmed'][current_id] == 1:
        CS.info['confirmed'][current_id] = 0

@message_handler(~Filters.command & Filters.text)
@data_keeper
def handle_text(bot, update):
    current_id = str(update.message.chat_id)
    message_text = update.message.text
    check_exit(current_id)
    if current_id not in CS.info['all_ids']:  # first message
        CS.info['all_ids'].append(current_id)
        CS.info['state'][current_id] = 0
        send(bot, current_id, Info.notokenreply)
    elif CS.info['state'][current_id] == 0:  # no token id yet
        send(bot, current_id, Info.notokenreply)
    elif CS.info['state'][current_id] == 1:
        CS.info['id_num'][current_id] = message_text
        if CS.info['chats'].get(message_text) == None:
            CS.info['chats'][message_text] = [current_id]
            send(bot, current_id, Info.waitingreply)
        else:
            CS.info['chats'][message_text].append(current_id)
            send(bot, current_id, Info.readyreply)
        CS.info['state'][current_id] = 2
    elif CS.info['state'][current_id] == 2:
        if len(CS.info['chats'][CS.info['id_num'][current_id]]) == 1:
            send(bot, current_id, Info.waitingreply2)
        else:
            if (current_id == CS.info['chats'][CS.info['id_num'][current_id]][0]):
                send(bot, CS.info['chats'][CS.info['id_num'][current_id]][1], message_text)
            else:
                send(bot, CS.info['chats'][CS.info['id_num'][current_id]][0], message_text)
    return

@data_keeper
def handle_not_text(bot, update, message_text, message_func):
    current_id = str(update.message.chat_id)
    check_exit(current_id)
    if current_id not in CS.info['all_ids']:  # first message
        CS.info['all_ids'].append(current_id)
        CS.info['state'][current_id] = 0
        send(bot, current_id, Info.notokenreply)
    elif CS.info['state'][current_id] == 0:  # no token id yet
        send(bot, current_id, Info.notokenreply)
    elif CS.info['state'][current_id] == 1:
        send(bot, current_id, Info.needastringreply)
    elif CS.info['state'][current_id] == 2:
        if len(CS.info['chats'][CS.info['id_num'][current_id]]) == 1:
            send(bot, current_id, Info.waitingreply2)
        else:
            if (current_id == CS.info['chats'][CS.info['id_num'][current_id]][0]):
                message_func(CS.info['chats'][CS.info['id_num'][current_id]][1], message_text.file_id)
            else:
                message_func(CS.info['chats'][CS.info['id_num'][current_id]][0], message_text.file_id)

@message_handler(~Filters.command & Filters.sticker)
def handle_sticker(bot, update):
    message_text = update.message.sticker
    handle_not_text(bot, update, message_text, bot.sendSticker)

@message_handler(~Filters.command & Filters.voice)
def handle_vox(bot, update):
    message_text = update.message.voice
    handle_not_text(bot, update, message_text, bot.sendVoice)

@message_handler(~Filters.command & Filters.photo)
def handle_photo(bot, update):
    message_text = update.message.photo[-1]
    handle_not_text(bot, update, message_text, bot.sendPhoto)

def send_command(bot, update, message : 'String'):
    current_id = str(update.message.chat_id)
    check_exit(current_id)
    check_ids(current_id)
    send(bot, current_id, message)    
    
@command_handler("start")
def handle_start(bot, update):
    send_command(bot, update, Info.startreply)

@command_handler("help")
def handle_help(bot, update):
    send_command(bot, update, Info.allcommandsreply)

@command_handler("feedback")
def handle_feedback(bot, update):
    send_command(bot, update, Info.feedbackreply)
    
@command_handler("exit")
@data_keeper
def handle_exit(bot, update):
    current_id = str(update.message.chat_id)
    check_ids(current_id)
    if CS.info['state'][current_id] != 2:
        send(bot, current_id, Info.nochatreply)
    elif CS.info['confirmed'].get(current_id) == None or CS.info['confirmed'][current_id] == 0:
        send(bot, current_id, Info.ineedconfirmreply)
        CS.info['confirmed'][current_id] = 1
    elif CS.info['confirmed'][current_id] == 1:
        CS.info['state'][current_id] = 0
        if len(CS.info['chats'][CS.info['id_num'][current_id]]) == 1:
            tmp = 0
        elif CS.info['chats'][CS.info['id_num'][current_id]][0] == current_id:
            send(bot, CS.info['chats'][CS.info['id_num'][current_id]][1], Info.deletedchatreply)
            CS.info['state'][CS.info['chats'][CS.info['id_num'][current_id]][1]] = 0
            CS.info['id_num'].pop(CS.info['chats'][CS.info['id_num'][current_id]][1])
        else:
            send(bot, CS.info['chats'][CS.info['id_num'][current_id]][0], Info.deletedchatreply)
            CS.info['state'][CS.info['chats'][CS.info['id_num'][current_id]][0]] = 0
            CS.info['id_num'].pop(CS.info['chats'][CS.info['id_num'][current_id]][0])
        CS.info['chats'].pop(CS.info['id_num'][current_id])
        CS.info['id_num'].pop(current_id)
        send(bot, current_id, Info.confirmeddeletereply)
        check_exit(current_id)    

@command_handler("token")
@data_keeper
def handle_token(bot, update):
    current_id = str(update.message.chat_id)
    check_exit(current_id)
    check_ids(current_id)
    if CS.info['state'].get(current_id) != None and CS.info['state'][current_id] == 2:
        send(bot, current_id, Info.alreadyinachatreply)
        return
    CS.info['state'][current_id] = 1
    send(bot, current_id, Info.sendtokenreply)

@message_handler(Filters.command)
def handle_error(bot, update):
    send_command(bot, update, Info.errorreply)

CS.load_data()

updater.start_polling()