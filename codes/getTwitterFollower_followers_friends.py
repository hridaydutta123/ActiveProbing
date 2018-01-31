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
allUserIDs = db.followerID.distinct("id")

userList = [956233635325132800, 170995068]
for users in userList:
	# Tweepy API get user details
	result = api.get_user(user_id=users)

	# Check whether the user is already present in mongo
	if users not in allUserIDs:
		# Insert into mongo
		insertMongo = db.followerID.insert_one({'id':users})

	# Get followers id of user
	try:
	    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

	    # Get followerids & friendsids of user
	    c = tweepy.Cursor(api.followers_ids, user_id = users)
	    c1 = tweepy.Cursor(api.friends_ids, user_id = users)

	    followerids = []
	    for page in c.pages():
	        followerids.append(page)
	    friendsids = []
	    for page in c1.pages():
	        friendsids.append(page)

	except tweepy.TweepError:
	    print "tweepy.TweepError="#, tweepy.TweepError
	except:
	    e = sys.exc_info()[0]
	    print "Error: %s" % e
	print followerids[0]
	print friendsids[0]
	with open("../data/" + str(users) + '_TwitterFollower_followers_friends.csv','a') as fp:
		fp.write(str(datetime.datetime.now()) + "," + str(users) + "," + str(followerids) + "," + str(friendsids) + "\n")