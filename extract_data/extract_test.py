#!/usr/bin/env python3

import praw
from praw.models import MoreComments
import json
import pandas as pd
import os

DATASET_SIZE = 10
SUBREDDIT = "UkrainianConflict"


def extract_headlines():
    headlines = []

    for submission in reddit.subreddit(SUBREDDIT).new(limit=DATASET_SIZE):
        headlines.append(
            {
                "created_utc": submission.created_utc,
                "id": submission.id,
                "subreddit_id": submission.subreddit_id,
                "downs": submission.downs,
                "ups": submission.ups,
                "author": submission.author,
                "total_awards_received": submission.total_awards_received,
                "body": submission.title,
            }
        )
    return headlines


def extract_comments():
    comments = []

    for top_level_comment in reddit.subreddit(SUBREDDIT).stream.comments():
        if len(comments) == DATASET_SIZE:
            break
        if isinstance(top_level_comment, MoreComments):
            continue
        comments.append(
            {
                "created_utc": top_level_comment.created_utc,
                "id": top_level_comment.id,
                "subreddit_id": top_level_comment.subreddit_id,
                "downs": top_level_comment.downs,
                "ups": top_level_comment.ups,
                "author": top_level_comment.author,
                "total_awards_received": top_level_comment.total_awards_received,
                "body": top_level_comment.body,
            }
        )
    return comments


def write_file(filename: str, reddit_data: list) -> None:
    df = pd.DataFrame(data=reddit_data)
    if not os.path.isfile(filename):
        df.to_csv(filename, header="column_names", index=False)
    else:
        df.to_csv(filename, mode="a", header=False, index=False)


if __name__ == "__main__":
    with open("creds.json") as fh:
        creds = json.loads(fh.read())[0]

    reddit = praw.Reddit(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        user_agent=creds["user_agent"],
    )

    headlines = extract_headlines()
    write_file(filename="./data/UkrainianConflict-headlines.csv", reddit_data=headlines)

    comments = extract_comments()
    write_file(filename="./data/UkrainianConflict-comments.csv", reddit_data=comments)
