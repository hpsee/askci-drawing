#!/usr/bin/env python

# Given posts between two dates, randomly select a winner.
# Each post is granted one raffle entry
# Example usage:
#   ./raffle.py 2019-11-18 2019-11-22


import json
from random import choice
import os
import sys

# The user must provide a start and end date
if len(sys.argv) < 2:
    sys.exit("Please include a json file of contenders to select.")

json_file = sys.argv[1]

if not os.path.exists(json_file):
    sys.exit("%s does not exist." % json_file)

with open(json_file, 'r') as filey:
    contenders = json.loads(filey.read())

# We need a list to select from
if not isinstance(contenders, list):
    sys.exit("Malformed data, should be list of contenders.")

# Contenders with admins
print("Found %s posts!" % len(contenders))

# Remove admins
admins = ['jma', 'vsoch']
contenders = [x for x in contenders if x['username'] not in admins]
print("%s are contenders!" % len(contenders))

# Randomly select a winner!
winner = choice(contenders)
print("We have a winner!")
print("Username: %s" % winner['username'])
print("Url: %s" % winner['url'])
print("Content: %s" % winner['content'])
