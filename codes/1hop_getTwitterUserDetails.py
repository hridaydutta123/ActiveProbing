import tweepy
from tweepy import OAuthHandler
import sys
import ConfigParser
from pymongo import MongoClient
import datetime
from random import randint
import time

# Mongo Settings
# Connect to MongoDB
client = MongoClient("hpc.iiitd.edu.in", 27017, maxPoolSize=50)

# Connect to db bitcoindb
db=client.activeprobing

settings_file = sys.argv[1]

#This file creates user-language feature generation
if len(sys.argv) < 1:
    print """
        Command : python userLanguages.py <inp-file> <settings-file>
        (IN OUR CASE)
        python userLanguages.py ../../Dataset/username_userID.csv ../settings.txt
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

auth = OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
api = tweepy.API(auth)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

#search
api = tweepy.API(auth)

# Get list of userIDs in mongo
allUserIDs = db.followers.distinct("id")

userList = [170995068]
for users in userList:
	try:
	    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

	    # Get followerids of user
	    c = tweepy.Cursor(api.followers_ids, user_id = users)
	    followerids = []
	    for page in c.pages():
	        followerids.append(page)
	    print "ids=", followerids
	except tweepy.TweepError:
	    print "tweepy.TweepError="#, tweepy.TweepError
	except:
	    e = sys.exc_info()[0]
	    print "Error: %s" % e

	for ids in followerids[0]:
		print ids
		# Tweepy API get user details
		result = api.get_user(user_id=ids)

		if ids not in allUserIDs:
			# Insert into mongo
			result._json['lastModified'] = datetime.datetime.now()
			result._json['followerOf'] = users
			insertMongo = db.followers.insert_one(result._json)
		else:
			# # Check for changes
			userMongoDetails = db.followers.find({'id':ids}, {'friends_count': 1, 'followers_count': 1})
			for values in userMongoDetails:
				existingFollowers = values['followers_count']
				existingFriends = values['friends_count']
			
			# New followers
			newFollowers = result._json['followers_count']
			newFriends = result._json['friends_count']

			# Check if followers and friends are same as exist in mongo
			if newFollowers != existingFollowers or newFriends != existingFriends:
				changeVals = {'timestamp': datetime.datetime.now(),'followers_count':newFollowers, 'friends_count': newFriends}
				db.followers.update({'id':ids}, {'$push': {"changes": changeVals}}, False, True)

