import os
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.event import listens_for, listen
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Set up database info
database_filename = "bookmarkie.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()


# bind the flask appication and the SQLAlchemy service
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


Base = declarative_base()

# Models
class Bookmark(Base, db.Model):
    """Base model for the Url and Directory model.
    (used to Single Table Inheritence)
    ...
    Attributes
    ----------
    id : int
        id of the bookmark (url/directory)
    title : str
        title of bookmark (url/directory)
    date_added : datetime
        date bookmark (url/directory) was added on
    position : int
        current position to remember order of bookmark (url/directory) in directory
    parent_id : int
        id of the directory the bookmark (url/directory) is contained in
    parent : relation
        Many to One relation for the Directory, containing the bookmarks (url/directory)
    """

    __tablename__ = "Bookmark"

    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    date_added = Column(DateTime, nullable=False, default=datetime.utcnow)
    position = Column(Integer)
    parent_id = Column(Integer, ForeignKey("Bookmark.id"), nullable=True)
    parent = relationship(
        "Bookmark",
        cascade="save-update, merge, delete",
        backref="children",
        lazy=False,
        remote_side="Bookmark.id",
    )
    type = Column(String)

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "Bookmark"}

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Url(Bookmark):
    """ Model representing the URLs
    ...
    Attributes
    ----------
    id : int
        id of the url
    title : str
        title of url
    url : str
        url address
    date_added : datetime
        date url was added on
    icon : str
        html icon data
    icon_uri : str
        html icon_uri found in firefox bookmarks
    tags : str
        tags describing url
    position : int
        current position to remember order of urls in directory
    parent_id : int
        id of the directory the url is contained in"""

    url = Column(String(500))
    icon = Column(String)
    icon_uri = Column(String)
    tags = Column(String(500))

    __mapper_args__ = {"polymorphic_identity": "Url"}

    def __init__(
        self,
        title,
        url,
        parent_id,
        date_added=None,
        icon=None,
        icon_uri=None,
        tags=None,
    ):
        if title == None:
            self.title = url
        else:
            self.title = title
        self.url = url
        self.date_added = date_added
        self.icon = icon
        self.icon_uri = icon_uri
        self.tags = tags
        self.parent_id = parent_id

    def __repr__(self):
        return f"{self.title} (id: {self.id}) -in- {self.parent}"

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "date_added": self.date_added,
            "icon": self.icon,
            "icon_uri": self.icon_uri,
            "tags": self.tags,
            "position": self.position,
            "parent_id": self.parent_id,
        }

    @staticmethod
    def serialize_list(bookmarks):
        return [b.serialize() for b in bookmarks]


class Directory(Bookmark):
    """ Model representing bookmark directories
    ...
    Attributes
    ----------
    id : int
        id of the directory
    title : str
        name of the directory
    date_added : datetime
        date directory was added on
    parent_id : int
        id of parent directory
    position : int
        current position in parent directory
    urls : db relationship
        urls contained in the directory"""

    __mapper_args__ = {"polymorphic_identity": "Directory"}

    def __init__(self, title, parent_id, date_added=None):
        self.title = title
        self.date_added = date_added
        self.parent_id = parent_id

    def __repr__(self):
        return f"{self.title} (id: {self.id})"

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "parent_id": self.parent_id,
            "date_added": self.date_added,
            "position": self.position,
            "children": [b.serialize() for b in self.children],
        }

    @staticmethod
    def serialize_list(result):
        return [d.serialize() for d in result]


# Event listener that will index Bookmarks before inserting them.
@listens_for(Bookmark, "before_insert", propagate=True)
def indexer(mapper, connect, self):
    if self.parent_id:
        position = len(Directory.query.get(self.parent_id).children)
        self.position = position

