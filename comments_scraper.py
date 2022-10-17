import multiprocessing
import praw
import mysql.connector
import datetime as dt
from multiprocessing import Pool
import sys

from config import *


# parallelization parameters
NUMBER_OF_PROCESSES = NUMBER_OF_PROCESSES_OVERRIDE or multiprocessing.cpu_count()

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)

reddit_db = mysql.connector.connect(
    host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME
)


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


cursor = reddit_db.cursor()

sql = f"""
     SELECT id from posts where id not in (
        SELECT post_id from comments
      ) and subreddit = '{SUBREDDIT_NAME}'
      """
cursor.execute(sql)
post_ids = cursor.fetchall()
post_ids = [post_id[0] for post_id in post_ids]

# adds in parallel comments from pre-specified posts
print("scraping comments (this is gonna take a while)...")
with Pool(NUMBER_OF_PROCESSES) as pool:
    pool.map(add_post_comments, post_ids)
