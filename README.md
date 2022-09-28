
# __MBTI chatbot__

This repository contains the code to develop a chatbot that can take one of the [__16 Myers-Briggs personality types__](https://www.16personalities.com/personality-types).

## __Scraping data__

The chatbot was trained for each personality using posts and comments belonging to the corresponding subreddit (for example, [r/infj](https://www.reddit.com/r/infj/) for the INFJ type). 

The file [`reddit_scraper.py`](https://github.com/aleceress/mbti_chatbot/blob/master/subreddit_scraper.py) contains the script to scrape a given subreddit.
To execute it, you first need an instance of a MySQL database to connect to.
You also need some parameters associated to your reddit account and to the MySQL database. You can insert them in a `config.py` file, following the schema of [`config.example.py`](https://github.com/aleceress/mbti_chatbot/blob/master/config.example.py), in which the parameters of interest are specified.

The script is gonna first load all posts in a table called __posts__, and then their comments in a table called __comments__. Although parallelization has been applied, this second part is gonna take many hours. That's why, once you have donloaded the posts you are interested in through the main script (~ 20min), you can use the script [`comments_scraper.py`](https://github.com/aleceress/mbti_chatbot/blob/master/comments_scraper.py) to download the associated comments. If you interrupt it, the next time you run it the script is gonna start from where you left.

## __Training__

### __Preparing data__
To train the model, I first reported data into the [`conversational dataset format`](https://github.com/PolyAI-LDN/conversational-datasets), i.e. a CSV table with the following structure:

| id          | response    | context       | context/0 | ... | context/n |
| :---        |    :----:   |          ---: |---:       | ---:|       ---:|
| s892nn     |  I'm fine      | It's ok. What about you?   | How's life?          |  ... |  Hi!      |

Here, context/n represents the beginning of the conversation, going to the most recent exchange (showed in context/0, context and response, which is the latest sentence in the conversation). It is possibile to change the cardinality of contexts by overriding the NUMBER_OF_CONTEXTS parameter in the `config.py` file.

The script [`create_conversational_dataset.py`](https://github.com/aleceress/mbti_chatbot/blob/master/create_conversational_dataset.py) generates the CSV starting from the SQL tables created during the scraping phase, saving it into a pickle file in the data fold and calling it < SUBREDDIT_NAME >conversations.pickle.
A conversation is built either from a post and one of its direct comments or from a post, a comment and its comment chain.

The execution of the script is parallelized, so it writes on N different CSVs - N depending on the NUMBER_OF_PROCESSES parameter - that are then put in the data/< SUBREDDIT_NAME > folder. Different CSVs are concatenated to create the final pickle file.