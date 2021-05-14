from cdifflib import CSequenceMatcher
import os
import telebot
import jsonpickle
from random import randint
 
admin_ids = [302115492]
 
 
def gen_id():
    return randint(1, 2**32)
 
 
class Database():
    def __init__(self):
        self.u_dir = "users"
        self.b_dir = "books"
        self.users = []
        self.books = []
        self.ban = []
        self.ops_done = 0
 
    def op(self):
        self.ops_done+=1
 
    def load_all(self):
        with open("db.json", 'r') as f:
            self = jsonpickle.decode(f.readline())
 
    def dump_all(self):
        with open("db.json", 'w') as f:
            f.write(jsonpickle.encode(self, make_refs=False))
 
    def get_books(self, uid):
        user = self.get_user(uid)
        return user.books
 
    def add_book(self, book):
        print(book)
        self.books.append(book)
        for user in self.users:
            if(user.id == book.owner_id):
                user.books.append(book)
        self.dump_all()
 
    def remove_book_by_id(self, bid):
        bk = 0
        for book in self.books:
            if book.id == bid:
                bk = book
                self.books.remove(book)
                break
        for user in self.users:
            if bk in user.books:
                user.books.remove(book)
                break
 
    def add_user(self, user):
        self.users.append(user)
        self.dump_all()
 
    def find_books(self, txt):
        l = [(max(CSequenceMatcher(None, txt.lower(), book.name.lower()).ratio(), CSequenceMatcher(None, txt.lower(
        ), book.author.lower()).ratio()), '@'+self.get_user(book.owner_id).name, book.name, book.author) for book in self.books]
        l.sort()
        l.reverse()
        l = [i[1:] for i in l]
        return l
 
    def remove_book(self, book):
        self.books.remove(book)
 
    def remove_by_ind(self, uid, ind):
        user = self.get_user(uid)
        if(ind > len(user.books)):
            return -1
        book = user.books[ind-1]
        # print(book)
        # print(self.books)
        # print(user.books)
        for ind, val in enumerate(self.books):
            if(val.id == book.id):
                self.books.pop(ind)
                break
        for ind, val in enumerate(user.books):
            if(val.id == book.id):
                user.books.pop(ind)
                break
        self.dump_all()
        return 0
 
    def remove_user(self, user):
        self.users.remove(user)
 
    def check_user(self, uid):
        for user in self.users:
            if user.id == uid:
                return True
        return False
 
    def get_username(self, uid):
        for user in self.users:
            if(user.id == uid):
                return user.name
        return ''.join([str(user) for user in self.users])
 
    def get_user(self, uid):
        for user in self.users:
            if(user.id == uid):
                return user
        return None
 
    def get_book(self, bid):
        for book in self.books:
            if(book.id == bid):
                return book
        return None
 
    def check_belonging(self, uid, bookid1, bookid2):
        u = self.get_user(uid)
        return (bookid1 in u.books) and (bookid2 not in u.books)
 
    def add_swap_req(self, bookid1, bookid2):
        u1 = self.get_user(self, self.get_book(bookid1))
        pass
 
# print(os.stat("db.json").st_size)
 
 
class User():
    id = 0
    name = ""
    books = []
    requests = []
 
    def __init__(self, name, uid):
        self.id = uid
        self.name = name
        self.books = []
 
    def add_book(self, book):
        self.books.append(book)
 
    def rem_req(self, newb_id, oldb_id):
        if(newb_id, oldb_id) in self.requests:
            self.requests.remove((newb_id, oldb_id))
 
    def remove_book(self, book):
        self.books.remove(book)
 
    def change_name(self, new_name):
        self.name = new_name
 
 
class Stats():
    s_f = ""
    u_f = ""
 
    def record_swap(self, user1, user2, book1, book2):
        pass
 
    def record_new_user(self, user):
        pass
 
    def record_new_book(self, book):
        pass
 
 
class Book():
    def __init__(self, name, author, img, oid):
        self.name = name
        self.author = author
        self.img = img
        self.id = gen_id()
        self.owner_id = oid
 
    def __str__(self):
        return str(self.id)+" : "+self.name
 
 
db = Database()
if(os.stat("db.json").st_size != 0):
    with open("db.json") as f:
        db = jsonpickle.decode(f.readline())
 
with open("token.secret", "r") as f:
    token = f.readline()[:-1]
    admin_ids = [int(i) for i in f.readline().split()]
 
telebot.apihelper.SESSION_TIME_TO_LIVE = 5 * 60
bot = telebot.TeleBot(token, parse_mode=None)
 
descr = {
    '/add название автор': 'Добавить книгу в базу для обмена. В названии могут быть пробелы, в авторе - нет.',
    '/books': 'Показывает список ваших книг в виде id Название Автор',
    '/remove id': 'Позволяет удалить вашу книгу по её `id` из `/books`',
    '/search название\автор': 'Поиск по базе книг для обмена',
    '/help': 'Выводит это сообщение',
    '/user Ник_в_телеграме': 'Выводит список всех книг пользователя',
}
 
 
def handle_messages(messages):
    global db
    for message in messages:
        uid = int(message.from_user.id)
        if(uid in db.ban):
            # bot.reply_to(message, 'Чел, ты в бане')
            continue
        if(message.text == None):
            bot.reply_to(
                message, 'Нет такой комманды :(\n/help выводит список комманд с описанием')
            continue
        words = message.text.split()
        if(not db.check_user(message.from_user.id)):
            db.add_user(User(message.from_user.username,
                        int(message.from_user.id)))
            db.dump_all()
        if(words[0][0] == '/'):
            db.dump_all()
            if(words[0] == '/books'):
                db.op()
                bot.reply_to(message, '\n'.join([str(ind+1)+' '+str(book.name)+' '+str(
                    book.author) for ind, book in enumerate(db.get_books(uid))]))
            if(words[0] == '/remove'):
                db.op()
                if(len(words) < 2):
                    bot.reply_to(
                        message, "Введите `id` книги для удаления из `/books`", parse_mode='Markdown')
                    continue
                if(not all([i in '1234567890' for i in words[1]])):
                    bot.reply_to(message, "`id` должен быть числом от 1 до " +
                                 str(len(db.get_user(uid).books)), parse_mode='Markdown')
                    continue
                if(db.remove_by_ind(uid, int(words[1])) == 0):
                    bot.reply_to(message, "Книга удалена")
                else:
                    bot.reply_to(
                        message, "У вас нет книги с таким `id`", parse_mode='Markdown')
 
            if(words[0] == '/add'):
                db.op()
                if(len(words) >= 3):
                    db.add_book(
                        Book(' '.join(words[1:-1]), words[-1], 'img.png', uid))
                    bot.reply_to(message, "Книга добавлена")
                else:
                    bot.reply_to(
                        message, "У книги должно быть название и автор")
 
            if(words[0] == '/search'):
                db.op()
                q = ' '.join(words[1:])
                bot.reply_to(message, '\n'.join(
                    [' '.join(j for j in i) for i in db.find_books(q)]))
            if(uid in admin_ids):
                if(words[0] == '/rm'):
                    db.remove_book_by_id(int(words[1], 16))
                    db.dump_all()
                    bot.reply_to(message, 'done')
                if(words[0] == '/ban' and (int(words[1]) not in admin_ids)):
                    db.ban.append(int(words[1]))
                    db.dump_all()
                    bot.reply_to(message, 'banned ' +
                                 db.get_user(int(words[1])).name)
                if(words[0] == '/unban'):
                    if(int(words[1]) in db.ban):
                        db.ban.remove(int(words[1]))
                        db.dump_all()
                        bot.reply_to(message, 'unbanned ' +
                                     db.get_user(int(words[1])).name)
                    else:
                        bot.reply_to(message, 'not banned ' +
                                     db.get_user(int(words[1])).name)
                if(words[0] == '/all'):
                    s = ''
                    for book in db.books:
                        s += ' '.join((book.name, book.author, str(hex(book.id)),
                                      '@'+db.get_user(book.owner_id).name))+'\n'
                    bot.reply_to(message, s)
                if(words[0] == '/dump'):
                    db.dump_all()
                    bot.reply_to(message, "db saved")
                if(words[0] == '/load'):
                    with open("db.json", 'r') as f:
                        db = jsonpickle.decode(f.readline())
                    bot.reply_to(message, "db loaded")
 
                if(words[0] == '/json'):
                    bot.reply_to(message, jsonpickle.encode(
                        db, make_refs=False))
        else:
            bot.reply_to(
                message, 'Нет такой комманды :(\n/help выводит список комманд с описанием')
 
 
bot.set_update_listener(handle_messages)
bot.polling(none_stop=True)