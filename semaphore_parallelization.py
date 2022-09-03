import multiprocessing
import praw
from psaw import PushshiftAPI
from tqdm import tqdm
import mysql.connector 
import datetime as dt
from multiprocessing import Queue, Process, Semaphore, Pool

reddit = praw.Reddit(
    client_id="Bm4_zFjt--o5aU9E_dzSeg",
    client_secret="15jr_6ct1g3OTQHAu5x23CI7KI8rTQ",
    user_agent="mbti chatbot",
)

reddit_db = mysql.connector.connect(
  host="172.16.10.50",
  user="alessia",
  password="P823vrv6j8LWDauUMXaHa4r9",
  database= "reddit"
)

cursor = reddit_db.cursor()
sql = "SELECT id from posts"
cursor.execute(sql)
post_ids = cursor.fetchall()

def add_post_comments(post_id, cursor, semaphore):
    semaphore.acquire()

    post = reddit.submission(post_id)
    post.comments.replace_more(limit=None)

    for comment in post.comments.list():
        sql = "INSERT INTO comments (id, body, post_id, timestamp) VALUES (%s, %s, %s, %s)"
        try:
            val = (comment.id, comment.body, post_id, dt.datetime.utcfromtimestamp(comment.created))
            cursor.execute(sql, val)
        except AttributeError:
            continue
        
    semaphore.release()
    reddit_db.commit()


NUMBER_OF_PROCESSES = 14

task_queue = Queue()
for post_id in post_ids:
    task_queue.put(post_id[0])

while not task_queue.empty():
    semaphore = Semaphore(NUMBER_OF_PROCESSES)
    for _ in range(NUMBER_OF_PROCESSES):
        post_id = task_queue.get()
        process = Process(target=add_post_comments, args = (post_id, cursor, semaphore))
        process.start()
