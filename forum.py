from flask import Flask, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, distinct
import math

import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://postgres:qwe123@localhost/forum2"
db = SQLAlchemy(app)

from model import User
from model import Category
from model import Message

@app.route('/')
def index():
    #print(db.session.query(func.count(Message.category_id), Category).\
    #                filter(Message.category_id == Category.id).\
    #                group_by(Category.id).all())

    # counting unique users in each category
    user_count = db.session.query(func.count(distinct(Message.author_id)).label('count'), Category.id.label('category_id'))\
                        .filter(Message.category_id == Category.id)\
                        .group_by(Category).subquery()

    # querying last messages from each category and filtering according to user_count
    last_messages = db.session.query(Category, Message)\
            .join(Message)\
            .filter(user_count.c.count > 3)\
            .filter(user_count.c.category_id == Category.id)\
            .distinct(Category.id)\
            .order_by(Category.id, Message.posted_at.desc())[:10]
            # .all()

    #querying root categories
    root_categories = Category.query\
            .filter(Category.parent_id == None)\
            .all()

    return render_template('index.html',
                           categories=root_categories,
                           messages=[ x for _, x in last_messages ],
                           total_users=User.query.count(),
                           total_categories=Category.query.count(),
                           total_messages=Message.query.count())

@app.route('/category/<path:subpath>', methods = ['GET', 'POST'])
def category(subpath):
    path = subpath.split('/')
    category_name = path[-1] # take last element of path

    category = Category.query\
            .filter(category_name == Category.name)\
            .first()

    if not category:
        abort(404)

    if request.method == 'POST':
        new_msg = Message(
                text = request.form['text'],
                category_id = category.id,
                author_id = os.getenv('USER_UUID'),
                posted_at = datetime.now())
        db.session.add(new_msg)
        db.session.commit()

    MSG_PER_PAGE = 10 # number of messages displayed per page

    # current page
    # if page number is not provided display first page
    # if page number is less than zero display first page
    cur_page = int(request.args.get('page', '') or 1)
    print("Page number %s" % cur_page)

    message_count = Message.query\
            .filter(Message.category_id == category.id)\
            .count()

    page_count = math.ceil(message_count / MSG_PER_PAGE) # pages required to display all messages

    if(cur_page > 6):
        lower = cur_page - 6
    else:
        lower = 1

    if(cur_page + 5 < page_count-1):
        upper = cur_page + 5
    else:
        upper = page_count-1

    messages = Message.query\
            .filter(Message.category_id == category.id)\
            .order_by(Message.posted_at.desc())\
            [(cur_page-1)*MSG_PER_PAGE : cur_page*MSG_PER_PAGE] # pagination

    subcategories = Category.query\
            .filter(Category.parent_id == category.id)\
            .all()

    print("Subpath: %s" % subpath)

    return render_template('category.html',
                           category=category,
                           messages=messages,
                           subcategories=subcategories,
                           subpath=subpath,
                           # pagination
                           cur_page=cur_page,
                           page_count=page_count,
                           message_count=message_count,
                           lower=lower,
                           upper=upper,
                           # footer
                           total_users=User.query.count(),
                           total_categories=Category.query.count(),
                           total_messages=Message.query.count())
