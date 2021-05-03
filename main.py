import telebot
import pickle
import os
from random import randint

def gen_id():
    return randint(1,2**64)

class Database():
    u_dir="users"
    b_dir="books"
    users=[]
    books=[]
    def __init__(self):
        pass
    def load_all(self):
        for u in sorted(os.listdir(self.u_dir)):
            with open(self.u_dir+'/'+u, 'rb') as f:
                self.users.append(pickle.load(f))
        for b in sorted(os.listdir(self.b_dir)):
            with open(self.b_dir+'/'+b, 'rb') as f:
                self.books.append(pickle.load(f))
    def add_book(self,book):
        self.books.append(book)
    def add_user(self,user):
        self.users.append(user)
    def find_books(self,txt):
        return self.books
    def remove_book(self, book):
        os.remove(self.b_dir+'/'+str(book.id))
        self.books.remove(book)
    def remove_user(self, user):
        os.remove(self.u_dir+'/'+str(user.id))
        self.users.remove(user)
    def dump_all(self):
        for u in self.users:
            with open(str(u.id),'wb') as f:
                pickle.dump(u,f)
        for b in self.books:
            with open(str(b.id),'wb') as f:
                pickle.dump(b,f)

class User():
    id=0
    name=""
    books=[]
    def __init__(self,name):
        self.id=gen_id()
        self.name=name
        self.books=[]
    def add_book(self,book):
        self.books.append(book)
    def remove_book(self,book):
        self.books.remove(book)
    def change_name(self,new_name):
        self.name=new_name

class Stats():
    s_f=""
    u_f=""
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
    id=0
    def __init__(self, name, author, img):
        self.name=name
        self.author=author
        self.img=img
        self.id=gen_id()



with open("token.secret","r") as f:
    token = f.readline()[:-1]

bot = telebot.TeleBot(token, parse_mode=None)

def handle_messages(messages):
    for message in messages:
        print(message)
        # Do something with the message
        bot.reply_to(message, message.text)

bot.set_update_listener(handle_messages)
bot.polling()
