from src.bookmarks_parser import BookmarksParser


def test_prepare_filepaths():
    filename = "/home/user/Downloads/source/bookmarks.html"
    temp_filepath = "/home/user/Downloads/source/temp_bookmarks.html"
    output_filepath = "/home/user/Downloads/source/output_bookmarks.html"
    bookmarks = BookmarksParser(filename)

    assert temp_filepath == bookmarks.temp_filepath
    assert output_filepath == bookmarks.output_filepath
