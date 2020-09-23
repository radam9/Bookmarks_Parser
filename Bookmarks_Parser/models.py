import time

import sqlalchemy
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Bookmark(Base):
    """Base model for the Url and Folder model.
    (used to Single Table Inheritence)
    ...
    Attributes
    ----------
    id : int
        id of the bookmark (url/folder)
    title : str
        title of bookmark (url/folder)
    date_added : datetime
        date bookmark (url/folder) was added on
    index : int
        current index to remember order of bookmark (url/folder) in folder
    parent_id : int
        id of the folder the bookmark (url/folder) is contained in
    parent : relation
        Many to One relation for the Folder, containing the bookmarks (url/folder)
    """

    __tablename__ = "bookmark"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    index = Column(Integer)
    parent_id = Column(Integer, ForeignKey("bookmark.id"), nullable=True)
    date_added = Column(Integer, nullable=False, default=round(time.time() * 1000))
    type = Column(String)
    parent = relationship(
        "Bookmark",
        cascade="save-update, merge",
        backref=backref("children", cascade="all"),
        lazy=False,
        remote_side="Bookmark.id",
    )

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "bookmark"}

    def insert(self):
        session.add(self)
        session.commit()

    def update(self):
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()


class Folder(Bookmark):
    """Model representing bookmark folders
    ...
    Attributes
    ----------
    id : int
        id of the folder
    title : str
        name of the folder
    date_added : datetime
        date folder was added on
    parent_id : int
        id of parent folder
    index : int
        current index in parent folder
    urls : db relationship
        urls contained in the folder"""

    __mapper_args__ = {"polymorphic_identity": "folder"}

    def __init__(self, title, index, parent_id, _id=None, date_added=None):
        if _id:
            self.id = _id
        self.title = title
        self.index = index
        self.parent_id = parent_id
        self.date_added = date_added


class Url(Bookmark):
    """Model representing the URLs
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
    index : int
        current index to remember order of urls in folder
    parent_id : int
        id of the folder the url is contained in"""

    url = Column(String)
    icon = Column(String)
    icon_uri = Column(String)
    tags = Column(String)

    __mapper_args__ = {"polymorphic_identity": "url"}

    def __init__(
        self,
        title,
        index,
        parent_id,
        url,
        _id=None,
        date_added=None,
        icon=None,
        icon_uri=None,
        tags=None,
    ):
        if _id:
            self.id = _id
        if title == None:
            self.title = url
        else:
            self.title = title
        self.index = index
        self.parent_id = parent_id
        self.date_added = date_added
        self.url = url
        self.icon = icon
        self.icon_uri = icon_uri
        self.tags = tags
