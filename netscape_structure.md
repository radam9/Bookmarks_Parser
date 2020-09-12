# Structure and Format of Firefox and Chrome HTML/JSON bookmark file exports.

## 1) Firefox HTML Bookmarks File Structure

All the Firefox bookmarks are contained inside the main `Bookmarks Menu` list.

The special folders `Bookmarks Toolbar` and `Other Bookmarks` have a special attribute to indicate their type. The `Mobile Bookmarks` folder is not included in the HTML file when being exported, you need to export the bookmarks as JSON or use the firefox sqlite database file to backup to export your `Mobile Bookmarks`.

#### Firefox HTML Bookmark file Template

```html
[Netscape Bookmark File Headers]
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks Menu</H1> <!-- Different "H1" Name than Chrome -->
<DL><p>
    <!-- The standard simple "H3" and "A" tags inside the main "H1/DL" are inside the "Bookmarks Menu" folder. -->
    <DT><H3></H3>
    <DT><A></A>
    <!-- Folder containing the Personal_Toolbar_Folder attribute set to true is the "Bookmarks Toolbar" folder -->
    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true"></H3>
    <DL><p>
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <!-- Folder containing the Unified_Bookmarks_Folder attribute set to true is the "Other Bookmarks" folder -->
    <DT><H3 UNFILED_BOOKMARKS_FOLDER="true"></H3>
    <DL><p>
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
</DL><p>
```

## 2) Chrome HTML Bookmarks File Structure

All the Chrome bookmarks are contained inside the main list.

The main list usually starts with the `Bookmarks bar` folder, all the bookmarks that follow the `Bookmarks bar` "H3" and are located inside the main list are either inside the `Other Bookmarks` or `Mobile Bookmarks` folder. Unlike the Firefox the `Mobile Bookmarks` folder is included inside the HTML export, but they are included right after the `Other Bookmarks` "H3" and "A" so it is not possible to differentiate between them from within the HTML file.

#### Chrome HTML Bookmark file Template

```html
[Netscape Bookmark File Headers]
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1> <!-- Different H1 Name than Firefox -->
<DL><p>
    <!-- Folder containing the Personal_Toolbar_Folder attribute as true is the "Bookmarks bar" folder -->
    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true"></H3>
    <DL><p>
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <!-- All the "H3" and "A" tags that come after the "Bookmarks bar" "H3" folder,
     and are in the main list, are links and folder from inside the "Other Bookmarks" folder -->
    <DT><H3></H3>
    <DL><p>
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <DT><A></A>
    <!-- Chrome appends the "Mobile Bookmarks" folder items after the "Other Bookmarks" folder items,
     there is no separator or identifier so it is not possible to identify them from the HTML file -->
    <DT><H3></H3>
    <DL><p>
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <DT><A></A>
</DL><p>
```
