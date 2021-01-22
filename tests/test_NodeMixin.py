import pytest
from bookmarks_converter.models import NodeMixin, Folder, Url


def test_create_url_as_db(url_custom, create_class_instance):
    instance = Url(
        title="Google",
        index=0,
        parent_id=1,
        url="https://www.google.com",
        _id=2,
        date_added=0,
        icon=None,
        icon_uri="https://www.google.com/favicon.ico",
        tags=None,
    )
    for key, value in url_custom.items():
        if key == "iconuri":
            assert value == instance.icon_uri
        else:
            assert value == getattr(instance, key)


def test_create_folder_as_db(folder_custom, create_class_instance):
    instance = Folder(title="Main Folder", index=0, parent_id=0, _id=1, date_added=0)
    for key, value in folder_custom.items():
        assert value == getattr(instance, key)


def test_create_url_as_json(url_custom, create_class_instance):
    instance = create_class_instance(url_custom, NodeMixin)
    assert url_custom == instance.create_url_as_json()


def test_create_folder_as_json(folder_custom, create_class_instance):
    instance = create_class_instance(folder_custom, NodeMixin)
    assert folder_custom == instance.create_folder_as_json()


def test_create_url_as_html(url_custom, create_class_instance):
    instance = create_class_instance(url_custom, NodeMixin)
    url = url_custom.get("url")
    date_added = url_custom.get("date_added")
    icon_uri = url_custom.get("iconuri")
    icon = url_custom.get("icon")
    title = url_custom.get("title")
    html_url = f'<DT><A HREF="{url}" ADD_DATE="{date_added}" LAST_MODIFIED="0" ICON_URI="{icon_uri}" ICON="{icon}">{title}</A>\n'
    assert html_url == instance.create_url_as_html()


# preparing the arguments for @pytest.mark.parametrize()
titles = [
    "Bookmarks Toolbar",
    "Bookmarks bar",
    "toolbar",
    "Other Bookmarks",
    "unfiled",
    "Main Folder",
]
expect1 = [
    f'<DT><H3 ADD_DATE="0" LAST_MODIFIED="0" PERSONAL_TOOLBAR_FOLDER="true">{t}</H3>\n'
    for t in titles[:3]
]
expect2 = [
    f'<DT><H3 ADD_DATE="0" LAST_MODIFIED="0" UNFILED_BOOKMARKS_FOLDER="true">{t}</H3>\n'
    for t in titles[3:5]
]
expect = [
    *expect1,
    *expect2,
    '<DT><H3 ADD_DATE="0" LAST_MODIFIED="0">Main Folder</H3>\n',
]
arguments = [(t, e) for t, e in zip(titles, expect)]


@pytest.mark.parametrize(
    "title, expected",
    arguments,
    ids=titles,
)
def test_create_folder_as_html(title, expected, folder_custom, create_class_instance):
    instance = create_class_instance(folder_custom, NodeMixin)
    instance.title = title
    assert expected == instance.create_folder_as_html()


@pytest.mark.parametrize(
    "method",
    [
        "create_folder_as_db",
        "create_url_as_db",
        "create_folder_as_html",
        "create_url_as_html",
        "create_folder_as_json",
        "create_url_as_json",
    ],
)
def test_check_type(method):
    instance = NodeMixin()
    instance.type = "None"
    with pytest.raises(TypeError) as error:
        getattr(instance, method)()


def test_iter():
    instance = NodeMixin()
    instance.children = [i for i in range(10)]
    for a, b in zip(instance, instance.children):
        assert a == b