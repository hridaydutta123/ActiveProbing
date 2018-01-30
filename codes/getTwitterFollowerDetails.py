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
allUserIDs = db.followerDetails.distinct("id")

userList = [956233635325132800, 170995068]
for users in userList:
	followerof = {}
	# Tweepy API get user details
	result = api.get_user(user_id=users)

	# Check whether the user is already present in mongo
	if users not in allUserIDs:
		# Insert into mongo
		insertMongo = db.followerDetails.insert_one({'id':users})

	# Get followers id of user
	try:
	    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

	    # Get followerids & friendsids of user
	    c = tweepy.Cursor(api.followers_ids, user_id = users)
	    c1 = tweepy.Cursor(api.friends_ids, user_id = users)

	    followerids = []
	    for page in c.pages():
	        followerids.append(page)

	    # Insert into mongo
	    changeVals = {'timestamp': datetime.datetime.now(),'followers':followerids}	
	    db.followerDetails.update({'id':users}, {'$push': {"changes": changeVals}}, False, True)

	    friendsids = []
	    for page in c1.pages():
	        friendsids.append(page)

	    # Insert into mongo
	    changeVals = {'timestamp': datetime.datetime.now(),'friendsids':friendsids}	
	    db.friendDetails.update({'id':users}, {'$push': {"changes": changeVals}}, False, True)


	except tweepy.TweepError:
	    print "tweepy.TweepError="#, tweepy.TweepError
	except:
	    e = sys.exc_info()[0]
	    print "Error: %s" % e


	for followers in followerids:
		# Check for changes
		userMongoDetails = db.followerDetails.find({ "id": users})
		isChangesExist = False
		for details in userMongoDetails:
			if 'changes' in details:
				# Get last update value
				existingFollowers = details['changes'][len(details['changes'])-1]['followers_count']
				existingFriends = details['changes'][len(details['changes'])-1]['friends_count']
			else:
				existingFollowers = details['followers_count']
				existingFriends = details['friends_count']

		#userMongoDetails = db.freemiumusers.find({'id':users}, {'friends_count': 1, 'followers_count': 1})
		
		# New followers
		newFollowers = result._json['followers_count']
		newFriends = result._json['friends_count']
		noOfFavourites = result._json['favourites_count']
		noOfTweets = result._json['statuses_count']

		print result._json['name'], existingFollowers, existingFriends, newFollowers, newFriends

		# Check if followers and friends are same as exist in mongo
		if newFollowers != existingFollowers or newFriends != existingFriends:
			changeVals = {'timestamp': datetime.datetime.now(),'followers_count':newFollowers, 'friends_count': newFriends, 'favourites_count': noOfFavourites, 'statuses_count': noOfTweets}
			db.followerDetails.update({'id':users}, {'$push': {"changes": changeVals}}, False, True)
	
	for friends in friendsids:
		# Check for changes
		userMongoDetails = db.friendDetails.find({ "id": users})
		isChangesExist = False
		for details in userMongoDetails:
			if 'changes' in details:
				# Get last update value
				existingFollowers = details['changes'][len(details['changes'])-1]['followers_count']
				existingFriends = details['changes'][len(details['changes'])-1]['friends_count']
			else:
				existingFollowers = details['followers_count']
				existingFriends = details['friends_count']
				
		# New followers
		newFollowers = result._json['followers_count']
		newFriends = result._json['friends_count']
		noOfFavourites = result._json['favourites_count']
		noOfTweets = result._json['statuses_count']

		print result._json['name'], existingFollowers, existingFriends, newFollowers, newFriends

		# Check if followers and friends are same as exist in mongo
		if newFollowers != existingFollowers or newFriends != existingFriends:
			changeVals = {'timestamp': datetime.datetime.now(),'followers_count':newFollowers, 'friends_count': newFriends, 'favourites_count': noOfFavourites, 'statuses_count': noOfTweets}
			db.friendDetails.update({'id':users}, {'$push': {"changes": changeVals}}, False, True)
