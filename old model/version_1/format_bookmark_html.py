import re
import os


def format_bookmark_html(file_path):
    """
    Takes in an absolute path to a HTML Bookmarks file, it creates a new Bookmarks file with the text "new_" prepeneded to the filename. where,
    - The main "<H1>" header is converted to "<H3>" and acts as the root folder.
    - All "<DT>" tags are removed.
    - "<H3>" acts as folders and list containers instead of "<DL>".
    - All "<H3>" and "<A>" tag's inner text are added as a "title" attribute within the html element.

    :param file_path: absolute path to bookmarks html file
    :type file_path: str
    """
    with open(file_path, "r") as f:
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

    output_file = os.path.dirname(file_path) + "/new_" + os.path.basename(file_path)

    with open(output_file, "w") as f:
        f.writelines(lines3)
