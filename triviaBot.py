from datetime import datetime

import config
import csv
import random
import re
import requests
import tweepy

#access tweepy

auth = tweepy.OAuthHandler(config.consumerKey, config.consumerKeySecret)
auth.set_access_token(config.accessToken, config.accessTokenSecret)

api = tweepy.API(auth)

## set the url to the trivia api

triviaURL = "https://the-trivia-api.com/api/questions?limit=1"

## set the search query so that we search for mentions of the bot.

searchQuery = '@MCCompBot'

retweet_filter='-filter:retweets'

q=searchQuery+retweet_filter

## create questions list and questions_info

questions_info = ['statusID', 'correctAnswer']
questions = []

## load csv file

with open('questions.csv', 'r') as csvFile:
    questions = [{k: int(v) for k, v in row.items()}
                for row in csv.DictReader(csvFile, skipinitialspace=True)]

## getQuestion and getGenQuestion

def getQuestion(category: str, sid: int):
    params = {'categories': category}
    r = requests.get(url = triviaURL, params=params)
    question = r.json()[0]
    sendTweet(question, sid)

def getGenQuestion(sid: int):
    r = requests.get(url = triviaURL)
    question = r.json()[0]
    sendTweet(question, sid)

## function to send a Tweet
    
def sendTweet(question, sid):
    tweet = makeTweet(question)
    sentTweet = api.update_status(status=tweet[0], in_reply_to_status_id = sid, auto_populate_reply_metadata=True)
    questions.append({'statusID': sentTweet.id, 'correctAnswer': tweet[1]})
## function to make the text of a tweet

def makeTweet(question):
    tweet = question['question']
    answers = [question['correctAnswer']] + question["incorrectAnswers"]
    random.shuffle(answers)
    correctNumber = 0
    for index, i in enumerate(answers):
        if i == question['correctAnswer']:
            correctNumber = index
        tweet += '\n'
        tweet += str(index + 1) + ": " + i
    return [tweet, correctNumber + 1]

def searchTweet(questions, id):
    for i in questions:
        if i['statusID'] == id:
            return i['correctAnswer']
    return -1

def removeTweet(id):
    for i in questions:
        if i['statusID'] == id:
            selected = i
            questions.remove(selected)
            return
    

## find sinceID

f = open("since.txt", "r")
sinceID = int(f.read())
f.close()

## get tweets

print(sinceID)

tweets = [status for status in tweepy.Cursor(api.search_tweets, q=q, since_id = sinceID).items()]

## create maxID variable

maxID = 0

## iterate through tweets, ask them question or reply to them whether they were right or not

for s in tweets:
    print(s.id)

    if s.in_reply_to_status_id != None:
        statusID = s.in_reply_to_status_id
        correctAnswer = searchTweet(questions, statusID)
        questionAnswer = re.search(r'\d+', s.text).group()
        print(questionAnswer)
        if correctAnswer != -1:
            removeTweet(statusID)
            if correctAnswer == int(questionAnswer):
                api.update_status(status="That is correct! Sent at " + datetime.now().strftime("%H:%M"), in_reply_to_status_id = s.id, auto_populate_reply_metadata=True)
            else:
                api.update_status(status="That is incorrect! Sent at " + datetime.now().strftime("%H:%M") + "EST", in_reply_to_status_id = s.id, auto_populate_reply_metadata=True)
        continue

    text = s.text.lower()
    hashtags = s.entities.get('hashtags')
    categories = ["sports", "geography", "history"]
    maxID = max(maxID, s.id)

    if hashtags:
        category = hashtags[0]['text']
        if category in categories:
            getQuestion(category=category, sid=s.id)
            continue
    getGenQuestion(sid=s.id)

print(questions)

## save csv file

with open('questions.csv', 'w') as csvFile:
    writer = csv.DictWriter(csvFile, fieldnames=questions_info)
    writer.writeheader()
    writer.writerows(questions)

## write new max ID

f = open("since.txt", "w")
f.write(str(max(maxID, sinceID)))
f.close()