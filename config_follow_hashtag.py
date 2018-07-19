###################################################
# COnfiguration for the file follow_hashtag.py
###################################################


##### Parameters: #######
#
# my_fname: output file name
# my_hashtag : the hashtag to follow (or a list of strings with different hashtags)
# my_since_date: date to start the query in 'yy-mm-dd' format , e.g. '2018-07-04'. The query goes from 
#                this date onwards in time, until the current time.
# my_until_id :  Last tweet id to stop the query at. Useful if you want to limit your query to some 
#                specific moment. If not specified, the query will run until current time.
# max_tweets: maximum numer of tweets to fetch. If not specified, default is 100k
#
# Output : in the directory Streams/ under your current working directory, 
# one file named stream_<my_fname>.jsonl



###################################################
# Twitter credentials. Only consumer key and consumer secret are needed. 
# This code uses three different account. 
###################################################

# Twitter credentials as strings
CONSUMER_KEY = 
CONSUMER_SECRET = 
ACCESS_TOKEN =
ACCESS_TOKEN_SECRET = 


CONSUMER_KEY_1 = 
CONSUMER_SECRET_1 = 
ACCESS_TOKEN_1 = 
ACCESS_TOKEN_SECRET_1 = 


CONSUMER_KEY_2 = 
CONSUMER_SECRET_2 = 
ACCESS_TOKEN_2 = 
ACCESS_TOKEN_SECRET_2 = 


# to add/remove credentials, edit the following list
oauth_keys = [[CONSUMER_KEY, CONSUMER_SECRET], 
               [CONSUMER_KEY_1, CONSUMER_SECRET_1],
               [CONSUMER_KEY_2, CONSUMER_SECRET_2]]



###################################################                                 


# Hashtag/query words to follow
my_hashtag = '#ThursdayThoughts' # can be a list of strings


# Output file name. For queries with only 1 hashtag, it is suggested to set just
# my_fname = my_hashtag
# For long queries, edit the following line

my_fname = my_hashtag


# starting date
my_since_date = '2018-07-19'

# Max. number of tweets to fetch
max_tweets = 100


# optional: last tweet id (useful to follow discussions from one specific tweet back)
# my_until_id = 1019225818759757826
