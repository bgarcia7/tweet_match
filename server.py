from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from flask import abort
from flask import make_response
from flask import redirect

import pymongo
import matplotlib.mlab as mlab
import matplotlib.pyplot as p
import numpy as np
import json
import jinja2
import os
import sentimentTasks as utils
import sys
sys.path.insert(0, 'topic_modeling')
import tweetlda

#=====[ Sets up directories  ]=====
base_dir = os.path.split(os.path.realpath(__file__))[0]
static_dir = os.path.join(base_dir, 'static')

#=====[ Initializes app  ]=====
app = Flask(__name__, static_folder=static_dir)

#====[ Routes to home screen where user enters screen name  ]=====
@app.route("/")
def home():
	# os.system("rm static/img/twitter_*")
	# os.system("rm static/img/neg_*")
	# os.system("rm static/img/pos_*")
	return render_template("index.html.jinja2",tweeters=2)

def sentiment_error_check(statuses, users):
	errors=[]
	for i,status in enumerate(statuses):
		if status == 1:
			print "[FAILURE] Unable to find tweets for @" + users[i]
			error = "*Unable to find tweets for @" + users[i] + " on Twitter"
			errors.append(error)
		elif status == 2:
			print "[FAILURE] Unable to analyze an adequate amount of tweets for @" + users[i]
			error = "*Unable to pull an adequate number of tweets for @" + users[i] + " from Twitter"
			errors.append(error)
		elif status == 3:
			print "[FAILURE] Out of valid API Keys"
			error = "*Sorry, we're out of API requests. Try adding a new API Key! :/"
			errors.append(error)
		elif status == 4:
			print "[FAILURE] The API key entered is invalid"
			error = "*The API Key you entered is invalid"
			errors.append(error)
	return errors

#=====[ Returns results from sentiment and topic analysis  ]=====
@app.route("/get_sentiment/<user_name_1>")
def get_sentiment(user_name_1):

	api_key = "NONE"
	#=====[ Checks to see if username entered in correct format  ]=====
	if user_name_1 == 'UNKNOWN':
		errors = ["*Please make sure to enter a twitter handle"]
		return render_template("index.html.jinja2",errors=errors,tweeters=1)

	if user_name_1[0] == '@':
		user_name_1 = user_name_1[1:]
	
	#=====[ Initialize stats dictionary for each user and compatability scores ]=====
	stats = {}
	stats[user_name_1] = {}
	
	#=====[ Initialize topic modeler  ]=====
	lda = tweetlda.TwitterLDAModel()

	############################ TWITTER USER 1 #######################################

	# =====[ Uses the alchemy framework to run sentiment analysis on twitter user ]=====
	statuses = [utils.run_sent_analysis(user_name_1,api_key)]

	#=====[ Checks to make sure sentiment analysis was successful and no errors were returned  ]=====
	errors = sentiment_error_check(statuses,[user_name_1])
	if len(errors) > 0:
		return render_template("index.html.jinja2",errors=errors,tweeters=1)

	# =====[ Gets json user data containing sentiment chart as well as tweets  ]=====
	user_data_1 = utils.get_json(user_name_1)
	#=====[ Gets image url for profile pic ]=====
	stats[user_name_1]['profile_img_url'] = utils.get_profile_url(user_data_1)
	#=====[ Gets average and standard deviation of sentiment  ]=====
	stats[user_name_1]['sent_mean'] = utils.get_mean(user_data_1[1:])
	stats[user_name_1]['sent_std'] = utils.get_std(user_data_1[1:])
	#=====[ Gets average and std_dev graphics ]=====
	stats[user_name_1]['emoticon'], stats[user_name_1]['sent'] = utils.get_emoticon(stats[user_name_1]['sent_mean'])
	stats[user_name_1]['std_img'] = utils.get_std_img(stats[user_name_1]['sent_std'])
	#=====[ tuple containing positive and negative entities  ]=====
	entity_scores = utils.get_sent_words(user_data_1[0])
	stats[user_name_1]['pos_scores'] = entity_scores[0]
	stats[user_name_1]['neg_scores'] = entity_scores[1]
	#=====[ Makes wordcloud  ]=====
	stats[user_name_1]['pos_wc'] = len(entity_scores[0]) > 0 
	stats[user_name_1]['neg_wc'] = len(entity_scores[1]) > 0 
	utils.make_wordcloud(user_name_1, entity_scores[0], 'pos')
	utils.make_wordcloud(user_name_1, entity_scores[1], 'neg')
	#=====[ Gets top topics for a given user  ]=====
	stats[user_name_1]['top_topics'] = lda.distill_top_topics(user_data_1[1:],5)

	print "[SUCCESSFUL] Stats aggregated for one user"

	return render_template("results.html.jinja2", user_name_1=user_name_1, stats=stats, tweeters=1)


@app.route("/compatability/<user_name_1>/<user_name_2>")
def compatability(user_name_1, user_name_2):

	api_key = "NONE"
	#=====[ Checks to see if username entered in correct format  ]=====
	if (user_name_1 == 'UNK' and user_name_2 == 'UNK'):
		errors = ["*Please make sure to enter two twitter handles"]
		return render_template("index.html.jinja2",errors=errors,tweeters=2)

	if user_name_1[0] == '@':
		user_name_1 = user_name_1[1:]
	if user_name_2[0] == '@':
		user_name_2 = user_name_2[1:]

	#=====[ Initialize stats dictionary for each user and compatability scores ]=====
	stats = {}
	stats[user_name_1] = {}
	stats[user_name_2] = {}
	stats['compatability'] = {}

	#=====[ Initialize topic modeler  ]=====
	lda = tweetlda.TwitterLDAModel()

	#=====[ Uses the alchemy framework to run sentiment analysis on twitter user ]=====
	statuses = [utils.run_sent_analysis(user_name_1,api_key), utils.run_sent_analysis(user_name_2,api_key)]

	#=====[ Checks to make sure sentiment analysis was successful and no errors were returned  ]=====
	errors = sentiment_error_check(statuses,[user_name_1,user_name_2])
	if len(errors) > 0:
		return render_template("index.html.jinja2",errors=errors,tweeters=2)


	############################ TWITTER USER 1 #######################################

	# =====[ Gets json user data containing sentiment chart as well as tweets  ]=====
	user_data_1 = utils.get_json(user_name_1)
	#=====[ Gets image url for profile pic ]=====
	stats[user_name_1]['profile_img_url'] = utils.get_profile_url(user_data_1)
	#=====[ Gets average and standard deviation of sentiment  ]=====
	stats[user_name_1]['sent_mean'] = utils.get_mean(user_data_1[1:])
	stats[user_name_1]['sent_std'] = utils.get_std(user_data_1[1:])
	#=====[ Gets average and std_dev graphics ]=====
	stats[user_name_1]['emoticon'], stats[user_name_1]['sent'] = utils.get_emoticon(stats[user_name_1]['sent_mean'])
	stats[user_name_1]['std_img'] = utils.get_std_img(stats[user_name_1]['sent_std'])
	#=====[ tuple containing positive and negative entities  ]=====
	entity_scores = utils.get_sent_words(user_data_1[0])
	stats[user_name_1]['pos_scores'] = entity_scores[0]
	stats[user_name_1]['neg_scores'] = entity_scores[1]
	#=====[ Makes wordcloud  ]=====
	stats[user_name_1]['pos_wc'] = len(entity_scores[0]) > 0 
	stats[user_name_1]['neg_wc'] = len(entity_scores[1]) > 0 
	utils.make_wordcloud(user_name_1, entity_scores[0], 'pos')
	utils.make_wordcloud(user_name_1, entity_scores[1], 'neg')
	#=====[ Gets top topics for a given user  ]=====

	stats[user_name_1]['top_topics'] = lda.distill_top_topics(user_data_1[1:],5)
	############################ TWITTER USER 2 #######################################

	# =====[ Gets json user data containing sentiment chart as well as tweets  ]=====
	user_data_2 = utils.get_json(user_name_2)
	#=====[ Gets image url for profile pic ]=====
	stats[user_name_2]['profile_img_url'] = utils.get_profile_url(user_data_2)
	#=====[ Gets average and standard deviation of sentiment  ]=====
	stats[user_name_2]['sent_mean'] = utils.get_mean(user_data_2[1:])
	stats[user_name_2]['sent_std'] = utils.get_std(user_data_2[1:])
	#=====[ Gets average and std_dev graphics ]=====
	stats[user_name_2]['emoticon'], stats[user_name_2]['sent'] = utils.get_emoticon(stats[user_name_2]['sent_mean'])
	stats[user_name_2]['std_img'] = utils.get_std_img(stats[user_name_2]['sent_std'])
	#=====[ tuple containing positive and negative entities  ]=====
	entity_scores = utils.get_sent_words(user_data_2[0])
	stats[user_name_2]['pos_scores'] = entity_scores[0]
	stats[user_name_2]['neg_scores'] = entity_scores[1]
	#=====[ Makes wordclouds  ]=====
	stats[user_name_2]['pos_wc'] = len(entity_scores[0]) > 0 
	stats[user_name_2]['neg_wc'] = len(entity_scores[1]) > 0 


	utils.make_wordcloud(user_name_2, entity_scores[0], 'pos')
	utils.make_wordcloud(user_name_2, entity_scores[1], 'neg')

	#=====[ Gets top topics for a given user  ]=====
	stats[user_name_2]['top_topics'] = lda.distill_top_topics(user_data_2[1:],5)

	#=====[ Computes topic and sentiment similarity scores using cosine and KL divergence, respectively  ]=====
	stats['compatability']['topic_similarity'] = lda.get_topic_similarity([user_data_1[1:],user_data_2[1:]])
	stats['compatability']['sentiment_similarity'] = utils.get_sent_similarity([user_data_1[1:],user_data_2[1:]])

	print "[SUCCESSFUL] Stats aggregated for both users"

	# return render_template("results.html.jinja2", user_name=user_name_2, pos_scores=entity_scores[0], neg_scores=entity_scores[1], sent_mean=stats[user_name_2]['sent_mean'], sent_std=stats[user_name_2]['sent_std'])


	return render_template("compatabilityResults.html.jinja2", user_name_1=user_name_1, user_name_2=user_name_2, stats=stats, tweeters=2)

#=====[ Adds necessary headers to prevent caching  ]=====
@app.after_request
def add_header(response):
	"""
	Add headers to both force latest IE rendering engine or Chrome Frame,
	and also to cache the rendered page for 10 minutes.
	"""
	response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
	response.headers['Cache-Control'] = 'public, max-age=0, no-store'
	return response

@app.route("/about")
def about():
	return render_template("about.html.jinja2")


if __name__ == "__main__":
	app.run()