from bs4 import BeautifulSoup
from models import *
import time
import os
import json
import re


class HTMLMixin:
    def parse_root_html(self):
        header = """<!DOCTYPE NETSCAPE-Bookmark-file-1>\n<!-- This is an automatically generated file.\n     It will be read and overwritten.\n     DO NOT EDIT! -->\n<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks Menu</H1>\n<DL><p>\n"""
        footer = "</DL>"

        self.proccessed = []

        while self.stack:
            stack_item = self.stack.pop()
            folder = self.iterate_folder_html(stack_item)
            if folder:
                placeholder = f'<folder{stack_item.get("id")}>'
                if self.proccessed and (placeholder in self.proccessed[-1]):
                    self.proccessed[-1] = self.proccessed[-1].replace(
                        placeholder, folder
                    )
                else:
                    self.proccessed.append(folder)

        temp = [header]
        temp.extend(self.proccessed)
        temp.append(footer)
        self.bookmarks = "".join(temp)

    def iterate_folder_html(self, stack_item):
        folder = [self.parse_folder_html(stack_item), "<DL><p>\n"]
        list_end = "</DL><p>\n"

        children = stack_item.get("children")
        if children:
            for child in children:
                if child.get("type") in ("folder", "text/x-moz-place-container"):
                    item = f'<folder{child.get("id")}>'
                    self.stack.append(child)
                else:
                    item = self.parse_url_html(child)
                folder.append(item)
            folder.append(list_end)
            result = "".join(folder)
            return result

    def parse_folder_html(self, folder):
        date_added = self.get_date_added(folder)
        title = self.get_title(folder)
        if title in ("Bookmarks Toolbar", "Bookmarks bar", "toolbar"):
            return f'<DT><H3 ADD_DATE="{date_added}" LAST_MODIFIED="0" PERSONAL_TOOLBAR_FOLDER="true">{title}</H3>\n'
        elif title in ("Other Bookmarks", "unfiled"):
            return f'<DT><H3 ADD_DATE="{date_added}" LAST_MODIFIED="0" UNFILED_BOOKMARKS_FOLDER="true">{title}</H3>\n'
        else:
            return f'<DT><H3 ADD_DATE="{date_added}" LAST_MODIFIED="0">{title}</H3>\n'

    def parse_url_html(self, url):
        return f'<DT><A HREF="{self.get_url(url)}" ADD_DATE="{self.get_date_added(url)}" LAST_MODIFIED="0" ICON_URI="{url.get("icon_uri")}" ICON="{url.get("icon")}">{self.get_title(url)}</A>\n'

    def get_title(self, item):
        if self.source == "Chrome":
            return item.get("name")
        else:
            return item.get("title")

    def get_date_added(self, item):
        if self.source == "Firefox":
            return item.get("dateAdded")
        else:
            return item.get("date_added")

    def get_url(self, item):
        if self.source == "Firefox":
            return item.get("uri")
        else:
            return item.get("url")


class BookmarksParserHTML:
    def __init__(self, filepath):

        self.new_filepath = (
            os.path.dirname(filepath) + "/new_" + os.path.basename(filepath)
        )

        self.format_bookmark_html(filepath)

        with open(self.new_filepath, "r", encoding="Utf-8") as f:
            self.soup = BeautifulSoup(
                markup=f, features="html.parser", from_encoding="Utf-8"
            )
        self.tree = self.soup.find("h3")
        del self.soup
        self.source = "Chrome" if self.tree.get("title") == "Bookmarks" else "Firefox"

        self.id = 2
        # stack containes a tuple of (folder, node).
        # folder being the parsed data, and node being the folder data from the tree.
        self.stack = []

    def format_bookmark_html(self, filepath):
        """
        Takes in an absolute path to a HTML Bookmarks file, it creates a new Bookmarks file with the text "new_" prepeneded to the filename. where,
        - The main "<H1>" header is converted to "<H3>" and acts as the root folder.
        - All "<DT>" tags are removed.
        - "<H3>" acts as folders and list containers instead of "<DL>".
        - All "<H3>" and "<A>" tag's inner text are added as a "title" attribute within the html element.

        :param file_path: absolute path to bookmarks html file
        :type file_path: str
        """
        with open(filepath, "r") as f:
            lines = f.readlines()

        # regex to select an entire H1/H3/A HTML element
        element = re.compile(r"(<(H1|H3|A))(.*?(?=>))>(.*)(<\/\2>)\n")

        # NOTE: maybe change the list comprehensions to Generator Comprehension for better efficiency

        lines1 = [element.sub(r'\1\3 TITLE="\4">\5', line) for line in lines]
        lines2 = [line.replace("<DT>", "") for line in lines1 if "<DL><p>" not in line]
        lines3 = [
            line.replace("<H1", "<H3")
            .replace("</H1>", "")
            .replace("</H3>", "")
            .replace("</DL><p>\n", "</H3>")
            .replace("\n", "")
            .strip()
            for line in lines2
        ]

        with open(self.new_filepath, "w") as f:
            f.writelines(lines3)

    def convert_to_json(self):
        self.mode = "json"
        self.bookmarks = {
            "type": "folder",
            "id": 1,
            "index": 0,
            "parent_id": None,
            "title": "root",
            "date_added": None,
            "date_modified": None,
            "children": [],
        }
        if self.source == "Chrome":
            self.parse_chrome_root_to_json()
        elif self.source == "Firefox":
            self.parse_firefox_root_to_json()

        while self.stack:
            stack_item = self.stack.pop()
            self.iterate_folder(mode="folder", stack_item=stack_item)

    def convert_to_db(self):
        self.mode = "db"
        self.bookmarks = []
        root = Folder(_id=1, title="root", parent_id="0", index=0)
        self.bookmarks.append(root)

        if self.source == "Chrome":
            self.parse_chrome_root_to_db(root)
        elif self.source == "Firefox":
            self.parse_firefox_root_to_db(root)

        while self.stack:
            stack_item = self.stack.pop()
            self.iterate_folder(mode="folder", stack_item=stack_item)

    def save_to_json(self):
        """
        Function to export the bookmarks as JSON at the same location and with the same name as the original file.
        """
        output_file = self.new_filepath.replace(".html", ".json")

        with open(output_file, "w", encoding="Utf-8") as f:
            json.dump(self.bookmarks, f, ensure_ascii=False)

    def save_to_db(self):
        database_path = "sqlite:///" + self.new_filepath.replace(".html", ".db")
        engine = create_engine(database_path, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        remove(Bookmark, "before_insert", indexer)
        Base.metadata.create_all(engine)
        session.commit()
        session.bulk_save_objects(self.bookmarks)
        session.commit()

    def parse_firefox_root_to_json(self):
        """
        Function that will format and iterate through a Firefox bookmarks file.
        """
        bookmarks_menu = {
            "type": "folder",
            "id": self.id_manager(),
            "index": 0,
            "parent_id": self.bookmarks.get("id"),
            "title": "Bookmarks Menu",
            "date_added": time.time(),
            "date_modified": None,
            "children": [],
        }
        menu_children = []
        root_children = [bookmarks_menu]
        for child in self.tree:
            if child.name == "h3":
                if child.get("personal_toolbar_folder") == "true":
                    index = len(root_children)
                    bookmarks_toolbar = self.parse_folder(
                        child, index, self.bookmarks.get("id")
                    )
                    self.add_to_stack((bookmarks_toolbar, child))
                    root_children.append(bookmarks_toolbar)
                elif child.get("unfiled.bookmarks.folder") == "true":
                    index = len(root_children)
                    other_bookmarks = self.parse_folder(
                        child, index, self.bookmarks.get("id")
                    )
                    self.add_to_stack((other_bookmarks, child))
                    root_children.append(other_bookmarks)
            else:
                menu_children.append(child)
        if menu_children:
            self.iterate_folder(
                mode="root", folder=bookmarks_menu, children=menu_children
            )

        self.bookmarks.get("children").extend(root_children)

    def parse_chrome_root_to_json(self):
        """
        Function that will format and iterate through a Chrome bookmarks file.
        """
        other_children = []
        for child in self.tree.children:
            if child.name == "h3":
                if child.get("personal_toolbar_folder") == "true":
                    bookmarks_bar = self.parse_folder(
                        child, 0, self.bookmarks.get("id")
                    )
                    self.bookmarks["children"].append(bookmarks_bar)
                    self.add_to_stack((bookmarks_bar, child))
            else:
                other_children.append(child)
        if other_children:
            other_bookmarks = {
                "type": "folder",
                "id": self.id_manager(),
                "index": 1,
                "parent_id": self.bookmarks.get("id"),
                "title": "Other Bookmarks",
                "date_added": time.time(),
                "date_modified": None,
                "children": [],
            }
            self.iterate_folder(
                mode="root", folder=other_bookmarks, children=other_children
            )
            self.bookmarks.get("children").append(other_bookmarks)

    def parse_firefox_root_to_db(self, root):
        bookmarks_menu = Folder(
            _id=self.id_manager(), index=0, parent_id=root.id, title="Bookmarks Menu"
        )
        self.bookmarks.append(bookmarks_menu)
        menu_children = []
        for child in self.tree.children:
            if child.get("parsonal_toolbar_folder") == "true":
                index = len(self.bookmarks) - 1
                bookmarks_toolbar = self.parse_folder(
                    item=child, index=index, parent_id=root.id
                )
                self.add_to_stack((bookmarks_toolbar, child))
                self.bookmarks.append(bookmarks_toolbar)
            elif child.get("unfiled.bookmarks.folder") == "true":
                index = len(self.bookmarks) - 1
                other_bookmarks = self.parse_folder(
                    item=child, index=index, parent_id=root.id
                )
                self.add_to_stack((other_bookmarks, child))
                self.bookmarks.append(other_bookmarks)
            else:
                menu_children.append(child)
        if menu_children:
            self.iterate_folder(
                mode="root", folder=bookmarks_menu, children=menu_children
            )

    def parse_chrome_root_to_db(self, root):
        other_children = []
        for child in self.tree.children:
            if child.name == "h3":
                if child.get("personal_toolbar_folder") == "true":
                    index = len(self.bookmarks) - 1
                    bookmarks_bar = self.parse_folder(
                        item=child, index=index, parent_id=root.id
                    )
                    self.add_to_stack((bookmarks_bar, child))
                    self.bookmarks.append(bookmarks_bar)
            else:
                other_children.append(child)
        if other_children:
            index = len(self.bookmarks) - 1
            other_bookmarks = Folder(
                _id=self.id_manager(),
                index=index,
                parent_id=root.id,
                title="Other Bookmarks",
            )
            self.bookmarks.append(other_bookmarks)
            self.iterate_folder(
                mode="root", folder=other_bookmarks, children=other_children
            )

    def iterate_folder(self, mode, stack_item=None, folder=None, children=None):
        """
        Function that appends the folders children, and adds any new folders to the stack.
        """
        if mode == "root":
            folder = folder
            children = children
        elif mode == "folder":
            folder, node = stack_item
            children = node.children

        if self.mode == "json":
            parent_id = folder.get("id")
            for index, child in enumerate(children):
                item = self.child_type_check(child, index, parent_id)
                folder.get("children").append(item)
        else:
            parent_id = folder.id
            for index, child in enumerate(children):
                item = self.child_type_check(child, index, parent_id)
                self.bookmarks.append(item)

    def child_type_check(self, child, index, parent_id):
        """
        Function checks if the child element is a hyperlink <A> or a folder <H3>, parses the child, and adds to stack if child is a folder.
        """
        if child.name == "a":
            item = self.parse_url(child, index, parent_id)
        elif child.name == "h3":
            item = self.parse_folder(child, index, parent_id)
            self.add_to_stack((item, child))
        return item

    def add_to_stack(self, stack_item):
        """
        Function to check that the node has contents before adding it to the stack
        """
        node = stack_item[1]
        if node.contents:
            self.stack.append(stack_item)

    def parse_folder(self, item, index, parent_id):
        """
        Function to parse a given folder into a dictionary object.
        """
        if self.mode == "json":
            folder = {
                "type": "folder",
                "id": self.id_manager(),
                "index": index,
                "parent_id": parent_id,
                "title": item.get("title"),
                "date_added": item.get("add_date"),
                "children": [],
            }
        else:
            folder = Folder(
                _id=self.id_manager(),
                index=index,
                parent_id=parent_id,
                title=item.get("title"),
                date_added=item.get("add_date"),
            )
        return folder

    def parse_url(self, item, index, parent_id):
        """
        Function to parse a given hyperlink into a dictionary object.
        """
        if self.mode == "json":
            url = {
                "type": "url",
                "id": self.id_manager(),
                "index": index,
                "parent_id": parent_id,
                "url": item.get("href"),
                "title": item.get("title"),
                "date_added": item.get("add_date"),
                "icon": item.get("icon"),
                "iconuri": item.get("icon_uri"),
                "tags": item.get("tags"),
            }
        else:
            url = Url(
                _id=self.id_manager(),
                index=index,
                parent_id=parent_id,
                url=item.get("href"),
                title=item.get("title"),
                date_added=item.get("add_date"),
                icon=item.get("icon"),
                icon_uri=item.get("icon_uri"),
                tags=item.get("tags"),
            )
        return url

    def id_manager(self):
        """
        Function to increment the id of the folders/hyperlinks.
        """
        the_id = self.id
        self.id += 1
        return the_id


class BookmarksParserJSON(HTMLMixin):
    def __init__(self, filepath):

        self.new_filepath = (
            os.path.dirname(filepath) + "/new_" + os.path.basename(filepath)
        )

        with open(filepath, "r", encoding="Utf-8") as f:
            self.tree = json.load(f)

        if self.tree.get("checksum"):
            self.source = "Chrome"
            self.tree = {
                "title": "root",
                "id": 0,
                "children": [folder for folder in self.tree.get("roots").values()],
            }
        elif self.tree.get("root"):
            self.source = "Firefox"
            for child in self.tree.get("children"):
                if child.get("title") == "menu":
                    child["title"] = "Bookmarks Menu"
                elif child.get("title") == "toolbar":
                    child["title"] = "Bookmarks Toolbar"
                elif child.get("title") == "unfiled":
                    child["title"] = "Other Bookmarks"
                elif child.get("title") == "mobile":
                    child["title"] = "Mobile Bookmarks"
        else:
            self.source = "Bookmarkie"

    def convert_to_html(self):
        if self.source == "Firefox":
            self.stack = []
            for child in self.tree.get("children")[::-1]:
                if child.get("title") == "Bookmarks Menu":
                    self.stack.extend(child.get("children")[::-1])
                else:
                    self.stack.append(child)
        else:
            self.stack = self.tree.get("children")[::-1]
        self.parse_root_html()

    def save_to_html(self):

        output_file = self.new_filepath.replace(".json", ".html")

        with open(output_file, "w", encoding="Utf-8") as f:
            f.write(self.bookmarks)

    def convert_to_db(self):
        self.bookmarks = []
        # contains tuples (folder, index, parent_id).
        self.stack = []
        root = Folder(_id=1, title="root", index=0, parent_id=0, date_added=time.time())
        self.bookmarks.append(root)

        for index, folder in enumerate(self.tree.get("children")):
            self.stack.append((folder, index, root.get("id")))

        while self.stack:
            stack_item = self.stack.pop()
            self.iterate_folder_db(stack_item)

    def save_to_db(self):
        database_path = "sqlite:///" + self.new_filepath.replace(".json", ".db")
        engine = create_engine(database_path, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        remove(Bookmark, "before_insert", indexer)
        Base.metadata.create_all(engine)
        session.commit()
        session.bulk_save_objects(self.bookmarks)
        session.commit()

    def iterate_folder_db(self, stack_item):
        item, index, parent_id = stack_item
        _id, title, index, date_added = self.get_properties(item, index)
        folder = Folder(
            _id=_id,
            title=title,
            index=index,
            parent_id=parent_id,
            date_added=date_added,
        )
        self.bookmarks.append(folder)

        parent_id = _id
        children = item.get("children")
        if children:
            for index, child in enumerate(children):
                _id, title, index, date_added = self.get_properties(child, index)

                if child.get("type") in ("folder", "text/x-moz-place-container"):
                    contents = child.get("children")
                    if contents:
                        self.stack.append((child, index, parent_id))
                else:
                    if self.source == "Firefox":
                        url = child.get("uri")
                    else:
                        url = child.get("url")
                    url = Url(
                        _id=_id,
                        title=title,
                        url=url,
                        index=index,
                        parent_id=parent_id,
                        date_added=date_added,
                        icon=child.get("icon"),
                        icon_uri=child.get("iconuri"),
                        tags=child.get("tags"),
                    )
                    self.bookmarks.append(url)

    def get_properties(self, item, index):
        _id = int(item.get("id"))
        if self.source == "Chrome":
            _id += 1
            title = item.get("name")
            index = index
        else:
            title = item.get("title")
            index = item.get("index")

        if self.source == "Firefox":
            date_added = item.get("dateAdded")
        else:
            date_added = item.get("date_added")
        return (_id, title, index, date_added)


class BookmarksParserDB(HTMLMixin):
    def __init__(self, filepath):

        self.new_filepath = (
            os.path.dirname(filepath) + "/new_" + os.path.basename(filepath)
        )

        database_path = "sqlite:///" + filepath
        engine = create_engine(database_path)
        Session = sessionmaker(bind=engine)
        session = Session()
        self.tree = session.query(Bookmark).get(1)
        self.source = "Database"

    def convert_to_html(self):
        self.stack = self.tree.get("children")[::-1]
        self.parse_root_html()

    def save_to_html(self):

        output_file = self.new_filepath.replace(".db", ".html")

        with open(output_file, "w", encoding="Utf-8") as f:
            f.write(self.bookmarks)

    def convert_to_json(self):
        self.stack = []
        self.bookmarks = self.parse_folder(self.tree)
        self.stack.append((self.bookmarks, self.tree))

        while self.stack:
            stack_item = self.stack.pop()
            folder, node = stack_item

            for child in node.children:
                if child.type == "url":
                    item = self.parse_url(child)
                elif child.type == "folder":
                    item = self.parse_folder(child)
                    if child.children:
                        self.stack.append((item, child))
                folder.get("children").append(item)

    def save_to_json(self):
        """
        Function to export the bookmarks as JSON at the same location and with the same name as the original file.
        """
        output_file = self.new_filepath.replace(".db", ".json")

        with open(output_file, "w", encoding="Utf-8") as f:
            json.dump(self.bookmarks, f, ensure_ascii=False)

    def parse_folder(self, folder):
        """
        Function to parse a given folder into a dictionary object.
        """
        folder = {
            "type": "folder",
            "id": folder.id,
            "index": folder.index,
            "parent_id": folder.parent_id,
            "title": folder.title,
            "date_added": folder.date_added,
            "children": [],
        }
        return folder

    def parse_url(self, url):
        """
        Function to parse a given hyperlink into a dictionary object.
        """
        url = {
            "type": "url",
            "id": url.id,
            "index": url.index,
            "parent_id": url.parent_id,
            "url": url.url,
            "title": url.title,
            "date_added": url.date_added,
            "icon": url.icon,
            "iconuri": url.icon_uri,
            "tags": url.tags,
        }
        return url
