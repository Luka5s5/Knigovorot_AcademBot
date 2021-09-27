from cdifflib import CSequenceMatcher
import os
import telebot
import jsonpickle
from random import randint

from telebot.types import KeyboardButton, ReplyKeyboardMarkup

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

    def set_user_tbook(self, uid, newtbook):
        for user in self.users:
            if(user.id == uid):
                user.tbook = newtbook

    def get_user_tbook(self, uid):
        for user in self.users:
            if(user.id == uid):
                return user.tbook

    def set_user_status(self, uid, newstatus):
        for user in self.users:
            if(user.id == uid):
                user.status = newstatus

    def get_user_status(self, uid):
        for user in self.users:
            if(user.id == uid):
                return user.status

    def op(self):
        self.ops_done += 1

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
            for book in user.books:
                if(book.id==bid):
                    user.books.remove(book)

    def add_user(self, user):
        self.users.append(user)
        self.dump_all()

    def find_books(self, txt):
        l = [(max(CSequenceMatcher(None, txt.lower(), book.name.lower()).ratio(), CSequenceMatcher(None, txt.lower(
        ), book.author.lower()).ratio(),max((CSequenceMatcher(None,txt.lower(),word).ratio() for word in book.name.split()))), '@'+self.get_user(book.owner_id).name, book.name, book.author) for book in self.books]
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
    status = ""
    tbookname = ''
    books = []
    requests = []

    def __init__(self, name, uid):
        self.id = uid
        self.name = name
        self.books = []
        self.status = 'menu'
        tbookname = ''

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
    # '/user Ник_в_телеграме': 'Выводит список всех книг пользователя',
}

menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(KeyboardButton('📚 Мои книги 📚')).row(KeyboardButton('🔍 Поиск книг 🔍')).row(KeyboardButton(
    '🟢 Добавить книгу 🟢')).row(KeyboardButton('🔴 Удалить книгу 🔴'))
cancel=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(KeyboardButton('Отмена'))

last_message=''

def handle_messages(messages):
    global db
    global menu
    global cancel
    global last_message
    for message in messages:
        last_message=str(message)
        uid = int(message.from_user.id)
        if(uid in db.ban):
            # bot.reply_to(message, 'Чел, ты в бане')
            continue
        if(message.text == None):
            bot.reply_to(
                message, 'Воспользуйтесь меню, пожалуйста', reply_markup=menu)
            continue
        words = message.text.split()
        if(not db.check_user(message.from_user.id)):
            if(message.from_user.username == None):
                bot.reply_to(
                    message, 'Чтобы с вами могли связаться другие пользователи бота, установите, пожалуйста, имя пользователя в настройках аккаунта')
                continue
            db.add_user(User(message.from_user.username,
                        int(message.from_user.id)))
            db.dump_all()
        if(words[0] == '/start'):
            db.op()
            bot.reply_to(
                message, "Привет, я - Бот-книговорот, воспользуйся меню, чтобы добавить или найти интересные книги", reply_markup=menu)
            continue
        # if(words[0][0] == '/'):
        db.dump_all()

        if(message.text == 'Отмена'):
            db.set_user_status(uid,'menu')
            db.set_user_tbook(uid,'')
            bot.reply_to(message,"Операция отменена, воспользуйтесь меню",reply_markup=menu)
            continue

        # if(db.get_user_status(uid)=='adding'):
        #     db.add_book(
        #             Book(' '.join(words[:-1]), words[-1], 'img.png', uid))
        #     bot.reply_to(message,'Книга успешно добавлена!',reply_markup=menu)
        #     db.set_user_status(uid,'menu')
        #     continue

        if(db.get_user_status(uid)=='book'):
            # db.add_book(
                    # Book(' '.join(words[:-1]), words[-1], 'img.png', uid))
            db.set_user_tbook(uid,message.text)
            db.set_user_status(uid,'author')
            bot.reply_to(message,'Теперь введите автора',reply_markup=cancel)
            continue

        if(db.get_user_status(uid)=='author'):
            db.add_book(
                    Book(db.get_user_tbook(uid), message.text, 'img.png', uid))
            bot.reply_to(message,'Книга успешно добавлена!',reply_markup=menu)
            db.set_user_status(uid,'menu')
            continue

        if(db.get_user_status(uid)=='deleting'):
            if(len(words) < 1):
                bot.reply_to(
                    message, "Введите `id` книги для удаления из `/books`", parse_mode='Markdown',reply_markup=cancel)
                continue
            if(not all([i in '1234567890' for i in words[0]])):
                bot.reply_to(message, "`id` должен быть числом от 1 до " +
                             str(len(db.get_user(uid).books)), parse_mode='Markdown',reply_markup=cancel)
                continue
            if(db.remove_by_ind(uid, int(words[0])) == 0):
                bot.reply_to(message, "Книга удалена",reply_markup=menu)
                db.set_user_status(uid,'menu')
                continue
            else:
                bot.reply_to(
                    message, "У вас нет книги с таким `id`", parse_mode='Markdown',reply_markup=cancel)
                continue

        if(db.get_user_status(uid)=='searching'):
            q = message.text
            bot.reply_to(message, '\n'.join(
                [' '.join(j for j in i) for i in db.find_books(q)][:10:]),reply_markup=menu)
            db.set_user_status(uid,'menu')
            continue

        if(message.text == '🟢 Добавить книгу 🟢'):
            bot.reply_to(message, 'Введите название книги без автора',reply_markup=cancel)
            db.set_user_status(uid, 'book')
            continue
        
        if(message.text == '📚 Мои книги 📚'):
            if(len(db.get_books(uid))!=0):
                bot.reply_to(message,'\n'.join([str(ind+1)+' '+str(
                book.author)+' - '+str(book.name) for ind, book in enumerate(db.get_books(uid))]),reply_markup=menu)
            else:
                bot.reply_to(message,'К сожалению у вас пока нет книг :(\nВы можете добавить их с помощью соответствующего пункта меню',reply_markup=menu)
            continue

        if(message.text == '🔍 Поиск книг 🔍'):
            db.set_user_status(uid,'searching')
            bot.reply_to(message,'Введите название или автора',reply_markup=cancel)
            continue

        if(message.text == '🔴 Удалить книгу 🔴'):
            if(len(db.get_books(uid))==0):
                bot.reply_to(message,'К сожалению у вас пока нет книг :(\nВы можете добавить их с помощью соответствующего пункта меню',reply_markup=menu)
                continue
            db.set_user_status(uid,'deleting')
            bot.reply_to(message,'Введите номер книги:\n'+'\n'.join([str(ind+1)+' '+str(book.name)+' '+str(
                book.author) for ind, book in enumerate(db.get_books(uid))]),reply_markup=cancel)
            continue
        if(words[0] == '/help'):
            db.op()
            bot.reply_to(message, '\n'.join(
                ['`'+comm+'` : '+desc for comm, desc in descr.items()]), parse_mode='Markdown')
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
                continue
            if(words[0] == '/ban' and (int(words[1]) not in admin_ids)):
                db.ban.append(int(words[1]))
                db.dump_all()
                bot.reply_to(message, 'banned ' +
                             db.get_user(int(words[1])).name)
                continue
            if(words[0]=='log'):
                bot.reply_to(message,last_message,reply_markup=menu)
            if(words[0] == '/unban'):
                if(int(words[1]) in db.ban):
                    db.ban.remove(int(words[1]))
                    db.dump_all()
                    bot.reply_to(message, 'unbanned ' +
                                 db.get_user(int(words[1])).name)
                else:
                    bot.reply_to(message, 'not banned ' +
                                 db.get_user(int(words[1])).name)
                continue
            if(words[0] == '/ucount'):
                bot.reply_to(message,str(len(db.users)))
            if(words[0] == '/all'):
                s = ''
                for book in db.books:
                    s += ' '.join((book.name, book.author, str(hex(book.id)),
                                   '@'+db.get_user(book.owner_id).name+' '+str(book.owner_id)))+'\n'
                chunks = [s[i:i+4000] for i in range(0, len(s), 4000)]
                for st in chunks:
                    bot.reply_to(message, st)
                continue
            if(words[0] == '/dump'):
                db.dump_all()
                bot.reply_to(message, "db saved")
                continue
            if(words[0] == '/load'):
                with open("db.json", 'r') as f:
                    db = jsonpickle.decode(f.readline())
                bot.reply_to(message, "db loaded")
                continue

            if(words[0] == '/json'):
                bot.reply_to(message, jsonpickle.encode(
                    db, make_refs=False))
                continue
        bot.reply_to(message,'Воспользуйтесь, пожалуйста, меню',reply_markup=menu)


bot.set_update_listener(handle_messages)
bot.polling(none_stop=True)
