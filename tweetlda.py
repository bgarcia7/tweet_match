import sys

sys.path.append('../')
sys.path.insert(0,'/usr/local/lib/python2.7/site-packages')


import re
import os
import gensim
import operator
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
# from gensim.models.ldamodel import LdaModel
from collections import Counter
import sentimentTasks as utils
from sklearn.metrics.pairwise import cosine_similarity


class TwitterLDAModel:

	#=====[ Initializes lda model and id2word for doc2bow conversion  ]=====
	def __init__(self):
		print gensim.__version__
		self.lda = gensim.models.ldamodel.LdaModel.load(os.path.join('topic_modeling/','trained'))
		self.id2word = gensim.corpora.Dictionary.load_from_text(os.path.join('topic_modeling/','._wordids.txt'))
		self.topic_names = []
		for line in open(os.path.join('topic_modeling/','topics.txt')):
			if(line.rstrip() != ""):
				self.topic_names.append(line[line.index(':')+1:].rstrip())

	def format_tweets(self, tweets):
		#=====[ Get stop words  ]=====
		remove_words = stopwords.words('english')

		#=====[ Take tweets to lowercase, tokenize on white space, and remove stop words  ]=====
		all_tweets = []
		for tweet in tweets:
			for word in tweet.lower().split():
				if word not in remove_words:
					all_tweets.append(word)

		return all_tweets
		
	def get_topics(self,tweets):
		"""
		returns list of topics for list of tweets
		"""

		#=====[ Turns tweets into bag of words and gets list of relevant topics  ]=====
		bow = self.id2word.doc2bow(tweets)

		#=====[ Infer top topics from bag of words  ]=====
		tweet_topics = self.lda[bow]
		return tweet_topics

	#=====[ Returns top topics for set of tweets  ]=====
	def distill_top_topics(self,user_data, topn):
		
		#=====[ Extracts tweet text from user data  ]=====
		tweets = utils.get_tweets(user_data)
		tweets = self.format_tweets(tweets)

		#=====[ Gets topics for list of tweets  ]=====
		all_tweet_topics = self.get_topics(tweets)
		topic_scores = {}

		#=====[ Aggregates scores for each topic from each tweet  ]=====
		for topic in all_tweet_topics:
			if topic[1] > 0.15:
				topic_scores[topic[0]] = topic[1]

		#=====[ Sorts topics and returns #topn of them  ]=====
		sorted_topics = sorted(topic_scores.items(), key=operator.itemgetter(1))
		top_topics = []
		for topic in sorted_topics:
			topic_name = self.topic_names[topic[0]]
			if topic_name not in top_topics:
				top_topics.append(topic_name)
		
		return top_topics

	def get_topic_similarity(self,user_data):
		""" Returns cosine similarity between topic scores for two users"""

		#=====[ Extracts tweet text from user data  ]=====
		tweets = [utils.get_tweets(data) for data in user_data]
		tweets = [self.format_tweets(tweet_set) for tweet_set in tweets]

		#=====[ Gets topics for list of tweets  ]=====
		all_tweet_topics = [self.get_topics(tweet_set) for tweet_set in tweets]

		scores = []

		#=====[ Rehydrates a vector in order to take cosine similarity 
		for topics in all_tweet_topics:
			topic_scores = [0]*100
			for score in topics:
				topic_scores[score[0]] = score[1]
			scores.append(topic_scores)

		similarity = cosine_similarity(scores[0:1], scores)
		similarity = int(float("%.3f" % similarity[0][1])*100)

		return similarity




