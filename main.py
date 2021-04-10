import telebot
import pickle

class Stats():
    swapsf=""
    usersf=""
    def record_swap(self,user1,user2,book1,book2):
        pass
    def record_new_user(self,user):
        pass
    def record_new_book(self,book):
        pass

class Book():
    name=""
    author=""
    img=""
    def __init__(self, fl):
        pass
    def __init__(self, _name, _author, _img):
        pass
    
with open("token.secret","r") as f:
    token = f.readline()[:-1]

bot = telebot.TeleBot(token, parse_mode=None)

def handle_messages(messages):
    for message in messages:
        print(message.text)
        # Do something with the message
        bot.reply_to(message, message.text)

bot.set_update_listener(handle_messages)
bot.polling()
