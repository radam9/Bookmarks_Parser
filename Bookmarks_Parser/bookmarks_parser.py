import json
import os
import re
import time

from bs4 import BeautifulSoup, Tag

from models import Base, Bookmark, Folder, Url, create_engine, sessionmaker
from node import HTMLBookmark, JSONBookmark


class BookmarksParserMixin:
    """
    Mixin containing all the core Bookmarks Parser functionality, which is later
    inherited by either the Iteration or Recursion parser.
    """

    def from_db(self, filepath):
        """
        Import the DB bookmarks file into self.tree as an object.
        """
        self.new_filepath = (
            os.path.dirname(filepath) + "/output_" + os.path.basename(filepath)
        )
        database_path = "sqlite:///" + filepath
        engine = create_engine(database_path)
        Session = sessionmaker(bind=engine)
        session = Session()
        self.tree = session.query(Bookmark).get(1)

    def save_to_db(self):
        """
        Function to export the bookmarks as SQLite3 DB.
        """
        database_path = "sqlite:///" + os.path.splitext(self.new_filepath)[0] + ".db"
        engine = create_engine(database_path, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        session.commit()
        session.bulk_save_objects(self.bookmarks)
        session.commit()

    def from_html(self, filepath):
        """
        Imports the HTML Bookmarks file into self.tree as a modified soup
        object using the TreeBuilder class HTMLBookmark, which adds property
        access to the html attributes of the soup object.
        """
        self.new_filepath = (
            os.path.dirname(filepath) + "/output_" + os.path.basename(filepath)
        )
        self.format_html_file(filepath, self.new_filepath)
        with open(self.new_filepath, "r") as f:
            soup = BeautifulSoup(
                markup=f,
                features="html.parser",
                from_encoding="Utf-8",
                element_classes={Tag: HTMLBookmark},
            )

        tree = soup.find("h3")
        self._restructure_root(tree)
        # set the id counter, will be used to add IDs to all elements when
        # converting the html bookmarks tree to JSON/DB.
        self.id = 1

    @staticmethod
    def format_html_file(filepath, output_filepath):
        """
        Takes in an absolute path to a HTML Bookmarks file, it creates a new Bookmarks file with the text "output_" prepeneded to the filename. where,
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

        # TODO: maybe change the list comprehensions to Generator Comprehension for better efficiency

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

        with open(output_filepath, "w") as f:
            f.writelines(lines3)

    def _restructure_root(self, tree):
        """
        Restructure the root of the HTML parsed tree to allow for an easier
        processing.

        If the tree title is 'Bookmarks Menu' we need to extract the two folders
        'Bookmarks Toolbar' and 'Other Bookmarks', then insert them into the
        root folders children.

        If the tree title is 'Bookmarks' we need to extract the 'Bookmarks bar'
        folder and insert it at the beggining of the root children. Then we need
        to rename the 'Bookmarks' folder to 'Other Bookmarks'.
        """
        self.tree = HTMLBookmark(
            name="h3",
            attrs={
                "id": 1,
                "index": 0,
                "parent_id": 0,
                "title": "root",
                "date_added": round(time.time() * 1000),
            },
        )
        self.tree.contents.append(tree)
        if tree.title == "Bookmarks Menu":
            for i, child in enumerate(tree):
                if child.title in ("Bookmarks Toolbar", "Other Bookmarks"):
                    self.tree.contents.append(tree.contents.pop(i))
        elif tree.title == "Bookmarks":
            tree.title = "Other Bookmarks"
            for i, child in enumerate(tree):
                if child.title == "Bookmarks bar":
                    self.tree.contents.insert(0, tree.contents.pop(i))
                    break

    def save_to_html(self):
        """
        Export the bookmarks as HTML.
        """
        output_file = os.path.splitext(self.new_filepath)[0] + ".html"
        with open(output_file, "w", encoding="Utf-8") as f:
            f.write(self.bookmarks)

    def from_json(self, filepath):
        """
        Imports the JSON Bookmarks file into self.tree as a
        JSONBookmark object.
        """
        self.new_filepath = (
            os.path.dirname(filepath) + "/output_" + os.path.basename(filepath)
        )
        self.format_json_file(filepath, self.new_filepath)
        # with object_hook the json is loaded as JSONBookmark object.
        with open(self.new_filepath, "r") as f:
            self.tree = json.load(f, object_hook=self._json_to_object, encoding="Utf-8")
        if self.tree.source == "Chrome":
            self._add_index()

    @staticmethod
    def format_json_file(filepath, output_filepath):
        """
        Reads Chrome/Firefox/Bookmarkie JSON bookmarks file (at filepath),
        and modifies it to a standard format to allow for easy
        parsing/converting.
        Exporting the result to a new JSON file (output_filepath) with
        a prefix of 'output_'.
        """
        with open(filepath, "r", encoding="Utf-8") as f:
            tree = json.load(f)

        if tree.get("checksum"):
            tree = {
                "name": "root",
                "id": 0,
                "type": "folder",
                "date_added": 0,
                "children": [folder for folder in tree.get("roots").values()],
            }
        elif tree.get("root"):
            for child in tree.get("children"):
                if child.get("title") == "menu":
                    child["title"] = "Bookmarks Menu"
                elif child.get("title") == "toolbar":
                    child["title"] = "Bookmarks Toolbar"
                elif child.get("title") == "unfiled":
                    child["title"] = "Other Bookmarks"
                elif child.get("title") == "mobile":
                    child["title"] = "Mobile Bookmarks"

        with open(output_filepath, "w", encoding="Utf-8") as f:
            json.dump(tree, f, ensure_ascii=False)

    def save_to_json(self):
        """
        Function to export the bookmarks as JSON.
        """
        output_file = os.path.splitext(self.new_filepath)[0] + ".json"
        with open(output_file, "w", encoding="Utf-8") as f:
            json.dump(self.bookmarks, f, ensure_ascii=False)

    def _add_index_and_id(self):
        """Add index and id to a stack_item. used for HTML Bookmarks that don't
        have neither id or index"""
        self.stack_item.index = self.index
        self.stack_item.id = self.id
        self.id += 1

        # id_ = 2
        # stack = [self.tree]

        # while stack:
        #     stack_item = stack.pop()

        #     for i, child in enumerate(stack_item, 0):
        #         child.id = id_
        #         child.index = i
        #         id_ += 1
        #         if child.type == "folder":
        #             stack.append(child)

    def _add_index(self):
        self.stack_item.index = self.index


class BookmarksParserIteration(BookmarksParserMixin):
    pass


# 1) Chrome JSON bookmarks don't have index

# 2) _add_id_and_index , _add_index are very similar, a way to factor
# similarities?

# 3) Try to create a unified iteration function, that converts from any form
# (DB/HTML/JSON) to any form (DB/HTML/JSON)

# 4) Try to create a unified recursive function, that converts from any form
# (DB/HTML/JSON) to any form (DB/HTML/JSON)

# 5) Iteration/Recursive function needs to be passed in output_format
# to pass it into the Node.create_folder/url

# 6) check if I need to split the BookmarksParserMixin into different Mixins.

# 7) list_name.append() gets reevaluated everytime its called, it's better to
# append_to_list = list_name.append(), and put append_to_list inside the loop
# instead

# 8) create a function that adds id/index to the element depending on its source
# json/chrome or html.

# 9) convert the for loops from using a list to using an iterator (.children)

# 10) to iterate over the children of an item, iterate of the item itself.

# 11) iteration/recursion functions take in an extra argument "addon"
# that takes a function as input, it is later used to run a function
# _add_id_and_index if it is provided. as follows:
# add_id_and_index = function if function else None
# NOTE: the stack_item and index needs to be bound to self (self.stack_item)
# and (self.index) for this way to work

# 12) Likewise thre should be a sort of switch that toggles whether it is
# required to add parent_id to the items or not (only if converting to DB)

# 13) after using the function _add_index_and_id in an iterative/recursive
# function, we need to reset the self.id back to 1.
