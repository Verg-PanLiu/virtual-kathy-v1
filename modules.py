# functions to be used by the routes
##########
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

# things we need for Tensorflow
import numpy as np
import tflearn
import tensorflow as tf
import random

import boto3
from boto3.dynamodb.conditions import Key
# restore all of our data structures
import pickle
data = pickle.load( open( "training_data", "rb" ) )
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

# import our chat-bot intents file
import json
with open('intents.json') as json_data:
    intents = json.load(json_data)

# Build neural network
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

# Define model and setup tensorboard
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')




# load our saved model
model.load('./model.tflearn')
# create a data structure to hold user context
context = {}

#######################################################################
#######################################################################
# PLEASE REPLACE aws_access_key_id AND aws_secret_access_key WITH YOUR OWN
# ACCESS KEY OF Amazon Web Services (AWS) TO ACCESS DynamoDB. YOU MAY ALSO
# HAVE DIFFERENT TABLE NAMES,FEEL FREE TO MODIFY
dyndb = boto3.resource('dynamodb',
                       region_name='YOUR SERVICE REGION',
                       aws_access_key_id='YOUR ACCESS KEY ID',
                       aws_secret_access_key='YOUR SECRET ACCESS KEY')
table1 = dyndb.Table("Pitt_CS_Courses")
table2 = dyndb.Table("Pitt_CS_Faculty")
table3 = dyndb.Table("Courses_Schedule")
table4 = dyndb.Table("Add_Questions")
table5 = dyndb.Table("Question_list")
metadata_item = {'Questions': "","Answers": ""}
#######################################################################
#######################################################################

# get response to unknown questions
for i in intents['intents']:
    if i['tag'] == 'unknown questions':
        unknown = str(random.choice(i['responses']))

def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=False):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)

    return (np.array(bag))

def classify(sentence):
    # generate probabilities from the model
    results = model.predict([bow(sentence, words)])[0]
    # filter out predictions below a threshold
    results = [[i,r] for i,r in enumerate(results) if r>0.25]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # return tuple of intent and probability
    return return_list

def response(sentence, userID='123', show_details = False):
    results = classify(sentence)
    #print(results)
    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents['intents']:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:
                    # set context for this intent if necessary
                    if 'context_set' in i:
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']

                    # check if this intent is contextual and applies to this user's conversation
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print ('tag:', i['tag'])
                        # a random response from the intent
                        if i['tag'] == "Pitt_CS_Courses":
                            try:
                                course = str(sentence.split(' ')[0].upper() + ' '+ sentence.split(' ')[1].zfill(4))
                                print(course)
                                response = table1.get_item(Key={'Course ID': course})
                                item = response['Item']
                                output = "Course ID: " + str(item['Course ID']) + '\n' \
                                         "Course Name: " + str(item['Course Name']) + '\n' \
                                         "Course Credits: " + str(item['Course Credits']) + '\n' \
                                         "Academic Career: " + str(item['Academic Career']) + '\n' \
                                         "Grade Component: " + str(item['Grade Component']) + '\n' \
                                         "Course Component: " + str(item['Course Component']) + '\n' \
                                         "Course Requirements: " + str(item['Course Requirements']) + '\n' \
                                         "Description: " + str(item['Description']) + '\n'
                            except:
                                output = "Sorry, course '" + sentence +"' is not provided at Pitt, please double check course ID and input format, and type it again."
                        elif i['tag'] == "Pitt_CS_Faculty":
                            try:
                                name = sentence.lower().split(':')[1]
                                response = table2.get_item(Key={"Full Name": name})
                                item = response['Item']
                                output = "Full Name: " + str(item['First Name']) + " " + str(item['Last Name']) + '\n' \
                                         "Email Address: " + str(item['Email Address']) + '\n' \
                                         "Phone Number: " + str(item['Phone Number']) + '\n' \
                                         "Position: " + str(item['Position']) + '\n' \
                                         "Profile: " + str(item['Profile']) + '\n'
                            except:
                                output = "Sorry, " + name + " is not a full-time faculty at CS department, please double check the name and input format, and type it again."
                        elif i['tag'] == "Courses_Schedule":
                            if sentence[0:9] == "schedule:":
                                course = sentence.lower().split(':')[1]
                                number = course.split(' ')[1].zfill(4)
                                # print(course)
                                # print(number)
                                response = table3.query(
                                    IndexName='Course-Number-index',
                                    KeyConditionExpression=Key('Course Number').eq(number)
                                )
                                output = ''
                                if not response['Items']:
                                    output = "Sorry, " + course + " is not offered at pitt, please double check course number and type it again."
                                else:
                                    for item in response['Items']:
                                        output += "Subject Code: " + str(item['Subject Code']) + '\n' \
                                                 "Course Number: " + str(item['Course Number']) + '\n' \
                                                 "Class Number: " + str(item['Class Number']) + '\n' \
                                                 "Days: " + str(item['Days']) + '\n' \
                                                 "Start Time: " + str(item['Start Time']) + '\n' \
                                                 "End Time: " + str(item['End Time']) + '\n' \
                                                 "Room: " + str(item['Room']) + '\n' \
                                                 "Instructor(s): " + str(item['Instructor(s)']) + '\n\n' 
                            else:
                                output = "Please double check the input format, and type it again."
                        elif i['tag'] == "Add_Questions":
                            question = sentence.split(':')[1]
                            metadata_item.update(Questions = question)
                            table4.put_item(Item=metadata_item)
                            output = str(random.choice(i['responses']))
                        elif i['tag'] == "Add_Answers":
                            answer = sentence.split(':')[1]
                            metadata_item.update(Answers = answer)
                            table4.put_item(Item=metadata_item)
                            metadata_item.update(Questions = "", Answers = "")
                            output = str(random.choice(i['responses']))
                        elif i['tag'] == "question category":
                            if sentence[0:9] == "category:":
                                category = sentence.lower().split(':')[1]
                                response = table5.query(
                                    IndexName='Category-index',
                                    KeyConditionExpression=Key('Category').eq(category)
                                )
                                output = ''
                                if not response['Items']:
                                    output = "Sorry, " + category + " is not the category provided, please double check category name and type it again."
                                else:
                                    for item in response['Items']:
                                        output += "Question ID: " + str(item['Question ID']) + '\n'\
                                                  "Question: " + str(item['Question']) + '\n'
                                    output += '\n' + str(random.choice(i['responses']))
                            else:
                                output = "Please double check the input format, and type it again."
                        elif i['tag'] == "questions":
                            if sentence[0:8] == "number: ":
                                try:
                                    question = sentence.lower().split(': ')[1]
                                    response = table5.get_item(Key={"Question ID": question})
                                    item = response['Item']
                                    output = "Question: " + str(item['Question']) + '\n' \
                                             "Answer: " + str(item['Answer']) + '\n'
                                    output += '\n' + str(random.choice(i['responses']))
                                except:
                                    output = "Sorry, question " + question + " is not in the list, please double check the question id, and type it again."
                            else:
                                output = "Please double check the input format, and type it again."
                        else:
                            output = str(random.choice(i['responses']))
                        return "Virtual Kathy: "+ output + '\n'
                    return "Virtual Kathy: " + unknown + '\n'
            results.pop(0)
    else:
        return "Virtual Kathy: " + unknown + '\n'