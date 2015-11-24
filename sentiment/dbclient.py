import os, sys, string, time, re
import requests, json, urllib, urllib2, base64
import pymongo

class DBClient:

	def __init__(self):
		db = pymongo.MongoClient().twitter_db
		self.tweets = db.tweets

	def show_tweets(self):

		db_tweets = self.tweets

		for tweet in tweets:
			db_id = db_tweets.insert(tweet)
	 
		db_count = db_tweets.count()
	
		print "Tweets stored in MongoDB! Number of documents in twitter_db: %d" % db_count
		# tweets = self.tweets
		# num_positive_tweets = tweets.find({"sentiment" : "positive"})
		# num_negative_tweets = tweets.find({"sentiment" : "negative"})
		# num_neutral_tweets = tweets.find({"sentiment" : "neutral"})
		# num_tweets = tweets.find().count()

		# print ("total number of tweets is" + num_weets)
		# print num_positive_tweets[0]['text']

