#!/usr/bin/env python3

import praw
from praw.models import MoreComments
import json
import pandas as pd

DATASET_SIZE = 1000

def extract_headlines():
    headlines = set()

    for submission in reddit.subreddit("UkrainianConflict").new(limit=DATASET_SIZE):
        headlines.add(submission.title)

    df = pd.DataFrame(data=list(headlines))
    df.to_csv("./data/UkrainianConflict-headlines.csv", index=False)


def extract_comments():
    comments = []

    for top_level_comment in reddit.subreddit("UkrainianConflict").stream.comments():
        if len(comments) == DATASET_SIZE:
            break
        if isinstance(top_level_comment, MoreComments):
            continue
        comments.append(top_level_comment.body)
        print(len(comments))

    df = pd.DataFrame(data=comments)
    df.to_csv("./data/UkrainianConflict-comments.csv", index=False)


if __name__ == "__main__":
    with open("creds.json") as fh:
        creds = json.loads(fh.read())[0]

    reddit = praw.Reddit(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        user_agent=creds["user_agent"],
    )
    extract_headlines()
    extract_comments()
