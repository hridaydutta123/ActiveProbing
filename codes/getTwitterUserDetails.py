import tweepy
from tweepy import OAuthHandler
import sys
import ConfigParser
from pymongo import MongoClient
import datetime
from random import randint

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
allUserIDs = db.freemiumusers.distinct("id")

userList = [956233635325132800, 170995068]
for users in userList:
	# Tweepy API get user details
	result = api.get_user(user_id=users)

	# Check whether the user is already present in mongo
	if users not in allUserIDs:
		# Insert into mongo
		insertMongo = db.freemiumusers.insert_one(result._json)

	# Check for changes
	userMongoDetails = db.freemiumusers.find({ "id": users})
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
		db.freemiumusers.update({'id':users}, {'$push': {"changes": changeVals}}, False, True)


