from models import Bookmark, Folder, Url
import json
import time
from bs4 import Tag


class Node:
    """
    Mixing class containing the methods used to create folders/urls in
    different formats HTML/JSON/DB, used in the creation of new bookmark tree
    in a different format.
    """

    def create_folder_as_db(self):
        folder = Folder(
            _id=self.id,
            index=self.index,
            parent_id=self.parent_id,
            title=self.title,
            date_added=self.date_added,
        )
        return folder

    def create_url_as_db(self):
        url = Url(
            _id=self.id,
            index=self.index,
            parent_id=self.parent_id,
            title=self.title,
            date_added=self.date_added,
            url=self.url,
            icon=self.icon,
            icon_uri=self.icon_uri,
            tags=self.tags,
        )
        return url

    def create_folder_as_html(self):
        if self.title in ("Bookmarks Toolbar", "Bookmarks bar", "toolbar"):
            return f'<DT><H3 ADD_DATE="{self.date_added}" LAST_MODIFIED="0" PERSONAL_TOOLBAR_FOLDER="true">{self.title}</H3>\n'
        elif self.title in ("Other Bookmarks", "unfiled"):
            return f'<DT><H3 ADD_DATE="{self.date_added}" LAST_MODIFIED="0" UNFILED_BOOKMARKS_FOLDER="true">{self.title}</H3>\n'
        else:
            return f'<DT><H3 ADD_DATE="{self.date_added}" LAST_MODIFIED="0">{self.title}</H3>\n'

    def create_url_as_html(self):
        return f'<DT><A HREF="{self.url}" ADD_DATE="{self.date_added}" LAST_MODIFIED="0" ICON_URI="{self.icon_uri}" ICON="{self.icon}">{self.title}</A>\n'

    def create_folder_as_json(self):
        folder = {
            "type": self.type,
            "id": self.id,
            "index": self.index,
            "parent_id": self.parent_id,
            "title": self.title,
            "date_added": self.date_added,
            "children": [],
        }
        return folder

    def create_url_as_json(self):
        url = {
            "type": self.type,
            "id": self.id,
            "index": self.index,
            "parent_id": self.parent_id,
            "title": self.title,
            "date_added": self.date_added,
            "url": self.url,
            "icon": self.icon,
            "iconuri": self.icon_uri,
            "tags": self.tags,
        }
        return url

    def create_folder(self, output_format):
        formats = {
            "db": lambda: self.create_folder_as_db(),
            "html": lambda: self.create_folder_as_html(),
            "json": lambda: self.create_folder_as_json(),
        }
        return formats[output_format]()

    def create_url(self, output_format):
        formats = {
            "db": lambda: self.create_url_as_db(),
            "html": lambda: self.create_url_as_html(),
            "json": lambda: self.create_url_as_json(),
        }
        return formats[output_format]()

    def __iter__(self):
        "Iterating over an Object iterates over its contents."
        return iter(self.children)

    def __repr__(self):
        return f"{self.title} - {self.type} - id: {self.id}"


class JSONBookmark(Node):
    """
    JSON Bookmark class used to create objects out of the folders/urls in a
    json bookmarks file while importing (json.load) using the object_hook.

    Attributes:
    ----------
    :param id: id of the element
    :type id: int
    :param index: index (position) of the element in its parent
    :type index: int
    :param parent_id: id of the element's parent
    :type parent_id: int
    :param title: title (name) of the element
    :type title: str
    :param date_added: date (time since epoch) at which the element was
    created/added to the bookmarks
    :type date_added: float
    :param type: element type (folder or url)
    :type type: str
    :param children: children of the current element
    :type children: list
    :param source: source of bookmark element (chrome/firefox/bookmarkie)
    :type source: str

    Parameters:
    -----------
    The class expects a mix of parameters similar to the attributes, they vary
    depending on the element type (folder/url)
    """

    def __init__(self, **kwargs):

        if "name" in kwargs:
            self.source = "Chrome"
        elif "typeCode" in kwargs:
            self.source = "Firefox"
        else:
            self.source = "Bookmarkie"

        self.id = int(kwargs.pop("id"))
        self.index = kwargs.pop("index", None)
        self.parent_id = kwargs.pop("parent_id", None)
        # chrome uses different key for title
        self.title = kwargs.pop("title", kwargs.pop("name", None))
        # firefox uses different key for date_added
        self.date_added = int(kwargs.pop("date_added", kwargs.pop("dateAdded", None)))

        temp = kwargs.pop("type")
        if temp in ("folder", "text/x-moz-place-container"):
            self.type = "folder"
            self.children = kwargs.pop("children", [])
        elif temp in ("url", "text/x-moz-place"):
            self.type = "url"
            # firefox uses different key for url
            self.url = kwargs.pop("url", kwargs.pop("uri", None))
            self.icon = kwargs.pop("icon", None)
            # firefox uses different key for icon_uri
            self.icon_uri = kwargs.pop("icon_uri", kwargs.pop("iconuri", None))
            self.tags = kwargs.pop("tags", None)

        if self.source == "Chrome":
            # chrome starts id from 0 not 1, add 1 to adjust
            self.id += 1
            # adjusting epoch for chrome timestamp
            self.date_added = self.date_added - 11644473600000000


class HTMLBookmark(Tag, Node):
    """
    TreeBuilder class, used to add property access to the beautifulsoup
    Tag class' attributes (date_added, icon, icon_uri, title, type and url).
    """

    @property
    def date_added(self):
        date_added = self.attrs.get("add_date")
        if not date_added:
            date_added = round(time.time() * 1000)
        return int(date_added)

    @property
    def icon(self):
        return self.attrs.get("icon")

    @property
    def icon_uri(self):
        return self.attrs.get("icon_uri")

    @property
    def title(self):
        return self.attrs.get("title")

    @property
    def type(self):
        if self.name == "h3":
            return "folder"
        elif self.name == "a":
            return "url"

    @property
    def url(self):
        return self.attrs.get("href")

    @property
    def children(self):
        """To standardize the access of children amongst the different
        classes."""
        return self.contents
