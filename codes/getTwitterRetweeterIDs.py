import tweepy
from tweepy import OAuthHandler
import sys
import ConfigParser
from random import randint
from pymongo import MongoClient
import datetime

settings_file = sys.argv[1]

# Connect to MongoDB
client = MongoClient("hpc.iiitd.edu.in", 27017, maxPoolSize=50)

# Connect to db bitcoindb
db=client.activeprobing

#This file creates user-language feature generation
if len(sys.argv) < 1:
    print """
        Command : python userLanguages.py <settings-file>
        (IN OUR CASE)
        python getTwitterTweetDetails.py ../config/apikeys.txt
    """
    sys.exit(1)

# Read config settings
config = ConfigParser.ConfigParser()
config.readfp(open(settings_file))

# Random API key selection 
randVal = randint(1,8)
CONSUMER_KEY = config.get('API Keys ' + str(randVal), 'API_KEY')
CONSUMER_SECRET = config.get('API Keys ' + str(randVal), 'API_SECRET')
ACCESS_KEY = config.get('API Keys ' + str(randVal), 'ACCESS_TOKEN')
ACCESS_SECRET = config.get('API Keys ' + str(randVal), 'ACCESS_TOKEN_SECRET')

print "API Key Details:", CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
auth = OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
api = tweepy.API(auth)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

#search
api = tweepy.API(auth)
userList = [956233635325132800]
tweets = []

for users in userList:
	for status in tweepy.Cursor(api.user_timeline, users).items():
		retweeters = []
		for reTweet in api.retweets(status._json['id'],100):
			print reTweet.user.id, reTweet.user.screen_name, reTweet.user.name
			#print reTweet._json['id_str'], reTweet._json['user']['id'], reTweet._json['retweeted_status']['id']
			retweeters.append(reTweet._json['user']['name'])

		with open("../data/" + str(users) + "_retweeterId_details.csv","a") as fp:
				fp.write(str(datetime.datetime.now()) + "," + str(users) + "," + str(status._json['id']) + "," + str(retweeters) + "\n\n")
		