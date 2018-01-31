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
userList = [956233635325132800, 891387302781386752, 958587449416044544]
tweets = []

for users in userList:
	for status in tweepy.Cursor(api.user_timeline, users).items():
		with open("/home/hridoyd/ActiveProbing/data/" + str(users) + "_tweet_details.csv","a") as fp:
			fp.write(str(datetime.datetime.now()) + "," + str(users) + "," + str(status._json) + "\n\n")
		fp.close()
		#insertMongo = db.tweets.insert_one(status._json)
		# for reTweet in api.retweets(status._json['id'],200):
		# 	details = reTweet._json
#db.tweets.update({'id':users}, {'$push': {"changes": {"timestamp":datetime.datetime.now(),"details":details}}}, False, True)			
