#!/usr/bin/env python

# Given posts between two dates, randomly select a winner.
# Each post is granted one raffle entry
# Example usage:
#   ./raffle.py 2019-11-18 2019-11-22


from datetime import datetime, timedelta
import json
import os
from time import sleep
from random import choice
import sys
import re
import requests

# The user must provide a start and end date
if len(sys.argv) < 3:
    sys.exit("Please specify a start and end date.")

# Try parsing the dates
since_date =  datetime.strptime(sys.argv[1], "%Y-%m-%d")
to_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")

# Add one more day to to date so that it covers previous day fully
to_date = to_date + timedelta(days=1)

# Sleep time in seconds (to not go above api limit)
sleep_time = 1.5
api_key = os.environ.get('DISCOURSE_API_KEY')
username = os.environ.get('DISCOURSE_API_USER')
api_base = os.environ.get('DISCOURSE_BASE', 'https://ask.cyberinfrastructure.org')

# Assert credentials are provided
if not api_key or not username:
    sys.exit("Please export your DISCOURSE_API_KEY and DISOURCE_API_USER")

# Requests must be authenticated
headers = {
    "Api-Key": api_key,
    "Api-Username": username
}

# Get all categories
url = "%s/categories.json" % api_base
response = requests.get(url, headers=headers)
if response.status_code != 200:
    sys.exit("Error getting discourse categories.")

categories = response.json()['category_list']['categories']
print("Found %s categories" % len(categories))

# We first need to get a full list of all topics
topics = []

for category in categories:
    print("Parsing Category is %s" % category['name'])
    url = "%s/c/%s.json" %(api_base, category['slug'])

    new_topics = []
    while url is not None:
        print("Getting %s" % url)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            # users, primary_groups, topic_list
            results = response.json().get('topic_list', {})
            new_topics = new_topics + results.get('topics', [])
            
            # /c/q-a?page=1
            url = results.get('more_topics_url', None)

            if url is not None:

                # We have to add the json
                url, params = url.split('?', 1)
                url = "%s%s.json?%s" %(api_base, url, params)
                sleep(sleep_time)

    print("Found %s topics for category %s" % (len(new_topics), category['slug']))
    topics = topics + new_topics
    

# Keep a lookup of counts for each user, within dates
counts = {}

# A function to parse a datetime string, determine if within range
def within_range(datestr, since_date, to_date):

    # We only need the day to determine if in range
    datestr = datestr.split('T')[0]
    post_date =  datetime.strptime(datestr, "%Y-%m-%d")
    return post_date > since_date and post_date < to_date

# pretty print a json object to file
def write_json(json_object, output_file, mode='w'):
    with open(output_file, mode) as filey:
        filey.writelines(json.dumps(json_object, indent=4))

contenders = []

# Now we want to get the posts for each topic!
for topic in topics:
    
    # First we need to get all post ids for a topic
    url = "%s/t/%s/%s.json" %(api_base, topic['slug'], topic['id'])

    print("Exporting post %s" % url)
    response = requests.get(url, headers=headers, data={'print': True})
    if response.status_code == 200:

        # This is all posts for a single topic
        details = response.json()
        for post in details['post_stream']['posts']:
            if within_range(post['created_at'], since_date, to_date):
                post_url = "%s/t/%s/%s/%s" % (api_base, post['topic_slug'], post['topic_id'], post['post_number'])
                contenders.append({"username": post['username'],
                                   "content": post['cooked'],
                                   "url": post_url})

        sleep(sleep_time)
    else:
        print("Issue with %s" % url)

# Randomly select a winner!
winner = choice(contenders)
print("We have a winner!")
print("Username: %s" % winner['username'])
print("Url: %s" % winner['url'])
print("Content: %s" % winner['content'])

# Save contenders to file
now = datetime.now()
datestr = "%s-%s-%s" %(now.year, now.month, now.day)
output_file = os.path.join('contests', "contenders-%s.json" % datestr)
write_json(contenders, output_file)
