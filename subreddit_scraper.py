import praw
from psaw import PushshiftAPI
import mysql.connector
import datetime as dt
from multiprocessing import Pool
import sys

from config import *

# parallelization parameters
NUMBER_OF_PROCESSES = 14


reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)

reddit_db = mysql.connector.connect(
    host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME
)


def add_subreddit_posts(subreddit_name):
    api = PushshiftAPI()

    for post in api.search_submissions(subreddit=subreddit_name):
        sql = "INSERT INTO posts (id, title, body, subreddit,timestamp) VALUES (%s, %s, %s, %s, %s)"
        try:
            val = (
                post.id,
                post.title,
                post.selftext,
                post.subreddit,
                dt.datetime.utcfromtimestamp(post.created),
            )
            cursor.execute(sql, val)
            reddit_db.commit()
        except AttributeError:
            continue


def add_post_comments(post_id):
    cursor = reddit_db.cursor()
    post = reddit.submission(post_id)
    post.comments.replace_more(limit=None)

    for comment in post.comments.list():
        try:
            sql = "INSERT INTO comments (id, body, post_id, timestamp) VALUES (%s, %s, %s, %s)"
            val = (
                comment.id,
                comment.body,
                post_id,
                dt.datetime.utcfromtimestamp(comment.created),
            )
            cursor.execute(sql, val)
        except:
            e = sys.exc_info()[0]
            print(e)
            print(post_id)
            continue

    reddit_db.commit()


def is_table_present(table_name):
    cursor = reddit_db.cursor()
    sql = f"SHOW tables like {table_name}"
    cursor.execute(sql)
    return len(cursor.fetchall) != 0


cursor = reddit_db.cursor()

# create posts table if  not present
if not is_table_present("posts"):
    cursor.execute(
        "CREATE TABLE posts (id VARCHAR(255) PRIMARY KEY, title TEXT, body TEXT, subreddit VARCHAR(255))"
    )

# create comments table if not present
if not is_table_present("comments"):
    cursor.execute(
        "CREATE TABLE comments(id VARCHAR(255), body TEXT, timestamp TIMESTAMP, post_id VARCHAR(200) references posts(id)"
    )

# adds posts from the specified subreddit
add_subreddit_posts(SUBREDDIT_NAME)

sql = """
      SELECT id from posts where id not in (
            SELECT post_id from comments
      )
      """

cursor.execute(sql)
post_ids = cursor.fetchall()
post_ids = [post_id[0] for post_id in post_ids]

# adds in parallel comments from pre-specified posts
with Pool(NUMBER_OF_PROCESSES) as pool:
    pool.map(add_post_comments, post_ids)
