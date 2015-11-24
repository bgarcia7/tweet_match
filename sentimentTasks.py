import sys

sys.path.append('/usr/local/lib/python2.7/site-packages')

import os 
import subprocess
import json
import scipy
import random
import numpy as np
from scipy.stats import norm
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def get_json(user_name):
	with open(os.path.join('sentiment/json_data/',user_name+'.json'), 'r') as f:		
		json_data = json.load(f)
	print "[SUCCESSFUL] LOAD JSON DATA"
	return json_data

def get_tweets(user_data):
	return [tweet['text'] for tweet in user_data]

def get_mean(tweets):
	return float("%.3f" % np.average([tweet['score'] for tweet in tweets]))

def get_std(tweets):
	return float("%.3f" % np.std([tweet['score'] for tweet in tweets]))

def get_profile_url(user_data):
	tweet = user_data[1]
	img_url = tweet['profile_image_url']
	return img_url

def pos_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(205, 68%%, %d%%)" % random.randint(40, 80)

def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(40, 100)

def neg_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(3, 97%%, %d%%)" % random.randint(40, 90)

def make_wordcloud(user_name, sent_words, sentiment):
	text = ""
	for word in sent_words:
		for i in range(1,int(100*np.abs(word[1]))):
			text = text + " " + word[0]

	if text == "": 
		return
	wc = WordCloud(background_color="white",max_words=10, margin=10, random_state=1).generate(text)
	
	
	if sentiment == 'pos':
		wc.recolor(color_func=pos_color_func, random_state=3)
	else:
		wc.recolor(color_func=neg_color_func, random_state=3)
	wc.to_file(os.path.join('static/img/', sentiment+"_wordcloud_"+user_name+".png"))
	# wc.to_file("wordcloud_testing.png")


#=====[ Returns tuple containing top positive and negative words to display to user  ]=====
def get_sent_words(sentChart):
	
	scores=[]
	for word in sentChart:
		scores.append((word,sentChart[word]))
	
	#=====[ Set datatype to tuple of string and score for sorting  ]=====
	dt = np.dtype([('word','S10'),('score',float)])
	sorted_scores = np.array(scores, dtype=dt)
	sorted_scores = np.sort(sorted_scores, order='score')

	#=====[ Set pos/neg scores based on amount of tweets present. Need to change to be  ]=====
	#=====[ based off of amount of NEG/POS tweets present  ]=====
	if len(sorted_scores) < 20:
		index1 = len(sorted_scores)/2
		index2 = len(sorted_scores) - index1
		neg_scores = sorted_scores[:index1]
		pos_scores = sorted_scores[index2:]
	else:
		neg_scores = sorted_scores[:10]
		pos_scores = sorted_scores[-10:]

	neg_scores = [score for score in neg_scores if score[1] < 0]
	pos_scores = [score for score in pos_scores if score[1] > 0]

	return (pos_scores, neg_scores)

def get_emoticon(score):
	if score < -0.75:
		return ('D\':', 'negative')
	elif score < -0.5:
		return ('D:','negative')
	elif score < -0.15:
		return ('):','negative')
	elif score < 0.15:
		return (':|','neutral')
	elif score < 0.5:
		return (':)','positive')
	elif score < 0.75:
		return (':D','positive')
	else:
		return (':\'D',	'positive');

def get_std_img(std):
	if std < 0.2:
		return "std_0.png"
	elif std < 0.5:
		return "std_1.png"
	elif std < 0.8:
		return "std_2.png"
	else:
		return "std_3.png"

def get_sent_similarity(user_data):
	
	scores=[]

	#=====[ Creates counts for each sentiment score in 21 buckets of width 0.1 from -1 to 1  ]=====
	for data in user_data:
		user_score = [0]*21
		for tweet in data:
			score = int(float("%.1f" % tweet['score'])*10+10)
			user_score[score] += 1
		scores.append(user_score)

	#=====[ Forms normalized probability distributions for each users sentiments  ]=====
	x = np.linspace(-1, 1, 100)
	
	mu, std = norm.fit(scores[0])
	p = norm.pdf(x, mu, std)
	mu, std = norm.fit(scores[1])
	p2 = norm.pdf(x,mu,std)
	
	#=====[ Takes Kullback-Leibler Divergence between probability distributions  ]=====
	similarity = float("%.5f" % scipy.stats.entropy(p,p2))

	#=====[ Converts similarity score to a percentage from 10 - 90 to display on compatability spectrum  ]=====
	if similarity < 0.003: 
		return 90
	elif similarity > 0.07:
		return 10
	else:
		return int(10 + ((similarity*100)-1)/6.7*80)

	return int(similarity)



def run_sent_analysis(user_name,api_key):
	successful_retrieval = os.system("python sentiment/recipe.py " + user_name + " 50 " + api_key)

	#=====[ Checks to make sure retrieval of tweets was successful  ]=====
	if successful_retrieval == 256:
		return 1
	elif successful_retrieval == 512:
		return 2
	elif successful_retrieval == 768:
		return 3
	elif successful_retrieval == 1024:
		return 4

	os.system("python sentiment/write.py")
	os.system("python sentiment/delete.py")
	os.system("Rscript sentiment/plot.r " + user_name)
	os.system("rm scores.*")
	os.system("rm time*")
	os.system("mv twitter_sentiment* static/img/")
	return 0
