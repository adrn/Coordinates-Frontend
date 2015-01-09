# coding: utf-8

""" ...explain... """

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import os
import sys

# Third-party
import numpy as np
import sqlite3
from astropy import log as logger

# Project
from twitterbot.twitter import tweet_stream, tweet_reply
from twitterbot.parse import convert_unit_tweet

conn = sqlite3.connect('tweets.db')
c = conn.cursor()
# c.execute("drop table tweets")
c.execute("""
    create table if not exists tweets (
        id serial primary key,
        tweet_id text,
        username text,
        body text,
        reply_sent integer
    )
""")

# c.execute("create index on tweets "
#           "(syllable_count)")
# c.execute("create index on tweets "
#           "(syllable_count, final_sound, final_word, random)")

for tweet in tweet_stream():
    tweet = tweet[0]
    tweet_id = tweet['id_str']
    tweet_text = tweet['text']
    uname = tweet['user']['screen_name']

    c.execute('SELECT * FROM tweets WHERE tweet_id = "{}"'.format(tweet_id))
    row = c.fetchone()
    if row is not None and row[4] == 1:
        logger.info("Reply already sent.")
        continue

    response = convert_unit_tweet(tweet_text)
    code = tweet_reply("@{0} {1}".format(uname,response), tweet_id, uname)

    if code == 200:
        sent = 1
    else:
        sent = 0
        logger.error("Failed to send reply -- error code: {}.".format(code))

    c.execute("""insert into tweets(tweet_id, username, body, reply_sent)
                  values (?, ?, ?, ?)
              """, (tweet_id, uname, tweet_text, sent))
    conn.commit()

conn.close()