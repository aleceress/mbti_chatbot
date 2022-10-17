from curses.ascii import SUB
from lib2to3.pgen2.token import NUMBER
import mysql.connector
import praw
import sys
from tqdm import tqdm
from multiprocessing import Pool,cpu_count

from config import *

NUMBER_OF_PROCESSES = cpu_count()

reddit_db = mysql.connector.connect(
    host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME
)
cursor = reddit_db.cursor()

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)

def add_parent_comments(post_id):
    # cursor = reddit_db.cursor()
    post = reddit.submission(post_id)
    post.comments.replace_more(limit=None)

    for comment in post.comments.list():
        try:
            parent_id = comment.parent_id[3:]
            if parent_id != post_id:
                cursor.execute(f"update comments set parent_comment = '{parent_id}' where id = '{comment.id}'")
        except:
            e = sys.exc_info()[0]
            print(e)
            print(post_id)
            continue
    reddit_db.commit()       

cursor.execute(f"select id from posts where subreddit = {SUBREDDIT_NAME}")
post_ids = cursor.fetchall()
post_ids = [post_id[0] for post_id in post_ids]

with Pool(NUMBER_OF_PROCESSES) as pool:
    pool.map(add_parent_comments, post_ids)
