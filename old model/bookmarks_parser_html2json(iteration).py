from bs4 import BeautifulSoup
import time
import os
import json


class Bookmarks_parser:
    def __init__(self, filepath):

        self.bookmarks = {
            "type": "folder",
            "id": 0,
            "index": 0,
            "parent_id": None,
            "title": "root",
            "date_added": None,
            "date_modified": None,
            "children": [],
        }

        self.filepath = filepath

        with open(self.filepath, "r", encoding="Utf-8") as f:
            self.soup = BeautifulSoup(
                markup=f, features="html.parser", from_encoding="Utf-8"
            )
        self.tree = self.soup.find("h3")
        self.source = "Chrome" if self.tree.get("title") == "Bookmarks" else "Firefox"

        self.id = 1
        # stack containes a tuple of (folder, node).
        # folder being the parsed data, and node being the folder data from the tree.
        self.stack = []

        if self.source == "Chrome":
            self.iterate_chrome()
        elif self.source == "Firefox":
            self.iterate_firefox()

        while self.stack:
            stack_item = self.stack.pop()
            self.iterate_folder(mode="folder", stack_item=stack_item)

    def iterate_firefox(self):
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

    def iterate_chrome(self):
        """
        Function that will format and iterate through a Chrome bookmarks file.
        """
        other_children = []
        for child in self.tree.contents:
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

    def iterate_folder(self, mode, stack_item=None, folder=None, children=None):
        """
        Function that appends the folders children, and adds any new folders to the stack.
        """
        if mode == "root":
            folder = folder
            children = children
        elif mode == "folder":
            folder, node = stack_item
            children = node.contents

        parent_id = folder.get("id")

        for index, child in enumerate(children):
            item = self.child_type_check(child, index, parent_id)
            folder.get("children").append(item)

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
        folder = {
            "type": "folder",
            "id": self.id_manager(),
            "index": index,
            "parent_id": parent_id,
            "title": item.get("title"),
            "date_added": item.get("add_date"),
            "date_modified": item.get("last_modified"),
            "children": [],
        }
        return folder

    def parse_url(self, item, index, parent_id):
        """
        Function to parse a given hyperlink into a dictionary object.
        """
        url = {
            "type": "url",
            "id": self.id_manager(),
            "index": index,
            "parent_id": parent_id,
            "url": item.get("href"),
            "title": item.get("title"),
            "date_added": item.get("add_date"),
            "date_modified": item.get("last_modified"),
            "icon": item.get("icon"),
            "icon_uri": item.get("icon_uri"),
            "tags": item.get("tags"),
        }
        return url

    def id_manager(self):
        """
        Function to increment the id of the folders/hyperlinks.
        """
        the_id = self.id
        self.id += 1
        return the_id

    def save_to_json_file(self):
        """
        Function to export the bookmarks as JSON at the same location and with the same name as the original file.
        """
        output_file = self.filepath.replace(".html", ".json")

        with open(output_file, "w", encoding="Utf-8") as f:
            json.dump(self.bookmarks, f, ensure_ascii=False)
