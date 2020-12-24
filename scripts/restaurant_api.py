#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request
import datetime
import random
from random_username.generate import generate_username


app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')

uid_a = 0
os = ['Apple iPhone', 'Android Device', 'PC', 'Apple Mac', 'Raspberyy Pi']
fave_food = ['Mexicsn', 'Thai', 'Pizza', 'American', 'BBQ', 'No Preference']
coupon = ['Yes'] * 25 + ['No'] * 75

# function to generate event timestamp weighted towards weekends and evenings
def get_rand_datetime():
    app_days = None
    v_hour = ['10','11','12','13','14','15','16','21'] + ['17','18','20'] * 5 + ['19'] * 10 
    v_min = list(range(1,60)) 
    jan_days = [4,5,11,12,18,19,25,26] * 5 + [1,2,3,6,7,8,9,10,13,14,15,16,17,20,21,22,23,24,27,28,29,30,31]
    feb_days = [1,2,8,9,15,16,22,23] * 5 + [3,4,5,6,7,10,11,12,13,14,17,18,19,20,21,24,25,26,27,28]
    mar_days = [1,2,8,9,15,16,22,23,29,30] * 5 + [3,4,5,6,7,10,11,12,13,14,17,18,19,20,21,24,25,26,27,28,31]
    apr_days = [5,6,12,13,19,20,26,27] * 5 + [1,2,3,4,7,8,9,10,11,14,15,16,17,18,21,22,23,24,25,28,29,30]
    may_days = [3,4,10,11,17,18,24,25,31] * 5 + [1,2,5,6,7,8,9,12,13,14,15,16,19,20,21,22,23,26,27,28,29,30]
    jun_days = [1,7,8,14,15,21,22,28,29] * 5 + [2,3,4,5,6,9,10,11,12,13,16,17,18,19,20,23,24,25,26,27,30,31]
    v_month = ['01','02','03','04','05','06']
    v_year = '2019'
    
    app_month = random.choice(v_month)
    if app_month == '01': app_days = random.choice(jan_days)
    elif app_month == '02': app_days = random.choice(feb_days)
    elif app_month == '03': app_days = random.choice(mar_days)
    elif app_month == '04': app_days = random.choice(apr_days) 
    elif app_month == '05': app_days = random.choice(may_days)
    else: app_days = random.choice(jun_days)

    app_timestamp = v_year + '-' \
                + app_month + '-' \
                + str(app_days) + ' ' \
                + random.choice(v_hour) + ':' \
                + str(random.choice(v_min)) + ':' \
                + str(random.choice(v_min))

    return(app_timestamp)

def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())

@app.route("/")
def default_response():
    default_event = {'event_type': 'default',
                     'uid': 'na',
                     'event_timestamp': get_rand_datetime(),
                     'description': 'default'}
    log_to_kafka('menu_app_events', default_event)
    return "This is the default response\n"

# Register a new user - we want to keep track of the userid so we just keep adding one
@app.route("/new_user")
def new_user():
    global uid_a
    new_user_event = {'event_type': 'new_user',
                      'uid': 'A' + str(uid_a).zfill(5),
                      'event_timestamp': get_rand_datetime(),
                      'description': generate_username(1)[0]}
    log_to_kafka('menu_app_events', new_user_event)
    uid_a += 1
    return "New user registered\n"

# Login to the app logins that will do stuff in the app (randomly)
@app.route("/login")
def login():
    global os
    login_event = {'event_type': 'login',
                   'uid': 'A' + str(random.randint(0,999)).zfill(5),
                   'event_timestamp': get_rand_datetime(),
                   'description': random.choice(os)}
    log_to_kafka('menu_app_events', login_event)
    return "User logged in\n"

# Login to the app logins that don't do anything in the app
@app.route("/login0")
def login0():
    global os
    login_event0 = {'event_type': 'login',
                   'uid': 'A' + str(random.randint(1000,9999)).zfill(5),
                   'event_timestamp': get_rand_datetime(),
                   'description': random.choice(os)}
    log_to_kafka('menu_app_events', login_event0)
    return "User logged in\n"

@app.route("/create_profile")
def create_profile():
    global fave_food
    create_profile_event = {'event_type': 'create_profile',
                           'uid': 'A' + str(random.randint(0,999)).zfill(5),
                           'event_timestamp': get_rand_datetime(),
                           'description': random.choice(fave_food)}
    log_to_kafka('menu_app_events', create_profile_event)
    return "User created profile\n"

@app.route("/menu_search")
def menu_search():
    menu_search_event = {'event_type': 'menu_search',
                         'uid': 'A' + str(random.randint(0,999)).zfill(5),
                         'event_timestamp': get_rand_datetime(),
                         'description': request.args['menu']}
    log_to_kafka('menu_app_events', menu_search_event)
    return "User searched menus\n"

@app.route("/order_food")
def order_food():
    global coupon
    order_food_event = {'event_type': 'order_food',
                        'uid': 'A' + str(random.randint(0,999)).zfill(5),
                        'event_timestamp': get_rand_datetime(),
                        'description': request.args['menu'],
                        'price': int(random.randint(10,50)),
                        'coupon': random.choice(coupon)}
    log_to_kafka('menu_app_events', order_food_event)
    return "user ordered food\n"

@app.route("/post_review")
def post_review():
    post_review_event = {'event_type': 'post_review',
                         'uid': 'A' + str(random.randint(0,999)).zfill(5),
                         'event_timestamp': get_rand_datetime(),
                         'description': request.args['review']}
    log_to_kafka('menu_app_events', post_review_event)
    return "User posted review\n"

@app.route("/post_rating")
def post_rating():
    post_rating_event = {'event_type': 'post_rating',
                         'uid': 'A' + str(random.randint(0,999)).zfill(5),
                         'event_timestamp': get_rand_datetime(),
                         'description': request.args['stars']}
    log_to_kafka('menu_app_events', post_rating_event)
    return "User posted ratingt\n"
