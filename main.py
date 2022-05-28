from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


from modules import clean_up_sentence
from modules import bow
from modules import classify
from modules import response

##########
# ####


# things we need for NLP
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

# things we need for Tensorflow
import numpy as np
import tflearn
import tensorflow as tf
import random

# restore all of our data structures
import pickle


# import our chat-bot intents file
import json


###################
import tweepy

app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'
keys = {
    "api_token": "JTADJ57r5Fi3MpDfwU228lwm6",
    "api_token_secret":"PxiHGhMoR0h57o7lWHOjjOKsiwNweNABeVtYCCEdyRj80vsjla",
    "access_token" : "1307426306330710016-AtQvDC0UwrVkTyVS8VaGrpdNvCToki",
    "access_token_secret" : "jfOfYWvAmZtbdLnFIO55lFJEYh3HwkmCMW91wXNX2UjVI"
}
auth = tweepy.OAuthHandler(keys["api_token"], keys["api_token_secret"])
auth.set_access_token(keys["access_token"], keys["access_token_secret"])
# Flask-Bootstrap requires this line
Bootstrap(app)



class VirtualKathyForm(FlaskForm):
    incTweet = StringField(' ', validators=[DataRequired()])
    submit4 = SubmitField('Enter')

# all Flask routes below
@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('main.html')

memo = ""
@app.route('/virtualkathy', methods=['GET', 'POST'])
def vk():
    global memo
    vkForm = VirtualKathyForm()
    userQuestion = vkForm.incTweet.data
    vkResponse = " "
    if vkForm.incTweet.data and vkForm.validate():
        memo = memo + "-> @Question: " + userQuestion + "\n---------------------------------------------------------------------------------\n"
        vkResponse = response(userQuestion)
        memo = memo + str(vkResponse) + "============================================================\n"
        return render_template('vk.html', form1=vkForm, response = memo)

    return render_template('vk.html', form1=vkForm)

  
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
