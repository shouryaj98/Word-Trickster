import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import sqlite3
import json

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def new_game():

    total = 34
    l = []
    for i in range(1,total+1):
        l.append(i)
    session.attributes['t'] = total
    session.attributes['l'] = json.dumps(l)
    session.attributes['ans'] = " "
    session.attributes['change'] = " "
    session.attributes['current_q'] = -1
    session.attributes['score'] = 0
    welcome_msg = "Welcome to word trickster. I'm going to give you three clues, you need to guess the word. If you require help at any point in the game, just say help. Are you ready for the first question?"
    return question(welcome_msg)

@ask.intent("AskIntent")
def next_round():
    round_msg = " "
    if session.attributes['change'] == True:
        session.attributes['change'] = " "
        round_msg += "Okay question changed."

    if session.attributes['ans'] == " ":
        number = ran_no()
        t = 0
        while number == int(session.attributes['current_q']):
            number = ran_no()
            t += 1
            if t==session.attributes['t']:
                session.attributes['current_q'] = -1
                return question("Sorry I cannot change the question since this is the last question of the game, you need to answer it to win it. Do you want to play?").reprompt("You are so close to defeating the word trickster! Don't give up now, come on, do you want to try the last question? ")
        session.attributes['current_q'] = number
    
    conn = sqlite3.connect('question.db')
    cursor = conn.execute("SELECT * from question where id ="+str(session.attributes['current_q']))
    for row in cursor:
        hint = row[1].split(',')
        answer = row[2]
    conn.close()
    round_msg += " The clues are "
    for h in hint[:-1]:
        round_msg += (h + ", ") 
    round_msg += "and " + hint[-1]
    session.attributes['ans'] = answer
    return question(round_msg).reprompt("Hey, you there? "+round_msg)

def ran_no():
    l = json.loads(session.attributes['l'])
    if len(l)==0:
        return -1
    n = randint(0,len(l)-1)
    t = l[n]
    return t

@ask.intent("AnswerIntent", convert={'ans': str})
def answer(ans):
    print("\n"+ans+"\n")
    a = ans.split(' ')  
    if len(a) == 1 and session.attributes['ans'] != " ":
        anss = session.attributes['ans']
        if ans == anss:
            l = json.loads(session.attributes['l'])
            l.remove(session.attributes['current_q'])
            session.attributes['l'] = json.dumps(l)
            session.attributes['current_q'] = -1
            session.attributes['score'] += 1
            if len(l)!=0:
                msg = "Correct! Do you want to play further?"
                session.attributes['ans'] = " "
            else:
                return statement("Congratulations! you have defeated word trickster, we hope you had a wonderful experience, I sure did. So goodbye for now, have a nice day!")
        else:
            msg = "Sorry, your answer "+ans+" is incorrect. Do you want to try again?"
        return question(msg).reprompt("Hmmm, don't you want to try again, say yes or no ?")
    else:
        return fallback()
        
@ask.intent("ChangeQuestion")
def change():
    session.attributes['change'] = True
    session.attributes['ans'] = " "
    return next_round()

@ask.intent("NoIntent")
def no():
    if session.attributes['ans'] == " ":
        return stop()
    else:
        session.attributes['ans'] = " "
        return question("Do you want to try another question?").reprompt("Hey, are you asleep, am i that boring?, do you want to try another question?")

@ask.intent("ScoreIntent")
def score():
    return question("Your score is "+str(session.attributes['score'])+". Do you want to continue with the game ?")

@ask.intent("AMAZON.FallbackIntent")
def fallback():
    session.attributes['ans'] = " "
    return question("I am not sure what you mean. Do you want to keep playing ?").reprompt("Knock knock, hello there, do you want to keep playing ? ") 

@ask.intent("AMAZON.StopIntent")
def stop():
    print("Stop")
    return statement("Okay. Goodbye") 

@ask.intent("AMAZON.CancelIntent")
def cancel():
    print("Cancel")
    return statement("Okay. Goodbye") 

@ask.intent("AMAZON.HelpIntent")
def help():
    msg = "Word Trickster is a game in which I'll give you three hints and you'll need to guess the word associated with those three hints, for example, if the hints are animal,playful, man's best friend then the answer is dog. You will be scored on the basis of the number of the correct answers, you can choose to skip questions if you are stuck, but, if you want to defeat word trickster you need to answer all the questions. This means, if you have skipped a question it will come again later on in the game, and only after answering all will you be declared a winner. Ready?"
    session.attributes['ans'] = " "
    return question(msg) 


if __name__ == '__main__':
    app.run(debug=True)
