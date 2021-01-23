from filecmp import cmp
from pathlib import Path

from bookmarks_converter import BookmarksConverter


def test_from_chrome_html_to_json(
    source_bookmark_files, result_bookmark_files, read_json
):
    result_file = Path(result_bookmark_files["from_chrome_html.json"])
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
    output_file = bookmarks.output_filepath.with_suffix(".json")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_chrome_html_to_db(
    source_bookmark_files, result_bookmark_files, get_dates_from_db
):
    origin = "Chrome"
    result_file = Path(result_bookmark_files["from_chrome_html.db"])
    result_bookmarks, root_date, other_date = get_dates_from_db(result_file, origin)
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.html"])
    bookmarks.parse_html()
    bookmarks.convert_to_db()
    bookmarks.bookmarks[0].date_added = root_date
    bookmarks.bookmarks[1].date_added = other_date
    bookmarks.save_to_db()
    output_file = bookmarks.output_filepath.with_suffix(".db")
    output_bookmarks, _, _ = get_dates_from_db(output_file, origin)
    assert result_bookmarks == output_bookmarks
    output_file.unlink()


def test_from_chrome_json_to_html(source_bookmark_files, result_bookmark_files):
    result_file = Path(result_bookmark_files["from_chrome_json.html"])
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.json"])
    bookmarks.parse_json()
    bookmarks.convert_to_html()
    bookmarks.save_to_html()
    output_file = bookmarks.output_filepath.with_suffix(".html")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_chrome_json_to_db(
    source_bookmark_files, result_bookmark_files, get_dates_from_db
):
    origin = "Chrome"
    result_file = Path(result_bookmark_files["from_chrome_json.db"])
    result_bookmarks, _, _ = get_dates_from_db(result_file, origin)
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.json"])
    bookmarks.parse_json()
    bookmarks.convert_to_db()
    bookmarks.save_to_db()
    output_file = bookmarks.output_filepath.with_suffix(".db")
    output_bookmarks, _, _ = get_dates_from_db(output_file, origin)
    assert result_bookmarks == output_bookmarks
    output_file.unlink()


def test_from_firefox_html_to_json(
    source_bookmark_files, result_bookmark_files, read_json
):
    result_file = Path(result_bookmark_files["from_firefox_html.json"])
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
    output_file = bookmarks.output_filepath.with_suffix(".json")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_firefox_html_to_db(
    source_bookmark_files, result_bookmark_files, get_dates_from_db
):
    origin = "Firefox"
    result_file = Path(result_bookmark_files["from_firefox_html.db"])
    result_bookmarks, root_date, menu_date = get_dates_from_db(result_file, origin)
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.html"])
    bookmarks.parse_html()
    bookmarks.convert_to_db()
    bookmarks.bookmarks[0].date_added = root_date
    bookmarks.bookmarks[13].date_added = menu_date
    bookmarks.save_to_db()
    output_file = bookmarks.output_filepath.with_suffix(".db")
    output_bookmarks, _, _ = get_dates_from_db(output_file, origin)
    assert result_bookmarks == output_bookmarks
    output_file.unlink()


def test_from_firefox_json_to_html(source_bookmark_files, result_bookmark_files):
    result_file = Path(result_bookmark_files["from_firefox_json.html"])
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.json"])
    bookmarks.parse_json()
    bookmarks.convert_to_html()
    bookmarks.save_to_html()
    output_file = bookmarks.output_filepath.with_suffix(".html")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_firefox_json_to_db(
    source_bookmark_files, result_bookmark_files, get_dates_from_db
):
    origin = "Firefox"
    result_file = Path(result_bookmark_files["from_firefox_json.db"])
    result_bookmarks, _, _ = get_dates_from_db(result_file, origin)
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.json"])
    bookmarks.parse_json()
    bookmarks.convert_to_db()
    bookmarks.save_to_db()
    output_file = bookmarks.output_filepath.with_suffix(".db")
    output_bookmarks, _, _ = get_dates_from_db(output_file, origin)
    assert result_bookmarks == output_bookmarks
    output_file.unlink()
