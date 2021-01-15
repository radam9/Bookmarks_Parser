from filecmp import cmp
from pathlib import Path

from src.bookmarks_converter import BookmarksConverter
from src.bookmarks_converter.core import JSONMixin
from src.bookmarks_converter.models import JSONBookmark


# JSONMixin tests
def test_json_to_object(folder_custom):
    folder = JSONMixin._json_to_object(folder_custom)
    assert isinstance(folder, JSONBookmark)


def test_format_json_file_chrome(source_bookmark_files, read_json):
    source_file = source_bookmark_files["bookmarks_chrome.json"]
    output_file = Path(source_file).with_name("temporary.json")
    BookmarksConverter.format_json_file(source_file, output_file)
    json_data = read_json(output_file)

    assert json_data.get("name") == "root"
    assert json_data.get("children")[0].get("name") == "Bookmarks bar"
    assert json_data.get("children")[1].get("name") == "Other bookmarks"
    Path(output_file).unlink()


def test_format_json_file_firefox(source_bookmark_files, read_json):
    source_file = source_bookmark_files["bookmarks_firefox.json"]
    output_file = Path(source_file).with_name("temporary.json")
    BookmarksConverter.format_json_file(source_file, output_file)
    json_data = read_json(output_file)
    root_children = json_data.get("children")
    assert root_children[0].get("title") == "Bookmarks Menu"
    assert root_children[1].get("title") == "Bookmarks Toolbar"
    assert root_children[2].get("title") == "Other Bookmarks"
    assert root_children[3].get("title") == "Mobile Bookmarks"
    Path(output_file).unlink()


# BookmarksConverter tests
def test_prepare_filepaths():
    filename = "/home/user/Downloads/source/bookmarks.html"
    temp_filepath = "/home/user/Downloads/source/temp_bookmarks.html"
    output_filepath = "/home/user/Downloads/source/output_bookmarks.html"
    bookmarks = BookmarksConverter(filename)

    assert temp_filepath == bookmarks.temp_filepath
    assert output_filepath == bookmarks.output_filepath


def test_from_chrome_html_to_json(
    source_bookmark_files, result_bookmark_files, read_json
):
    result_file = result_bookmark_files["from_chrome_html.json"]
    json_data = read_json(result_file)
    # date_added of "root" folder
    root_date = json_data["date_added"]
    # date_added of "Other Bookmarks" folder
    other_date = json_data["children"][1]["date_added"]
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.html"])
    bookmarks.parse_html()
    bookmarks.convert_to_json()
    bookmarks.bookmarks["date_added"] = root_date
    bookmarks.bookmarks["children"][1]["date_added"] = other_date
    bookmarks.save_to_json()
    output_file = Path(bookmarks.output_filepath).with_suffix(".json")
    assert cmp(result_file, output_file)
    Path(output_file).unlink()


def test_from_chrome_html_to_db(
    source_bookmark_files, result_bookmark_files, get_dates_from_db
):
    result_file = result_bookmark_files["from_chrome_html.db"]
    root_date, other_date = get_dates_from_db(result_file, "Chrome")
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.html"])
    bookmarks.parse_html()
    bookmarks.convert_to_db()
    bookmarks.bookmarks[0].date_added = root_date
    bookmarks.bookmarks[1].date_added = other_date
    bookmarks.save_to_db()
    output_file = Path(bookmarks.output_filepath).with_suffix(".db")
    assert cmp(result_file, output_file)
    Path(output_file).unlink()


def test_from_chrome_json_to_html(source_bookmark_files, result_bookmark_files):
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.json"])
    bookmarks.parse_json()
    bookmarks.convert_to_html()
    bookmarks.save_to_html()
    output_file = Path(bookmarks.output_filepath).with_suffix(".html")
    assert cmp(result_bookmark_files["from_chrome_json.html"], output_file)
    Path(output_file).unlink()


def test_from_chrome_json_to_db(
    source_bookmark_files, result_bookmark_files, get_dates_from_db
):
    result_file = result_bookmark_files["from_chrome_json.db"]
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.json"])
    bookmarks.parse_json()
    bookmarks.convert_to_db()
    bookmarks.save_to_db()
    output_file = Path(bookmarks.output_filepath).with_suffix(".db")
    assert cmp(result_file, output_file)
    Path(output_file).unlink()


def test_from_firefox_html_to_json(
    source_bookmark_files, result_bookmark_files, read_json
):
    result_file = result_bookmark_files["from_firefox_html.json"]
    json_data = read_json(result_file)
    # date_added of "root" folder
    root_date = json_data["date_added"]
    # date_added of "Bookmarks Menu" folder
    menu_date = json_data["children"][0]["date_added"]
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.html"])
    bookmarks.parse_html()
    bookmarks.convert_to_json()
    bookmarks.bookmarks["date_added"] = root_date
    bookmarks.bookmarks["children"][0]["date_added"] = menu_date
    bookmarks.save_to_json()
    output_file = Path(bookmarks.output_filepath).with_suffix(".json")
    assert cmp(result_file, output_file)
    Path(output_file).unlink()


def test_from_firefox_html_to_db(
    source_bookmark_files, result_bookmark_files, get_dates_from_db
):
    result_file = result_bookmark_files["from_firefox_html.db"]
    root_date, menu_date = get_dates_from_db(result_file, "Firefox")
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.html"])
    bookmarks.parse_html()
    bookmarks.convert_to_db()
    bookmarks.bookmarks[0].date_added = root_date
    bookmarks.bookmarks[13].date_added = menu_date
    bookmarks.save_to_db()
    output_file = Path(bookmarks.output_filepath).with_suffix(".db")
    assert cmp(result_file, output_file)
    Path(output_file).unlink()


def test_from_firefox_json_to_html(source_bookmark_files, result_bookmark_files):
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.json"])
    bookmarks.parse_json()
    bookmarks.convert_to_html()
    bookmarks.save_to_html()
    output_file = Path(bookmarks.output_filepath).with_suffix(".html")
    assert cmp(result_bookmark_files["from_firefox_json.html"], output_file)
    Path(output_file).unlink()


def test_from_firefox_json_to_db(
    source_bookmark_files, result_bookmark_files, get_dates_from_db
):
    result_file = result_bookmark_files["from_firefox_json.db"]
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.json"])
    bookmarks.parse_json()
    bookmarks.convert_to_db()
    bookmarks.save_to_db()
    output_file = Path(bookmarks.output_filepath).with_suffix(".db")
    assert cmp(result_file, output_file)
    Path(output_file).unlink()
