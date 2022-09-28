import pandas as pd
import csv
import mysql.connector
from tqdm import tqdm
from multiprocessing import Pool, current_process
import multiprocessing
import glob

from config import *

NUMBER_OF_PROCESSES = 15
NUMBER_OF_CONTEXTS = 13

# conneting to sql db
reddit_db = mysql.connector.connect(
    host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME
)

# loading sql db posts
cursor = reddit_db.cursor()
cursor.execute("select * from posts")
posts = cursor.fetchall()
posts = pd.DataFrame(
    posts, columns=["post_id", "post_title", "post_body", "subreddit_name", "timestamp"]
).drop(columns=["timestamp"])

# loading sql db comments
cursor.execute("select * from comments")
comments = cursor.fetchall()
comments = pd.DataFrame(
    comments, columns=["id", "comment_body", "post_id", "comment_timestamp", "parent_comment"]
)

# creating different files to write conversations on
for i in range(NUMBER_OF_PROCESSES):
    with open(f"data/{SUBREDDIT_NAME}/conversations{str(i).zfill(2)}.csv", "w") as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(
            [
                "id",
                "response",
                "context",
                "context/0",
                "context/1",
                "context/2",
                "context/3",
                "context/4",
                "context/5",
                "context/6",
                "context/7",
                "context/8",
                "context/9"
            ]
        )

def generate_comment_chain(comment_id, conversation):
    comment = comments[comments.id == comment_id]
    if len(comment) == 0 or len(conversation) > NUMBER_OF_CONTEXTS:
        return 
    if  comment.parent_comment.values[0] is None:
        conversation.append(comment.comment_body.values[0])
        conversation.append(posts[posts.post_id == comment.post_id.values[0]].post_body.values[0])
    else:
        conversation.append(comment.comment_body.values[0])
        parent_comment_id = comment.parent_comment.values[0]
        generate_comment_chain(parent_comment_id, conversation)

def generate_post_conversations(post_id):
    for comment_id in comments[(comments.post_id == post_id)].id:
        conversation = []
        generate_comment_chain(comment_id, conversation)
        conversation.insert(0, comment_id)
        with open(f"data/infj/conversations{str(int(current_process().name[16:])%NUMBER_OF_PROCESSES).zfill(2)}.csv", 'a') as f:
            writer = csv.writer(f) 
            writer.writerow(conversation[:NUMBER_OF_CONTEXTS]) 

# adding conversations in the conversational db in parallel
post_ids = posts.post_id
with Pool(NUMBER_OF_PROCESSES) as pool:
    pool.map(generate_post_conversations, post_ids)

# concatenate different CSVs
local_path = f"data/{SUBREDDIT_NAME}"
filenames = glob.glob(local_path + "/*.csv")

parallel_conversations = [pd.read_csv(filename) for filename in filenames]
conversations = pd.concat(parallel_conversations, ignore_index=True)

conversations.to_pickle(f"data/{SUBREDDIT_NAME}_conversations.pickle")