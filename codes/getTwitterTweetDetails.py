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

# Get id of tweeets in mongo
allTweetIDs = db.tweets.distinct("id")
allTweetIDs = [int(x) for x in allTweetIDs]


for status in tweepy.Cursor(api.user_timeline, userList[0]).items():
	# results = api.status_lookup(status._json['id'])
	for reTweet in api.retweets(status._json['id'],200):
		print int(status._json['id'])
		allRTersIDs = db.tweets.find({'id':int(status._json['id'])})
		for ids in allRTersIDs:
			for rterIds in ids['retweets']:
				print rterIds['user']['id']
		reTweet._json["last_seen"] = datetime.datetime.now()
		# db.tweets.update({'id':status._json['id']}, {'$push': {"retweets": reTweet._json}}, False, True)
		# db.tweets.reTweet._json
	if status._json['id'] not in allTweetIDs:
		insertMongo = db.tweets.insert_one(status._json)
	# Check for changes
	# userMongoDetails = db.tweets.find({'id':status._json['id']}, {'friends_count': 1, 'followers_count': 1})
	# for values in userMongoDetails:
	# 	existingFollowers = values['followers_count']
	# 	existingFriends = values['friends_count']
	
	# # New followers
	# newFollowers = result._json['followers_count']
	# newFriends = result._json['friends_count']

	# print  existingFollowers, existingFriends, newFollowers, newFriends

	# # Check if followers and friends are same as exist in mongo
	# if newFollowers != existingFollowers or newFriends != existingFriends:
	# 	changeVals = {'timestamp': datetime.datetime.now(),'followers_count':newFollowers, 'friends_count': newFriends}
	# 	db.freemiumusers.update({}, {'$push': {"changes": changeVals}}, False, True)
