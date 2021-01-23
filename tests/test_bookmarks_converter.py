from filecmp import cmp
from pathlib import Path

from bookmarks_converter import BookmarksConverter
from bookmarks_converter.core import JSONMixin
from bookmarks_converter.models import JSONBookmark


class Test_JsonMixin:
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


class Test_BookmarksConverter:
    def test_prepare_filepaths(self):
        filename = "/home/user/Downloads/source/bookmarks.html"
        temp_filepath = Path("/home/user/Downloads/source/temp_bookmarks.html")
        output_filepath = Path("/home/user/Downloads/source/output_bookmarks.html")
        bookmarks = BookmarksConverter(filename)

        assert temp_filepath == bookmarks.temp_filepath
        assert output_filepath == bookmarks.output_filepath
