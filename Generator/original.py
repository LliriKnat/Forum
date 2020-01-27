import psycopg2
from psycopg2.extensions import adapt, AsIs, register_adapter
from psycopg2.extras import execute_values
import random
import functools
import uuid

from datetime import datetime
from datetime import timedelta

words = []
names = []
last_names = []



def get_random_user():
    random_name = "{} {}".format(random.choice(names), random.choice(last_names))
    return {
                'id': str(uuid.uuid4()),
                'name': random_name
           }

def get_random_category():
    # generating category name
    random_words = []
    for i in range(random.randint(1,4)):
        random_words.append(random.choice(words))

    category_name = " ".join(random_words)

    new_category = {
                'id': str(uuid.uuid4()),
                'name': category_name,
                'parent_id': None
            }

    # generating category parent
    if random.getrandbits(1): # same as random.choice([True, False]): but faster
        if(len(categories) is not 0):
            new_category['parent_id'] = random.choice(categories)['id']

    return new_category

def get_random_message():
    random_words = []
    for i in range(random.randint(2,8)):
        random_words.append(random.choice(words))

    message_text = " ".join(random_words)

    new_message = {
        'id': str(uuid.uuid4()),
        'text': message_text,
        'category_id': random.choice(categories)['id'],
        'author_id': random.choice(users)['id'],
        'posted_at': get_random_date()
    }
    return new_message



def get_random_date():
    start = datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    end = datetime.now()

    delta = end - start
    random_seconds = random.randrange(int(delta.total_seconds()))

    return start + timedelta(seconds=random_seconds)


if __name__ == "__main__":
    conn = psycopg2.connect("dbname=forum user=postgres password=qwe123")
    cur = conn.cursor()

    with open('words.txt') as f:
        words = [ line.replace('\n', '') for line in f.readlines() ]    

    with open('first-names.txt') as f:
        names = [ line.replace('\n', '') for line in f.readlines() ]    

    with open('last-names.txt') as f:
        last_names = [ line.replace('\n', '') for line in f.readlines() ]    

    users = []
    categories = []
    messages = []

    #500k users, 5000 categories, 10000000(10m)

    for i in range(1000):
        users.append(get_random_user())

    for i in range(30):
        categories.append(get_random_category())

    for i in range(10000):
        messages.append(get_random_message())

    execute_values(
            cur,
            "INSERT INTO users (id, name) VALUES %s",
            users,
            "(%(id)s, %(name)s)")

    execute_values(
            cur,
            "INSERT INTO categories (id, name, parent_id) VALUES %s",
            categories,
            "(%(id)s, %(name)s, %(parent_id)s)")

    execute_values(
            cur,
            "INSERT INTO messages (id, text, category_id, author_id, posted_at) VALUES %s",
            messages,
            "(%(id)s, %(text)s, %(category_id)s, %(author_id)s, %(posted_at)s)")
    # cur.execute("INSERT INTO users (id, name) VALUES (%s);", [User("nigger")])

    conn.commit()
    cur.close()
    conn.close()

class User:
    def __init__(self, name):
        self._id = uuid.uuid4()
        self._name = name

    def getId(self):
        return self._id

    def getName(self):
        return self._name


class Category:
    def __init__(self, name):
        self._id = uuid.uuid4()
        self._name = name
        self._parent = None

    def getId(self):
        return self._id

    def getName(self):
        return self._name

    def getParent(self):
        return self._parent

    def setParent(self, uuid):
        self._parent = uuid


class Message:
    def __init__(self, text, author, category, posted_at):
        self.id = uuid.uuid4()
        self.text = text
        self.author = author
        self.category = category
        self.posted_at = posted_at


# class to SQL adapters
def adapt_user(user):
    uuid = adapt(str(user.getId()))
    name = adapt(user.getName())
    return AsIs("%s, %s" % (uuid, name))


def adapt_category(category):
    uuid = adapt(category.getId())
    name = adapt(category.getName())
    parent_id = adapt(category.getParent())
    return AsIs("%s, %s, %s" % (uuid, name, parent_id))


def adapt_message(message):
    uuid = adapt(message.id).getquoted()
    text = adapt(message.text).getquoted()
    category_id = adapt(message.category).getquoted()
    author_id = adapt(message.author).getquoted()
    posted_at = adapt(message.posted_at).getquoted()
    return AsIs("'(%s, %s, %s, %s, %s)'"
                % (uuid, text, category_id, author_id, posted_at))


register_adapter(User, adapt_user)
register_adapter(Category, adapt_category)
register_adapter(Message, adapt_message)

def old_get_random_category():
    # generating category name
    random_words = []
    for i in range(random.randint(1,4)):
        random_words.append(random.choice(words))

    category_name = " ".join(random_words)

    new_category = Category(category_name)

    # generating category parent
    if random.getrandbits(1): # same as random.choice([True, False]): but faster
        if(len(categories) is not 0):
            new_category.setParent(random.choice(categories).getId())

    return new_category


def old_get_random_message():
    random_words = []
    for i in range(random.randint(2,8)):
        random_words.append(random.choice(words))

    message_text = " ".join(random_words)

    new_message = Message(
                    message_text,
                    random.choice(users),
                    random.choice(categories),
                    get_random_date())

    return new_message
