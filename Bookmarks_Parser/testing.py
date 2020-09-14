from node import Node
from models import Bookmark, Url, Folder
import json
from bs4 import BeautifulSoup

source_html = (
    "/home/vagabond/Downloads/Programming/Bookmarks_Parser/test/bookmarks_chrome.html"
)
source_json = (
    "/home/vagabond/Downloads/Programming/Bookmarks_Parser/test/bookmarks_chrome.json"
)

with open(source_html, "r") as f:
    soup = BeautifulSoup(f)

with open(source_json, "r", encoding="Utf-8") as f:
    content = json.load(f)

bookmark = Url(
    _id=1,
    index=1,
    parent_id=1,
    title="Adam",
    date_added=1257485384,
    url="https://www.google.com",
)


a = Node(node=content.get("roots").get("bookmark_bar"), _id=0, index=0, parent_id=0)

b = 0

c = Node(
    node=bookmark, _id=bookmark.id, index=bookmark.index, parent_id=bookmark.parent
)
x = 0