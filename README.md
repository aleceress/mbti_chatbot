
# __MBTI chatbot__

This repository contains the code to develop a chatbot that can take one of the [__16 MBTI personality types__](https://www.16personalities.com/personality-types).

## __Training data__

The chatbot was trained for each personality using posts and comments belonging to the corresponding subreddit (for example, [r/infj](https://www.reddit.com/r/infj/) for the INFJ type). 

The file [`reddit_scraper.py`](https://github.com/aleceress/mbti_chatbot/blob/master/subreddit_scraper.py) contains the script to scrape a subreddit, given its name.
To execute it, you need some parameters associated to yor reddit account and also a mysql database. You can insert them in a `config.py` file, following the schema of [`config.example.py`](https://github.com/aleceress/mbti_chatbot/blob/master/config.example.py).