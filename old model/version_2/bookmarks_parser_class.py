from bs4 import BeautifulSoup


class Bookmarks_Parser:
    ID = 1
    Bookmarks = []

    def __new__(self, bookmarks_file):
        with open(bookmarks_file, encoding="Utf-8") as f:
            soup = BeautifulSoup(markup=f, features="html5lib", from_encoding="Utf-8")
        # Check if HTML Bookmark version is Chrome or Firefox
        # Prepare the data to be parsed
        # Parse the root of the bookmarks tree
        heading = soup.find("h1")
        root = soup.find("dl")
        self.bookmarks = {}
        if heading.text == "Bookmarks":
            self.bookmarks = self.parse_root_chrome(root)
        elif heading.text == "Bookmarks Menu":
            self.bookmarks = self.parse_root_firefox(root)

    @staticmethod
    def indexer(item, index):
        """
        Add position index for urls and folders
        """
        if item.get("type") in {"url", "folder"}:
            item["index"] = index
            index += 1
        return index

    @staticmethod
    def parse_url(child, parent_id):
        """
        Function that parses a url tag <DT><A>
        """
        result = {
            "type": "url",
            "id": Bookmarks_Parser.ID,
            "index": None,
            "parent_id": parent_id,
            "url": child.get("href"),
            "title": child.text,
            "date_added": child.get("add_date"),
            "icon": child.get("icon"),
        }
        Bookmarks_Parser.ID += 1
        # getting icon_uri & tags are only applicable in Firefox
        icon_uri = child.get("icon_uri")
        if icon_uri:
            result["icon_uri"] = icon_uri
        tags = child.get("tags")
        if tags:
            result["tags"] = tags.split(",")
        return result

    @staticmethod
    def parse_folder(child, parent_id):
        """
        Function that parses a folder tag <DT><H3>
        """
        result = {
            "type": "folder",
            "id": Bookmarks_Parser.ID,
            "index": None,
            "parent_id": parent_id,
            "title": child.text,
            "date_added": child.get("add_date"),
            "date_modified": child.get("last_modified"),
            "special": None,
            "children": [],
        }
        Bookmarks_Parser.ID += 1
        # for Bookmarks Toolbar in Firefox and Bookmarks bar in Chrome
        if child.get("personal_toolbar_folder"):
            result["special"] = "toolbar"
        # for Other Bookmarks in Firefox
        if child.get("unfiled_bookmarks_folder"):
            result["special"] = "other_bookmarks"
        return result

    @staticmethod
    def recursive_parse(node, parent_id):
        """
        Function that recursively parses folders and lists <DL><p>
        """
        index = 0
        # case were node is a folder
        if node.name == "dt":
            folder = self.parse_folder(node.contents[0], parent_id)
            items = self.recursive_parse(node.contents[2], folder["id"])
            folder["children"] = items
            return folder
        # case were node is a list
        elif node.name == "dl":
            data = []
            for child in node:
                tag = child.contents[0].name
                if tag == "h3":
                    folder = self.recursive_parse(child, parent_id)
                    index = self.indexer(folder, index)
                    data.append(folder)
                elif tag == "a":
                    url = self.parse_url(child.contents[0], parent_id)
                    index = self.indexer(url, index)
                    data.append(url)
            return data

    @staticmethod
    def parse_root_firefox(root):
        """
        Function to parse the root of the firefox bookmark tree
        """
        # create bookmark menu folder and give it an ID
        bookmarks = {
            "type": "folder",
            "id": Bookmarks_Parser.ID,
            "index": 0,
            "parent_id": 0,
            "title": "Bookmarks Menu",
            "date_added": None,
            "date_modified": None,
            "special": "main",
            "children": [],
        }
        Bookmarks_Parser.ID += 1
        index = 0  # index for bookmarks/bookmarks menu
        main_index = 1  # index for root level
        result = [0]  # root contents
        for node in root:
            # skip node if not <DT>
            if node.name != "dt":
                continue
            # get tag of first node child
            tag = node.contents[0].name
            if tag == "a":
                url = self.parse_url(node.contents[0], 1)
                index = self.indexer(node, index)
                bookmarks["children"].append(url)
            if tag == "h3":
                folder = self.recursive_parse(node, 1)
                # check for special folders (Other Bookmarks / Toolbar)
                # add them to root level instead of inside bookmarks
                if folder["special"]:
                    folder["parent_id"] = 0
                    main_index = self.indexer(folder, main_index)
                    result.append(folder)
                else:
                    index = self.indexer(folder, index)
                    bookmarks["children"].append(folder)

        result[0] = bookmarks
        return result

    @staticmethod
    def parse_root_chrome(root):
        """
        Function to parse the root of the chrome bookmark tree
        """
        # Create "other bookmarks" folder and give it an ID
        other_bookmarks = {
            "type": "folder",
            "id": Bookmarks_Parser.ID,
            "index": 1,
            "parent_id": 0,
            "title": "Other Bookmarks",
            "date_added": None,
            "date_modified": None,
            "special": "other_bookmarks",
            "children": [],
        }
        Bookmarks_Parser.ID += 1
        result = [0]
        index = 0
        for node in root:
            if node.name != "dt":
                continue
            # get the first child element (<H3> or <A>)
            element = node.contents[0]
            tag = element.name
            # if an url tag is found at root level, add it to "Other Bookmarks" children
            if tag == "a":
                url = self.parse_url(node.contents[0], 1)
                index = self.indexer(node, index)
                other_bookmarks["children"].append(url)
            elif tag == "h3":
                # if a folder tag is found at root level, check if its the main "Bookmarks Bar", else append to "Other Bookmarks" children
                if element.get("personal_toolbar_folder"):
                    folder = recursive_parse(node, 0)
                    folder["index"] = 0
                    folder["special"] = "main"
                    result[0] = folder
                else:
                    parent_id = other_bookmarks["id"]
                    folder = self.recursive_parse(node, parent_id)
                    index = self.indexer(folder, index)
                    other_bookmarks["children"].append(folder)
        # add "Other Bookmarks" folder to root if it has children
        if len(other_bookmarks["children"]) > 0:
            result.append(other_bookmarks)
        return result


source = "/home/vagabond/Downloads/booky/temp_helper_files/bookmarks/bookmarks_chrome_2020_07_20.html"

result = Bookmarks_Parser(source)
x = 0
