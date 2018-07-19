import tweepy
import sys
import json
import config_follow_hashtag
import time
import os
import twitter
import urllib
from follow_conversations import get_all_replies
from datetime import date, timedelta, datetime
import datetime



###################################################

"""
 This script allows to scrape twitter overcoming two limitations of the
 twitter API:
 1 - the limit of 180 requests/15 minutes is pushed to 400
 2 - the rate limit: exploits multiple twitter credentials, 
                     switching authentication every time the request limit is 
                     exceeded.

 Effective for following hashtags with high frequency of tweets.

 To edit parameters of the query, edit the file config_follow_hashtag.py
 
 Output : in the directory Streams/ under your current working directory, one file 
 named stream_<fname>.jsonl

""" 

###################################################






###################################################
###################################################

def get_multiple_auth():
    """
    Gets twitter authentication with a list of credentials. 
    Note that only consumer key and consumer secret are needed.
    """
    try:
        # edit the config_follow_hashtag to set your twitter credentials
        auths = []
        for consumer_key, consumer_secret in config_follow_hashtag.oauth_keys:
            auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
            auths.append(auth)
       
    except KeyError: 
        sys.stderr.write('Set valid twitter variables!')
        sys.exit(1)
        
    return auths



def get_api(auths):
    try:
        apis = [tweepy.API(auth, wait_on_rate_limit=True, 
                         wait_on_rate_limit_notify=True,
                         retry_errors=set([401, 404, 500, 503])) for auth in auths]
    except KeyError:
        sys.stderr.write('Invalid API')
        sys.exit(1)
    return apis




class HashtagFollower(object):
    
    def __init__(self, api_list, hashtag, 
                 since_date = date.today()-timedelta(15), 
                 until_date = date.today()+timedelta(1), 
                 n_tweets = 100000,
                 n_tweets_batch = 100,
                 Verbose=False, 
                 until_id = None,
                 n_pages = 1):
        
        self.api_list = api_list
        self.hashtag = hashtag
        self.since_date = since_date
        self.until_date = until_date
        self.until_date_or = until_date
        self.n_tweets = n_tweets
        self.n_tweets_batch = n_tweets_batch
        self.Verbose = Verbose
        self.init=False
        self.until_id = until_id
        self.until_id_or = until_id
        self.n_pages = n_pages
        self.limit_reached = False
        
        self.data_dir = os.getcwd()+'/Streams/'
        self.outfile = self.data_dir+'stream_'+config_follow_hashtag.my_fname+'.jsonl'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)  
        print('Saving tweets to %s \n' %self.outfile)
        
        
        
    def _init_query(self):
        """ Initialise variables for the query. """
        print('Initializing query for %s ...' %self.hashtag)
        init = False
        self.switch = 0
        self.api = self.api_list[self.switch]
        self.remaining_req = self._get_remaining_req()
        self.tweet_count = 0
        self.id_list=[]
        self.first_date = self.until_date
        self.kwargs = {"q": self.hashtag, "count": self.n_tweets_batch,
                        "since" : self.since_date,
                        "tweet_mode" : 'extended', "full_text" : True,
                      "wait_on_rate_limit":True,
                      "wait_on_rate_limit_notify":True}
        print('Using auth %s' %self.api)

        return self
    
    
    def _init_until(self):
        
        """ Initialise ending point of the query, 
        either to a date or to a tweet id depending on input (see config file ) """
        
        if "max_id" in self.kwargs.keys():
            self.kwargs.pop("max_id")
        if "until" in self.kwargs.keys():
            self.kwargs.pop("until")
        
        if self.until_id_or==None:
            self.kwargs["until"] = self.until_date_or
            print('initialising to period: %s  - %s' %(self.kwargs["until"], self.kwargs["since"]))
        else:
            self.kwargs["max_id"] = self.until_id_or
            
            print('Searching from  %s up to id %s' %(self.kwargs["since"],self.kwargs["max_id"]))
        self.until_date = self.until_date_or
        self.until_id = self.until_id_or
        print('Query arguments: %s' %self.kwargs)
        

        
        
    def run_query(self):
        """ Initialise and run the query """
        
        # Initialise the query
        self = self._init_query()
        
        while self.tweet_count<self.n_tweets and not self.limit_reached:
            
            try:
                print("Getting next %s tweets..." %self.n_tweets_batch)
                
                if not self.init:
                    self._init_until()
                else:
                    if 'until' in self.kwargs.keys():
                        self.kwargs.pop('until')
                    self.kwargs["max_id"] = self.last_id-1

                cursor =  tweepy.Cursor(self.api.search, **self.kwargs).pages(self.n_pages)
                response= [tweet for page in cursor for tweet in page]
                                
                self._on_response(response)
                self._check_status(response)

            except BaseException as e:
                sys.stderr.write("Error run_query: {}\n".format(e))
                time.sleep(5)   
            
        print('Query completed !')
    
 
        
    def _on_response(self, response):
        
        """ When data are arriving, performs the task requested. In this case 
            we save each tweet in the output file.
            Edit this to add options.
        """
        
        with open(self.outfile, 'a+') as f:
                    for tweet in response:
                        if tweet.id not in self.id_list:
                                f.write(json.dumps(tweet._json)+'\n')
                                self.tweet_count +=1
                                

 
    
    
    def _check_status(self, response):
        
        """
        Updates requests left, checks rate limits, and if needed switches account
        """
        
        self.new_id_list = [tw.id for tw in response]
        self.created_list = [tw.created_at for tw in response]
        
        self.id_list = self._id_update(self.new_id_list)
        self.old_date = self.until_date
        self.remaining_req = self._get_remaining_req()
        
        if self.new_id_list:
            self.last_id = self.new_id_list[len(self.new_id_list) - 1]
            if not self.init:
                print('Init successful.')
                self.init = True
            
        if not self.init:
            print('Failed first request! Retry with a different starting date')
            self.until_date = date.today() - timedelta(1)
            
        if self.created_list:
            self.until_date = self.created_list[len(self.created_list)-1]
            
        if (not self.new_id_list) or (self.old_date == self.until_date) or (self.remaining_req==0):
            if self.remaining_req==0:
                print('  Rate limit exceeded ....')
            else:
                print('--------------  No more tweets found.  --------------')
                #self.init = False
                self.limit_reached = True                
            self._switch_auth()
            
        else:
            self.user_list = [str(tw.user.screen_name) for tw in response]
            print("Last id was ", self.last_id,", by", self.user_list[len(self.user_list) -1],
                              ", Created at: ",str(self.until_date) )
            print("Remaining requests: ",  self.remaining_req)
            print('Got %s tweets' %self.tweet_count)
     
    
    
    def _switch_auth(self):
        print('################# Changing auth to n. %s  #################' %str(self.switch+1))
        if self.switch+1 > len(self.api_list)-1:
            self.switch = 0
        else:   
            self.switch += 1
        self.api = self.api_list[self.switch]
        
        print('Using auth %s' %self.api)
        if self._get_remaining_req()==0:
            print('No more authentications available ! Sleep for 15 minutes....')
            time.sleep(60*15)
    
    
    def _get_remaining_req(self):
        return self.api.rate_limit_status()['resources']['search']['/search/tweets']['remaining']

    
    def _id_update(self, my_id_list):
        l1 = len(my_id_list)+len(self.id_list)
        for my_id in my_id_list:
            if my_id not in self.id_list:
                self.id_list.append(my_id)
        l2 = len(self.id_list)
        if l1!=l2:
            print('%s duplicates found and dropped...' %str(l1-l2))
        return self.id_list


    
    
###################################################
# Main : intitialise and run the query
###################################################

def main():
       
    # Get authentication & api
    my_auth = get_multiple_auth()
    my_api = get_api(my_auth)

    my_params = {'api_list' : my_api, 
                 'hashtag' : config_follow_hashtag.my_hashtag,
                 'since_date' : config_follow_hashtag.my_since_date,
                 'n_tweets' : config_follow_hashtag.max_tweets, 
                 'n_tweets_batch' : 100, 
                 'Verbose' : True, 
                           }
    
    try:
        my_params['until_id'] = config_follow_hashtag.my_until_id
    except AttributeError:
         pass
    
    # create HashtagFollower object
    my_follower = HashtagFollower(**my_params)
                           
    
    # Run 
    my_follower.run_query()
    
    
    
if __name__=='__main__':
    main()
