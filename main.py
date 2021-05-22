import telebot
import pickle
import os
from random import randint

admin_ids=[]

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
        for user in self.users:
            if(user.id==book.owner_id):
                user.books.append(book)
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
    def check_user(self,uid):
        for user in self.users:
            if user.id==uid:
                return True
        return False
    def get_username(self,uid):
        for user in self.users:
            if(user.id == uid):
                return user.name
        return ''.join([str(user) for user in self.users])
    def get_user(self,uid):
        for user in self.users:
            if(user.id==uid):
                return user
        return 0

class User():
    id=0
    name=""
    books=[]
    def __init__(self,name,uid):
        self.id=uid
        self.name=name
        self.books=[]
    def add_book(self,book):
        self.books.append(book)
    def remove_book(self,book):
        self.books.remove(book)
    def change_name(self,new_name):
        self.name=new_name
    def __str__(self):
        return str(self.name)+' '+str(self.id)+' '+''.join('('+str(book)+')' for book in self.books)

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
    owner_id=0
    def __init__(self, name, author, img, oid):
        self.name=name
        self.author=author
        self.img=img
        self.id=gen_id()
        self.owner_id=oid
    def __str__(self):
        return str(self.id)+" : "+self.name



with open("token.secret","r") as f:
    token = f.readline()[:-1]
    admin_ids = [int(i) for i in f.readline().split()]

bot = telebot.TeleBot(token, parse_mode=None)
db = Database()
db.load_all();

commands=['/add','/status']

def handle_messages(messages):
    for message in messages:
        if(message.text==None):
            continue
        uid=int(message.from_user.id)
        if(not db.check_user(message.from_user.id)):
            words=message.text.split();
            if(words[0] in ['/reg', '/regiser']):
                db.add_user(User(message.from_user.username,int(message.from_user.id)))
                bot.reply_to(message,'Succesfully registered as '+message.from_user.username);
            else:
                bot.reply_to(message,'Please register with /reg')
            continue
        words=message.text.split();
        if(words[0] in commands):
            if(words[0]=='/add'):
                db.add_book(Book(''.join([words[i]+' ' for i in range(1,len(words))]),'author','img.png',uid))
                bot.reply_to(message, "book added!")
            if(words[0]=='/status'):
                bot.reply_to(message, str(db.get_user(uid)))
        else:
            bot.reply_to(message, db.get_username(uid)+' is registered!')
        print(message)
        # Do something with the message


bot.set_update_listener(handle_messages)
bot.polling()
