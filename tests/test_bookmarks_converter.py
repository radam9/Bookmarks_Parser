import json
from filecmp import cmp
from pathlib import Path

from bookmarks_converter import BookmarksConverter
from bookmarks_converter.core import JSONMixin
from bookmarks_converter.models import Folder, JSONBookmark


class Test_DBMixin:
    def test_parse_db(self, result_bookmark_files, get_data_from_db):
        file_path = result_bookmark_files["from_chrome_html.db"]
        instance = BookmarksConverter(file_path)
        instance.parse_db()
        bookmarks, _, _ = get_data_from_db(file_path, "Chrome")
        assert bookmarks[0] == instance.tree

    def test_iterate_folder_db(self):
        # TODO:
        pass

    def test_convert_to_db(self):
        # TODO:
        pass

    def test_save_to_db(self, get_data_from_db):
        file_path = "temp.db"
        bookmarks = list()
        for i in range(1, 11):
            parent_id = None if i == 0 else 0
            bookmarks.append(
                Folder(date_added=0, index=0, _id=i, parent_id=parent_id, title="Title")
            )
        instance = BookmarksConverter(file_path)
        instance.bookmarks = bookmarks
        instance.save_to_db()
        output_file = instance.output_filepath
        temp_bookmarks, _, _ = get_data_from_db(output_file, None)
        assert bookmarks == temp_bookmarks
        output_file.unlink()


class Test_HTMLMixin:
    def test_parse_html(self):
        # TODO:
        pass

    def test_format_html_file(self):
        # TODO:
        pass

    def test_restructure_root(self):
        # TODO:
        pass

    def test_convert_to_html(self):
        # TODO:
        pass

    def test_iterate_folder_html(self):
        # TODO:
        pass

    def test_create_placeholder(self):
        # TODO:
        pass

    def test_save_to_html(self):
        # TODO:
        pass


class Test_JSONMixin:
    def test_parse_json(self):
        # TODO:
        pass

    def test_json_to_object(self, folder_custom):
        folder = JSONMixin._json_to_object(folder_custom)
        assert isinstance(folder, JSONBookmark)

    def test_format_json_file_chrome(self, source_bookmark_files, read_json):
        source_file = source_bookmark_files["bookmarks_chrome.json"]
        output_file = Path(source_file).with_name("temporary.json")
        BookmarksConverter.format_json_file(source_file, output_file)
        json_data = read_json(output_file)

        assert json_data.get("name") == "root"
        assert json_data.get("children")[0].get("name") == "Bookmarks bar"
        assert json_data.get("children")[1].get("name") == "Other Bookmarks"
        output_file.unlink()

    def test_format_json_file_firefox(self, source_bookmark_files, read_json):
        source_file = source_bookmark_files["bookmarks_firefox.json"]
        output_file = Path(source_file).with_name("temporary.json")
        BookmarksConverter.format_json_file(source_file, output_file)
        json_data = read_json(output_file)
        root_children = json_data.get("children")
        assert root_children[0].get("title") == "Bookmarks Menu"
        assert root_children[1].get("title") == "Bookmarks Toolbar"
        assert root_children[2].get("title") == "Other Bookmarks"
        assert root_children[3].get("title") == "Mobile Bookmarks"
        output_file.unlink()

    def test_convert_to_json(self):
        # TODO:
        pass

    def test_save_to_json(self, result_bookmark_files):
        result_file = result_bookmark_files["from_firefox_html.json"]
        instance = BookmarksConverter(result_file)
        with open(result_file, "r", encoding="utf-8") as file_:
            instance.bookmarks = json.load(file_)
        output_file = Path(result_file).with_name("output_file.json")
        instance.output_filepath = output_file
        instance.save_to_json()
        assert cmp(result_file, output_file, shallow=False)
        output_file.unlink()


class Test_BookmarksConverter:
    def test_init(self):
        file_path = Path("/home/user/Downloads/source/bookmarks.html")
        output_file = file_path.with_name(f"output_{file_path.name}")
        temp_file = file_path.with_name(f"temp_{file_path.name}")
        instance = BookmarksConverter(str(file_path))
        assert instance.bookmarks is None
        assert instance.stack is None
        assert instance.stack_item is None
        assert instance.tree is None
        assert instance.filepath == file_path
        assert isinstance(instance.filepath, Path)
        assert instance.output_filepath == output_file
        assert instance.temp_filepath == temp_file

    def test_prepare_filepaths(self):
        filename = "/home/user/Downloads/source/bookmarks.html"
        temp_filepath = Path("/home/user/Downloads/source/temp_bookmarks.html")
        output_filepath = Path("/home/user/Downloads/source/output_bookmarks.html")
        bookmarks = BookmarksConverter(filename)

        assert temp_filepath == bookmarks.temp_filepath
        assert output_filepath == bookmarks.output_filepath

    def test_add_index(self):
        # TODO:
        pass
