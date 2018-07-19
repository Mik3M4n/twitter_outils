#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

 Get all replies to a tweet, inlcuding replies-to replies. 
 If the tweet is itself a reply, it fetches the origin of the conversation
 and all replies to the original tweet.
 The algorithm consists in:
 - look for all tweets addressed to the users
 - find the one with in_reply_to_status_id = tweet_id (each tweet has a unique id)
 - recursively call the function to get all the conversation
 
 Input: a list of tweets in .jsonl format (one example of input file is is Streams/example_input.jsonl) 

 Usage:  from console :  > follow_conversations.py my-input-file.jsonl
 
 Output : in the directory Replies/ under your current working directory, one file for each conversation
 named replies_to_<tweet.id>.jsonl

 See the notebook test_follow_conversations.ipynb for an example

"""



import tweepy
import sys
import sys
import json
import twitter
import os





# Set you twitter credentials here
CONSUMER_KEY = 
CONSUMER_SECRET = 
ACCESS_TOKEN = 
ACCESS_TOKEN_SECRET = 






###################################################
###################################################


def get_all_replies(tweet, api, fout, depth=10, Verbose=False):
    """ Gets all replies to one tweet (also replies-to-replies with a recursive call).
        Saves replies to the file fout in .jsonl format.
        Parameters: tweet : Status() object 
                    api : a valid twitter API
                    fout: name of the output file
                    depth: max length of the conversation to stop at
                    Verbose: print some updated during the query
    """
    
    if depth < 1:
        if Verbose:
            print( 'Max depth reached')
        return
    user = tweet.user.screen_name
    tweet_id = tweet.id
    search_query = '@' + user
    
    # filter out retweets
    retweet_filter = '-filter:retweets'
    
    query = search_query + retweet_filter
    try:
        myCursor = tweepy.Cursor(api.search, q=query, 
                                 since_id=tweet_id,
                                 max_id=None, 
                                 wait_on_rate_limit=True, 
                                 wait_on_rate_limit_notify=True, 
                                 tweet_mode='extended',
                                 full_text=True).items()
        rep = [ reply for reply in myCursor if reply.in_reply_to_status_id == tweet_id ]
    except tweepy.TweepError as e:
        sys.stderr.write(('Error get_all_replies: {}\n').format(e))
        time.sleep(60)

    if len(rep) != 0:
        if Verbose: 
            if hasattr(tweet, 'full_text'):
                print ('Saving replies to: %s' % tweet.full_text)
            elif hasattr(tweet, 'text'):
                print ('Saving replies to: %s' % tweet.text)
            print("Output path: %s" %fout)
        
        # save to file
        with open(fout, 'a+') as (f):  
            for reply in rep:
                    data_to_file = json.dumps(reply._json)
                    f.write(data_to_file + '\n')
            
            # recursive call
            get_all_replies(reply, api, fout, depth=depth - 1, Verbose = False)
    
    return 


def find_source(api, tweet, max_height=100):
    """ 
    If a tweet is a reply, find the origin of the conversation. 
    Otherwise, returns the tweet itself
    """
    
    if tweet.in_reply_to_status_id != None:
        try:
            original_tw = api.get_status(tweet.in_reply_to_status_id, 
                                          tweet_mode='extended', 
                                          full_text=True)
            if original_tw.in_reply_to_status_id == None:
                tweet = original_tw
            else:
                # recursive call
                tweet = find_source(api, original_tw, max_height=max_height - 1)
        
        except tweepy.error.TweepError:
            print("Original tweet not available. Looking only for replies to current tweet.")
            pass
        
    return tweet
    



###################################################
# Main: given a .jsonl file containing tweets in .json format, fetch replies to each tweet.
###################################################



def get_auth():
    """
    Gets twitter authentication.
    """
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    except KeyError:
        sys.stderr.write('Set valid twitter variables!')
        sys.exit(1)

    return auth


def get_api(auth):
    """
    Sets the API given the twitter autorization auth
    """
    api = tweepy.API(auth)
    return api





def follow_conversations(tweets_file, api, outdir):
        for line in open(tweets_file):
            original_tweet = twitter.Status.NewFromJsonDict(json.loads(line))
            #print('Tweet id: %s' %tweet.id)
            fout = '%s/replies_to_%s.jsonl' %(outdir, original_tweet.id)
            
            tweet = find_source(api, original_tweet)
            
            # save original tweet
            with open(fout, 'a') as f:
                f.write(json.dumps(tweet._json) + '\n')
            
            # fetch and save full conversation
            get_all_replies(tweet, api, fout, Verbose= True)
        
        return
            

def main():

    # Get authentication & api
    my_auth = get_auth()
    my_api = get_api(my_auth)
    
    
    tweets_file = sys.argv[1] # file where the tweets are stored, read from console

    outdir = os.getcwd()+'/Replies'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    follow_conversations(tweets_file, my_api, outdir)
    
    
    
if __name__=='__main__':
    main()