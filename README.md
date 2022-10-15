
# __MBTI chatbot__

This repository contains the code to develop a chatbot that can take one of the [__16 Myers-Briggs personality types__](https://www.16personalities.com/personality-types).

## __Scraping data__

The chatbot is fine-tuned for each personality using posts and comments belonging to the corresponding subreddit (for example, [r/infj](https://www.reddit.com/r/infj/) for the _INFJ type_). 

[`reddit_scraper.py`](https://github.com/aleceress/mbti_chatbot/blob/master/subreddit_scraper.py) contains the script to scrape a given subreddit.
To execute it, you first need an instance of a MySQL database to connect to.
You also need some parameters associated to your reddit account and to the MySQL database: all needs to be inserted in a `config.py` file, following the schema of [`config.example.py`](https://github.com/aleceress/mbti_chatbot/blob/master/config.example.py).

The script is gonna first load all posts in a table called `posts` , and then their comments in a table called `comments`. Although parallelization has been applied, this second part is gonna take many hours. That's why, once you have downloaded the posts you are interested in through the main script (~ 20min), you can use the script [`comments_scraper.py`](https://github.com/aleceress/mbti_chatbot/blob/master/comments_scraper.py) to download the associated comments. If you interrupt it, the next time you run it the script is gonna start from where you left.

## __Training__

### __Preparing data__
To train the model, I first reported data into the [`conversational dataset format`](https://github.com/PolyAI-LDN/conversational-datasets), i.e. a CSV table with the following structure.

| id          | response    | context       | context/0 | ... | context/n |
| :---        |    :----:   |          ---: |---:       | ---:|       ---:|
| s892nn     |  I'm fine      | It's ok. What about you?   | How's life?          |  ... |  Hi!      |

Here, _context/n_ represents the beginning of the conversation, going to the most recent exchange (showed in _context/0_, _context_ and _response_, which is the latest sentence in the conversation). It is possibile to change the cardinality of contexts by overriding the `NUMBER_OF_CONTEXTS` parameter in the `config.py` file.

The script [`create_conversational_dataset.py`](https://github.com/aleceress/mbti_chatbot/blob/master/create_conversational_dataset.py) generates the CSV starting from the SQL tables created during the scraping phase, saving it into a pickle file in the data folder.
A conversation is built either from a post and one of its direct comments or from a post, a comment and its comment chain.

The execution of the script is parallelized, so it writes on N different CSVs - N depending on the  `NUMBER_OF_PROCESSES` parameter - finally concatenated to create the resulting pickle file.

### __Model__

The notebook [`training.py`](https://github.com/aleceress/mbti_chatbot/blob/master/training.ipynb) contains the fine-tuning of the [`DialoGPT-medium`](https://github.com/microsoft/DialoGPT) language model on the conversational data, and is mainly an adaptation of the code you can find in [`this notebook`](https://github.com/ncoop57/i-am-a-nerd/blob/master/_notebooks/2020-05-12-chatbot-part-1.ipynb). 

Executing [`demo.py`]() will start the conversation.

## __Running__

To run all the code in the respository, you can create a virtual environment and run the following commands.

```
virtualenv venv 
source ./venv/bin/activate
pip install -r requirements.txt
```
