import re
import numpy as np
import pandas as pd
import tweetlda

from gensim import corpora
from gensim.models import TfidfModel
from gensim.models.ldamodel import LdaModel
from nltk.corpus import stopwords
from collections import Counter


def format_tweets(tweets):
	#=====[ Replace non alphabetic characters, take to lower case, and tokenize on spaces ]=====
	tweets = tweets.str.replace('[^A-Za-z ]', '')
	tweets = tweets.str.lower().str.split()

	#=====[ Remove stopwords  ]=====
	remove_words = stopwords.words('english')
	tweets = tweets.apply(lambda word: [w for w in word if not w in remove_words])

	return tweets

# =====[ Read in CSV and label columns ]=====
df = pd.read_csv('trainingandtestdata/testdata.manual.2009.06.14.csv')
df.columns=['empty','empty2','time','subject','user_name','tweet']

#=====[ Drop unnecessary parameters ]=====
df=df.drop(["empty","empty2","time"],axis=1)

#=====[ Get number of unique subjects ]=======
unique_subjects = df.subject.nunique()

df.tweet = format_tweets(df.tweet)

#=====[ Instantiate Tweet LDA Model  ]=====
ldamodel = tweetlda.TweetLDAModel(df.tweet)
ldamodel.fit(20,20)

#=====[ Print topic indexed at 0 with top 20 words ]=====
print ldamodel.lda.print_topic(0,topn=20)

#=====[ Format test tweets  ]=====
test_tweets = pd.DataFrame(["Lebron! I hope you're doing well!","Kobe, I hope you're ankle stays broken!"])
test_tweets.columns=['tweet']
test_tweets.tweet = format_tweets(test_tweets.tweet)

#=====[ Retrieve a tweet  ]=====
tweet = test_tweets.tweet[0]

#=====[ Turn new doc into tfidf bag of words  ]=====
bow = dictionary.doc2bow(tweet)
doc = tfidf[bow]

#=====[ Get topics for new doc  ]=====
topics = ldamodel.lda[doc]

#=====[ Sort topics for new doc  ]=====
topics.sort(key=lambda tup: tup[1])

ldamodel.lda.print_topic(topics[-1][0], topn=20)

