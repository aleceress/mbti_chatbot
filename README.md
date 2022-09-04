
# __MBTI chatbot__

This repository contains the code to develop a chatbot that can take one of the [__16 Myers-Briggs personality types__](https://www.16personalities.com/personality-types).

## __Scraping data__

The chatbot was trained for each personality using posts and comments belonging to the corresponding subreddit (for example, [r/infj](https://www.reddit.com/r/infj/) for the INFJ type). 

The file [`reddit_scraper.py`](https://github.com/aleceress/mbti_chatbot/blob/master/subreddit_scraper.py) contains the script to scrape a given subreddit.
To execute it, you first need an instance of a MySQL database to connect to.
You also need some parameters associated to your reddit account and to the MySQL database. You can insert them in a `config.py` file, following the schema of [`config.example.py`](https://github.com/aleceress/mbti_chatbot/blob/master/config.example.py), in which the parameters of interest are specified.

The script is gonna first load all posts in a table called `posts`, and then their comments in a table called `comments`. Although parallelization has been applied, this second part is gonna take many hours. That's why, once you have donloaded the posts you are interested in through the main script (~ 20min), you can use the script `scrape_comments.py` to download the associated comments. If you interrupt it, the next time you run it the script is gonna start from where you left.