import os
from flask import Flask
from bookmarkie.models import *
from bookmarkie.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bookmarkie import bookmarks_parser


def main(env="test"):
    # setup database info according to the given input
    if env == "test":
        database_filename = "bookmarkie_test.db"
        project_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = "sqlite:///{}".format(
            os.path.join(project_dir, database_filename)
        )
    elif env == "production":
        database_filename = "bookmarkie.db"
        project_dir = os.path.dirname(os.path.abspath(__file__)) + "/bookmarkie/"
        database_path = "sqlite:///{}".format(
            os.path.join(project_dir, database_filename)
        )

    # initialize app
    app = create_app()

    # initialize database
    setup_db(app, database_path)

    # Create Database
    db.drop_all()
    db.create_all()

    # Create database initial data
    directories = [
        Directory(name="Entertainment"),
        Directory(name="Email"),
        Directory(name="Images"),
        Directory(name="Programming"),
        Directory(name="Information"),
    ]
    urls = [
        Url(title="Youtube", url="https://www.youtube.com", directory_id=1),
        Url(title="Veoh", url="https://www.veoh.com/", directory_id=1),
        Url(title="Gmail", url="https://www.google.com/gmail/about/#", directory_id=2),
        Url(title="Outlook", url="https://outlook.live.com/owa/", directory_id=2),
        Url(title="Unsplash", url="https://unsplash.com/", directory_id=3),
        Url(title="ArtStation", url="https://www.artstation.com/", directory_id=3),
        Url(title="Python", url="https://www.python.org/", directory_id=4),
        Url(title="Udacity", url="https://www.udacity.com/", directory_id=4),
        Url(title="Wikipedia", url="https://www.wikipedia.org/", directory_id=5),
        Url(title="Encyclopedia", url="https://www.encyclopedia.com/", directory_id=5),
    ]

    # Commit data to database
    db.session.bulk_save_objects(directories)
    db.session.bulk_save_objects(urls)
    db.session.commit()


# Temporary function just to test the "bookmarks_parser.py" script
def main_books():
    # Set Bookmarks file path
    bookmark_file = "/home/vagabond/Downloads/booky/temp_helper_files/bookmarks/bookmarks_chrome_2020_07_20.html"

    # Set up database info
    database_filename = "bookmarkie.db"
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

    # initialize app
    app = Flask(__name__)
    engine = create_engine(database_path)
    Session = sessionmaker(bind=engine)
    session = Session()
    connection = engine.connect()

    # initialize database
    setup_db(app, database_path)

    # Create Database
    Base.metadata.drop_all(connection)
    Base.metadata.create_all(connection)
    session.commit()

    # Parse bookmarks
    bookmarks_parser.main(bookmark_file)

    # Commit data to database
    session.commit()


def empty_db():
    database_filename = "bookmarkie_test.db"
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))
    # initialize app
    app = create_app()

    # initialize database
    setup_db(app, database_path)

    # Create Database
    db.drop_all()
    db.create_all()


# if __name__ == "__main__":
#     main(env="production")
# else:
#     main()

if __name__ == "__main__":
    main_books()
