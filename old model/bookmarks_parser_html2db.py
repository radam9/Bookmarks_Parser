from bs4 import BeautifulSoup
from .models import Bookmark, Folder, Url
from .get_favicon import get_favicon_iconuri
from datetime import datetime


def format_datetime(date):
    return datetime.fromtimestamp(int(date))


def parse_url(child, parent_id):
    """
    Function that parses a url tag <DT><A>, creates a url and returns the ID
    """
    date_added = format_datetime(child.get("add_date"))
    href = child.get("href")
    url = Url(title=child.text, url=href, parent_id=parent_id, date_added=date_added,)

    # getting icon, icon_uri and tags
    icon = child.get("icon")
    icon_uri = child.get("icon_uri")
    if icon:
        url.icon = icon
        url.icon_uri = icon_uri
    else:
        url.icon_uri, url.icon = get_favicon_iconuri(href)

    tags = child.get("tags")
    if tags:
        url.tags = tags.split(",")
    url.insert()


def parse_folder(child, parent_id):
    """
    Function that parses a folder tag <DT><H3>
    """
    date_added = format_datetime(child.get("add_date"))
    folder = Folder(title=child.text, parent_id=parent_id, date_added=date_added,)
    # for Bookmarks Toolbar in Firefox and Bookmarks bar in Chrome
    if child.get("personal_toolbar_folder"):
        folder.special = "toolbar"
    # for Other Bookmarks in Firefox
    if child.get("unfiled_bookmarks_folder"):
        folder.special = "other_bookmarks"
    folder.insert()
    return folder


def recursive_parse(node, parent_id):
    """
    Function that recursively parses folders and lists <DL><p>
    """
    # case where node is a folder
    if node.name == "dt":
        folder = parse_folder(node.contents[0], parent_id)
        recursive_parse(node.contents[2], folder.id)
    # case where node is a list
    elif node.name == "dl":
        for child in node:
            tag = child.contents[0].name
            if tag == "h3":
                recursive_parse(child, parent_id)
            elif tag == "a":
                parse_url(child.contents[0], parent_id)


def parse_root_firefox(root, root_folder):
    """
    Function to parse the root of the firefox bookmark tree
    """
    # create bookmark menu folder
    bookmarks = Folder(title="Bookmarks Menu", parent_id=root_folder.id)
    bookmarks.insert()
    for node in root:
        # skip node if not <DT>
        if node.name != "dt":
            continue
        # get tag of first node child
        element = node.contents[0]
        tag = element.name
        if tag == "h3":
            # check for special folders (Other Bookmarks / Toolbar)
            # add them to root level instead of inside bookmarks
            if element.get("personal_toolbar_folder") or element.get(
                "unfiled_bookmarks_folder"
            ):
                recursive_parse(node, root_folder.id)
            else:
                recursive_parse(node, bookmarks.id)
        elif tag == "a":
            parse_url(node.contents[0], bookmarks.id)


def parse_root_chrome(root, root_folder):
    """
    Function to parse the root of the chrome bookmark tree
    """
    for node in root:
        if node.name != "dt":
            continue
        if len(root_folder.children) > 0:
            # Create "other bookmarks" folder
            other_bookmarks = Folder(title="Other Bookmarks", parent_id=root_folder.id)
            other_bookmarks.insert()
        # get the first child element (<H3> or <A>)
        element = node.contents[0]
        tag = element.name
        if tag == "h3":
            # if a folder tag is found at root level, check if its the main "Bookmarks Bar", else append to "Other Bookmarks" children
            if element.get("personal_toolbar_folder"):
                recursive_parse(node, root_folder.id)
            else:
                # if "other_bookmarks" not in locals():
                recursive_parse(node, other_bookmarks.id)
        # if an url tag is found at root level, add it to "Other Bookmarks"
        elif tag == "a":
            parse_url(node.contents[0], other_bookmarks.id)


# Main function
def main(bookmarks_file):
    """
    Main function, takes in a HTML bookmarks file from Chrome/Firefox and returns a JSON nested tree of the bookmarks.
    """
    # Open HTML Bookmark file and pass contents into beautifulsoup
    with open(bookmarks_file, encoding="Utf-8") as f:
        soup = BeautifulSoup(markup=f, features="html5lib", from_encoding="Utf-8")
    # Check if HTML Bookmark version is Chrome or Firefox
    # Get the main DL list (root) out of the html file
    heading = soup.find("h1")
    root = soup.find("dl")
    # Create root folder for bookmarks
    root_folder = Folder(title="root", parent_id=None)
    root_folder.insert()
    # Parse the root of the bookmarks tree
    if heading.text == "Bookmarks":
        parse_root_chrome(root, root_folder)
    elif heading.text == "Bookmarks Menu":
        parse_root_firefox(root, root_folder)


