from models import Bookmark, Folder, Url
from bs4 import Tag


class Node:
    """
    Class containing information and methods for a Bookmarks File node (URL/FOLDER) obtained from a HTML/JSON/DB file as source.

    Parameters:
    ----------
    :param type: node type (folder or url)
    :type type: str
    :param id: id of the node
    :type id: int
    :param index: index (position) of the node in its parent
    :type index: int
    :param parent_id: id of the node's parent
    :type parent_id: int
    :param title: title (name) of the node
    :type title: str
    :param date_added: date (time since epoch) at which the node was created/added to the bookmarks
    :type date_added: float
    :param date_modified: date (time since epoch) at which the node was created/last modified
    :type date_modified: float
    :param children: children of the current node
    :type children: list
    :param source: source of bookmark node (chrome/firefox/database..etc)
    :type source: str
    """

    def __init__(self, node, _id=None, index=None, parent_id=None, source=None):
        self.id = _id
        self.index = index
        self.parent_id = parent_id
        self.source = source
        if isinstance(node, Tag):
            self.initialize_from_html(node)
        elif isinstance(node, dict):
            self.initialize_from_json(node)
        elif isinstance(node, Bookmark):
            self.initialize_from_db(node)
        else:
            self.raise_typeerror()

    def initialize_from_html(self, node):
        """
        Initialize the Node class using a BeautifulSoup4 Tag element as an input
        """
        self.title = node.get("title")
        self.date_added = node.get("add_date")
        if node.name == "h3":
            self.type = "folder"
            self.children = []  # or node.contents
        elif node.name == "a":
            self.type = "url"
            self.url = node.get("href")
            self.icon = node.get("icon")
            self.icon_uri = node.get("icon_uri")
            self.tags = node.get("tags")
        else:
            self.raise_typeerror("The provided node is neither an 'A' or 'H3' tag")

    def initialize_from_json(self, node):
        _type = node.get("type")
        if _type in ("folder", "text/x-moz-place-container"):
            self.type = "folder"
            self.children = []  # or node.get("children")
        elif _type in ("url", "text/x-moz-place"):
            self.type = "url"
            if self.source == "Firefox":
                self.url = node.get("uri")
            else:
                self.url = node.get("url")
            self.icon = node.get("icon")
            self.icon_uri = node.get("icon_uri")
            self.tags = node.get("tags")
        if self.source == "Chrome":
            self.title = node.get("name")
            self.id += 1
        else:
            self.title = node.get("title")
        if self.source == "Firefox":
            self.date_added = node.get("dateAdded")
        else:
            self.date_added = node.get("date_added")

    def initialize_from_db(self, node):
        self.title = node.title
        self.date_added = node.date_added
        _type = node.type
        if _type in ("folder"):
            self.children = []  # or node.children
        elif _type in ("url",):
            self.url = node.url
            self.icon = node.icon
            self.icon_uri = node.icon_uri
            self.tags = node.tags

    def folder_as_html(self):
        if self.title in ("Bookmarks Toolbar", "Bookmarks bar", "toolbar"):
            return f'<DT><H3 ADD_DATE="{self.date_added}" LAST_MODIFIED="0" PERSONAL_TOOLBAR_FOLDER="true">{self.title}</H3>\n'
        elif self.title in ("Other Bookmarks", "unfiled"):
            return f'<DT><H3 ADD_DATE="{self.date_added}" LAST_MODIFIED="0" UNFILED_BOOKMARKS_FOLDER="true">{self.title}</H3>\n'
        else:
            return f'<DT><H3 ADD_DATE="{self.date_added}" LAST_MODIFIED="0">{self.title}</H3>\n'

    def url_as_html(self):
        return f'<DT><A HREF="{self.url}" ADD_DATE="{self.date_added}" LAST_MODIFIED="0" ICON_URI="{self.icon_uri}" ICON="{self.icon}">{self.title}</A>\n'

    def folder_as_json(self):
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

    def url_as_json(self):
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

    def folder_as_db(self):
        folder = Folder(
            _id=self.id,
            index=self.index,
            parent_id=self.parent_id,
            title=self.title,
            date_added=self.date_added,
        )
        return folder

    def url_as_db(self):
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

    @staticmethod
    def raise_typeerror(msg=None):
        if msg is None:
            msg = "You need to provide a proper node input."
        raise TypeError(msg)
