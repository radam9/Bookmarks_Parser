import json
import os
import re
import time

from bs4 import BeautifulSoup, Tag

from models import (
    Base,
    Bookmark,
    Folder,
    HTMLBookmark,
    JSONBookmark,
    Node,
    Url,
    create_engine,
    sessionmaker,
)


class BookmarksParserMixin:
    """Mixin containing all the core Bookmarks Parser functionality, which is
    later inherited by either the Iteration or Recursion parser."""

    def from_db(self, filepath):
        """Import the DB bookmarks file into self.tree as an object."""
        self.new_filepath = (
            os.path.dirname(filepath) + "/output_" + os.path.basename(filepath)
        )
        database_path = "sqlite:///" + filepath
        engine = create_engine(database_path)
        Session = sessionmaker(bind=engine)
        session = Session()
        self.tree = session.query(Bookmark).get(1)

    def save_to_db(self):
        """Function to export the bookmarks as SQLite3 DB."""
        database_path = "sqlite:///" + os.path.splitext(self.new_filepath)[0] + ".db"
        engine = create_engine(database_path, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        session.commit()
        session.bulk_save_objects(self.bookmarks)
        session.commit()

    def from_html(self, filepath):
        """Imports the HTML Bookmarks file into self.tree as a modified soup
        object using the TreeBuilder class HTMLBookmark, which adds property
        access to the html attributes of the soup object."""
        self.new_filepath = (
            os.path.dirname(filepath) + "/output_" + os.path.basename(filepath)
        )
        self.format_html_file(filepath, self.new_filepath)
        with open(self.new_filepath, "r") as file_:
            soup = BeautifulSoup(
                markup=file_,
                features="html.parser",
                from_encoding="Utf-8",
                element_classes={Tag: HTMLBookmark},
            )
        HTMLBookmark.reset_id_counter()
        tree = soup.find("h3")
        self._restructure_root(tree)
        self._add_index()

    @staticmethod
    def format_html_file(filepath, output_filepath):
        """Takes in an absolute path to a HTML Bookmarks file, it creates a new
        Bookmarks file with the text "output_" prepeneded to the filename.
        where;
        - The main "<H1>" tag is converted to "<H3>" and acts as the root folder
        - All "<DT>" tags are removed.
        - "<H3>" acts as folders and list containers instead of "<DL>".
        - All "<H3>" and "<A>" tag's inner text are added as a "title"
        attribute within the html element.

        :param filepath: absolute path to bookmarks html file.
        :type filepath: str
        :param output_filepath: absolute path and name for output file.
        :type output_filepath: str"""
        with open(filepath, "r") as file_:
            lines = iter(file_.readlines())

        # regex to select an entire H1/H3/A HTML element
        element = re.compile(r"(<(H1|H3|A))(.*?(?=>))>(.*)(<\/\2>)\n")

        # TODO: maybe change the list comprehensions to Generator Comprehension
        # or some other method for better efficiency (time/memory)

        lines1 = iter(element.sub(r'\1\3 TITLE="\4">\5', line) for line in lines)
        lines2 = iter(
            line.replace("<DT>", "") for line in lines1 if "<DL><p>" not in line
        )
        lines3 = iter(
            line.replace("<H1", "<H3")
            .replace("</H1>", "")
            .replace("</H3>", "")
            .replace("</DL><p>\n", "</H3>")
            .replace("\n", "")
            .strip()
            for line in lines2
        )

        with open(output_filepath, "w") as file_:
            file_.writelines(lines3)

    def _restructure_root(self, tree):
        """Restructure the root of the HTML parsed tree to allow for an easier
        processing.

        If the tree title is 'Bookmarks Menu' we need to extract the two folders
        'Bookmarks Toolbar' and 'Other Bookmarks', then insert them into the
        root folders children.

        If the tree title is 'Bookmarks' we need to extract the 'Bookmarks bar'
        folder and insert it at the beggining of the root children. Then we need
        to rename the 'Bookmarks' folder to 'Other Bookmarks'."""
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
        self.tree.children.append(tree)
        if tree.title == "Bookmarks Menu":
            for i, child in enumerate(tree):
                if child.title in ("Bookmarks Toolbar", "Other Bookmarks"):
                    self.tree.children.append(tree.children.pop(i))
        elif tree.title == "Bookmarks":
            tree.title = "Other Bookmarks"
            for i, child in enumerate(tree):
                if child.title == "Bookmarks bar":
                    self.tree.children.insert(0, tree.children.pop(i))
                    break

    def save_to_html(self):
        """Export the bookmarks as HTML."""
        output_file = os.path.splitext(self.new_filepath)[0] + ".html"
        with open(output_file, "w", encoding="Utf-8") as file_:
            file_.write(self.bookmarks)

    def from_json(self, filepath):
        """Imports the JSON Bookmarks file into self.tree as a
        JSONBookmark object."""
        self.new_filepath = (
            os.path.dirname(filepath) + "/output_" + os.path.basename(filepath)
        )
        self.format_json_file(filepath, self.new_filepath)
        # with object_hook the json tree is loaded as JSONBookmark object tree.
        with open(self.new_filepath, "r") as file_:
            self.tree = json.load(
                file_, object_hook=self._json_to_object, encoding="Utf-8"
            )
        if self.tree.source == "Chrome":
            self._add_index_and_id()

    @staticmethod
    def _json_to_object(jdict):
        """Helper function used as object_hook for json load."""
        return JSONBookmark(**jdict)

    @staticmethod
    def format_json_file(filepath, output_filepath):
        """Reads Chrome/Firefox/Bookmarkie JSON bookmarks file (at filepath),
        and modifies it to a standard format to allow for easy
        parsing/converting.
        Exporting the result to a new JSON file (output_filepath) with
        a prefix of 'output_'."""
        with open(filepath, "r", encoding="Utf-8") as file_:
            tree = json.load(file_)

        if tree.get("checksum"):
            tree = {
                "name": "root",
                "id": 0,
                "index": 0,
                "parent_id": 0,
                "type": "folder",
                "date_added": 0,
                "children": list(tree.get("roots").values()),
            }
        elif tree.get("root"):
            folders = {
                "menu": "Bookmarks Menu",
                "toolbar": "Bookmarks Toolbar",
                "unfiled": "Other Bookmarks",
                "mobile": "Mobile Bookmarks",
            }
            for child in tree.get("children"):
                child["title"] = folders[child.get("title")]

        with open(output_filepath, "w", encoding="Utf-8") as file_:
            json.dump(tree, file_, ensure_ascii=False)

    def save_to_json(self):
        """Function to export the bookmarks as JSON."""
        output_file = os.path.splitext(self.new_filepath)[0] + ".json"
        with open(output_file, "w", encoding="Utf-8") as file_:
            json.dump(self.bookmarks, file_, ensure_ascii=False)

    def convert_to_json_using_encoder(self):
        """Converts the bookmarks tree into JSON, using the `json.dump()`
        while overriding the `default()` function located inside JSONEncoder
        with the `self.default()` method by passing it in as a parameter.
        NOTE: This method is slower than the iteration convert_to_json()"""
        output_file = os.path.splitext(self.new_filepath)[0] + ".json"
        with open(output_file, "w", encoding="Utf-8") as file_:
            json.dump(obj=self.tree, fp=file_, ensure_ascii=False, default=self.default)

    def _add_index(self):
        """Add index to each element if tree source is HTML or JSON(Chrome)"""
        stack = [self.tree]
        while stack:
            stack_item = stack.pop()
            for i, child in enumerate(stack_item, 0):
                child.index = i
                if child.type == "folder":
                    stack.append(child)

    @staticmethod
    def default(jobj):
        """JSON Bookmarks Serializing function,
        passed into `json.dump()` to serialize the JSONBookmark Objects
        into a dictionary"""
        bookmarks = (Bookmark, Folder, Url, Node, JSONBookmark, HTMLBookmark)
        if isinstance(jobj, bookmarks):
            if jobj.type == "folder":
                obj = jobj.create_folder_as_json()
                obj["children"].extend(jobj.children)
                return obj
            elif jobj.type == "url":
                obj = jobj.create_url_as_json()
                return obj
        return json.JSONEncoder.default(o=jobj)


class BookmarksParserIteration(BookmarksParserMixin):
    """Bookmarks Parser class that converts the bookmarks to DB/HTML/JSON, using
    Iteration and Stack."""

    def __init__(self):
        self.bookmarks = None
        self.stack = None
        self.stack_item = None

    def convert_to_db(self):
        """Convert the imported bookmarks to database objects."""
        self.bookmarks = []
        self.stack = [self.tree]

        while self.stack:
            self.stack_item = self.stack.pop()
            self.iterate_folder_db()

    def iterate_folder_db(self):
        """Iterate through each item in the hierarchy tree and create
        a database object, appending any folders that contain children to
        the stack for futher proccessing."""
        folder = self.stack_item.create_folder_as_db()
        self.bookmarks.append(folder)
        parent_id = folder.id
        for child in self.stack_item:
            child.parent_id = parent_id
            if child.type == "folder":
                if child.children:
                    self.stack.append(child)
                else:
                    folder = child.create_folder_as_db()
                    self.bookmarks.append(folder)
            else:
                url = child.create_url_as_db()
                self.bookmarks.append(url)

    def convert_to_html(self):
        """Convert the imported bookmarks to HTML."""
        header = """<!DOCTYPE NETSCAPE-Bookmark-file-1>\n<!-- This is an automatically generated file.\n     It will be read and overwritten.\n     DO NOT EDIT! -->\n<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks Menu</H1>\n<DL><p>\n"""
        footer = "</DL>"

        self.stack = self.tree.children[::-1]
        self.proccessed = []

        while self.stack:
            self.stack_item = self.stack.pop()
            folder = self.iterate_folder_html()
            if not folder:
                continue
            placeholder = f"<folder{self.stack_item.id}>"
            if self.proccessed and (placeholder in self.proccessed[-1]):
                self.proccessed[-1] = self.proccessed[-1].replace(placeholder, folder)
            else:
                self.proccessed.append(folder)

        temp = [header]
        temp.extend(self.proccessed)
        temp.append(footer)
        self.bookmarks = "".join(temp)

    def iterate_folder_html(self):
        """Iterate through each item in the hierarchy tree and convert it to
        HTML. If a folder has children, it is added to the stack and a
        placeholder is left in its place so it can be inserted back to its
        position after processing."""
        folder = [self.stack_item.create_folder_as_html(), "<DL><p>\n"]
        list_end = "</DL><p>\n"
        for child in self.stack_item:
            if child.type == "folder":
                item = f"<folder{child.id}>"
                self.stack.append(child)
            else:
                item = child.create_url_as_html()
            folder.append(item)
        folder.append(list_end)
        result = "".join(folder)
        return result

    def convert_to_json(self):
        """Convert the imported bookmarks to JSON."""
        self.stack = []
        self.bookmarks = self.tree.create_folder_as_json()
        self.stack.append((self.bookmarks, self.tree))

        while self.stack:
            self.stack_item = self.stack.pop()
            folder, node = self.stack_item
            children = folder.get("children")
            for child in node:
                if child.type == "folder":
                    item = child.create_folder_as_json()
                    if child.children:
                        self.stack.append((item, child))
                else:
                    item = child.create_url_as_json()
                children.append(item)


# [X] Chrome JSON bookmarks don't have index

# [X] _add_id_and_index , _add_index are very similar, a way to factor
# similarities?

# [X] create a function that adds id/index to the element depending
#  on its source json/chrome or html.

# [X] convert the for loops from using a list to using an iterator (.children)

# [X] to iterate over the children of an item, iterate of the item itself.

# [X] after importing an HTML file, we need to reset the HTMLBookmark
# counter = itertools.count() to 2

# [x] convert_to_json_using_encoder() has not been tested with a big hierarchy
# object, it has been tested on a small nested object and worked.
# check the 'default=' parameter in json.dump()
# now the function is fully functional

# [X] use itertools.count(start=2) instead of global ID counter.

# [x] check for improvements for _format_html_file() function.

# [X] list_name.append() gets reevaluated everytime its called, it's better to
# append_to_list = list_name.append(), and put append_to_list inside the loop
# instead
# NOTE: No need since the number of times it is executed in this app isn't that
# high

# [/] Try to create a unified iteration function, that converts from any form
# (DB/HTML/JSON) to any form (DB/HTML/JSON)
# NOTE: Does not seems possible

# [] Try to create a unified recursive function, that converts from any form
# (DB/HTML/JSON) to any form (DB/HTML/JSON)

# [] check if I need to split the BookmarksParserMixin into different Mixins.

# [] iteration/recursion functions take in an extra argument "addon"
# that takes a function as input, it is later used to run a function
# _add_index if it is provided. as follows:
# add_index = function if function else None
# NOTE: the stack_item and index needs to be bound to self (self.stack_item)
# and (self.index) for this way to work

# [] Likewise there should be a sort of switch that toggles whether it is
# required to add parent_id to the items or not (only if converting to DB)

# [] Maybe its possible to completely remove the string/regex substitution in
# format_html_file() if I read more into BS4 and its options
# custom parser / TreeBuilder / Soupstrainer / Tag class

# [] check iterate_folder_html() possible bug when folder is empty.

# [] different way to create a HTML document from an Object.

# [] iterate_folder_db() will currently not work due to the lack of
# index and parent_id, and a mismatch of the items read and added to the stack.

# [] in line format_json_file in thr "checksum" branch modified the generator
# from: "children": [folder for folder in tree.get("roots").values()],
# to: "children": list(tree.get("roots").values(),
