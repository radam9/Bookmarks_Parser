# JSON Chrome

chrome timestamp starts from a different epoch (microseconds from 1601-01-01T00:00:00Z)
subtract 11644473600000000 to bring it to unix epoch

### Folder

{
"children": [],
"date_added": "13244233436520764",
"date_modified": "0",
"id": "6",
"name": "Social",
"type": "folder"
}

### Url

{
"date_added": "13244224395000000",
"id": "7",
"name": "Twitter. It’s what’s happening / Twitter",
"type": "url",
"url": "https://twitter.com/?lang=en"
}

# JSON Firefox

### Folder

{
"guid":"K3LUb7o0kSUt",
"title":"Mozilla Firefox",
"index":0,
"dateAdded":1599750431776000,
"lastModified":1599750431776000,
"id":7,
"typeCode":2,
"type":"text/x-moz-place-container",
"children":[]
}

### Url

{
"guid":"7TpRGhofxKDv",
"title":"Help and Tutorials",
"index":0,
"dateAdded":1599750431776000,
"lastModified":1599750431776000,
"id":8,
"typeCode":1,
"iconuri":"fake-favicon-uri:https://support.mozilla.org/en-US/products/firefox",
"type":"text/x-moz-place",
"uri":"https://support.mozilla.org/en-US/products/firefox"
}

# JSON Bookmarkie

### Folder

{
"type": "folder",
"id": folder.id,
"index": folder.index,
"parent_id": folder.parent_id,
"title": folder.title,
"date_added": folder.date_added,
"children": [],
}

### Url

{
"type": "url",
"id": url.id,
"index": url.index,
"parent_id": url.parent_id,
"url": url.url,
"title": url.title,
"date_added": url.date_added,
"icon": url.icon,
"iconuri": url.icon_uri,
"tags": url.tags,
}
