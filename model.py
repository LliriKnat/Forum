from forum import db
from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.String(), nullable=False)

    def __repl__(self):
        return "<User id='%s' name='%s'>" % (self.id, self.name)

    def __str__(self):
        return self.__repl__()


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.String(), nullable=False)
    parent_id = db.Column(UUID(as_uuid=True), db.ForeignKey("categories.id"))

    parent = db.relationship("Category", remote_side=[id])

    def __repl__(self):
        return "<Category id='%s' name='%s'>" % (self.id, self.name)

    def __str__(self):
        return self.__repl__()


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    text = db.Column(db.Text())
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey("categories.id"))
    author_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
    posted_at = db.Column(db.DateTime)

    category = db.relationship("Category", backref=db.backref("messages", lazy=True))
    user = db.relationship("User", backref=db.backref("messages", lazy=True))

    def __repl__(self):
        return "<Message author='%s' posted_at='%s'>" % (self.author_id, self.posted_at)

    def __str__(self):
        return self.__repl__()
