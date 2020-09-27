import pytest


@pytest.fixture
def url_chrome():
    return {
        "date_added": "13244224395000000",
        "id": "1",
        "name": "Google",
        "type": "url",
        "url": "https://www.google.com",
    }


@pytest.fixture
def folder_chrome():
    return {
        "children": [],
        "date_added": "13244233436520764",
        "date_modified": "0",
        "id": "2",
        "name": "Main Folder",
        "type": "folder",
    }


@pytest.fixture
def url_firefox():
    return {
        "guid": "7TpRGhofxKDv",
        "title": "Google",
        "index": 0,
        "dateAdded": 1599750431776000,
        "lastModified": 1599750431776000,
        "id": 2,
        "typeCode": 1,
        "iconuri": "https://www.google.com/favicon.ico",
        "type": "text/x-moz-place",
        "uri": "https://www.google.com",
    }


@pytest.fixture
def folder_firefox():
    return {
        "guid": "K3LUb7o0kSUt",
        "title": "Main Folder",
        "index": 0,
        "dateAdded": 1599750431776000,
        "lastModified": 1599750431776000,
        "id": 1,
        "typeCode": 2,
        "type": "text/x-moz-place-container",
        "children": [],
    }


@pytest.fixture
def url_custom():
    return {
        "type": "url",
        "id": 2,
        "index": 0,
        "parent_id": 1,
        "url": "https://www.google.com",
        "title": "Google",
        "date_added": 0,
        "icon": None,
        "iconuri": "https://www.google.com/favicon.ico",
        "tags": None,
    }


@pytest.fixture
def folder_custom():
    return {
        "type": "folder",
        "id": 1,
        "index": 0,
        "parent_id": 0,
        "title": "Main Folder",
        "date_added": 0,
        "children": [],
    }