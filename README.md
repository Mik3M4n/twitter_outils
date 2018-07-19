
This repo contains some code useful to scrape twitter and not immediately available in the twitter API.

In particular:

1 - follow_hashtag is a script that runs a query with one or more keywords trying to overcome some limitations of the twitter API:

	A - the number of requests allowed is 400/15 mins instead of 180/15 mins

	B - it allows to exploit multiple accounts. When the rate limit for one is reached, it switches to the next

	Thus this script is useful to  follow hashtags with high frequency of tweets.

	To edit parameters of the query, edit the file config_follow_hashtag.py

	Usage: from console > python follow_hashtag.py

	Output : in the directory Streams/ under your current working directory, one file named stream_<fname>.jsonl



2 - follow_conversations contains a function that allows to get all replies to a tweet, inlcuding replies-to replies. If the tweet is itself a reply, it fetches the origin of the conversation and all replies to original tweet. This kind of option is not included in the twitter API, so one has to do it by hand. 

With this script, given a list of tweets in .jsonl format, we can reconstruct all conversations containign the tweets in the list.


Usage:  from console :  > python follow_conversations.py my-input-file.jsonl

Output : in the directory Replies/ under your current working directory, one file for each conversation named replies_to_<tweet.id>.jsonl

Example: see the notebook test_follow_conversations.ipynb for an example
