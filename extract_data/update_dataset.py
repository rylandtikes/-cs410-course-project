#!/usr/bin/env python3
"""
Updates dataset columns with current reddit metrics
"""
import json
import praw
import pandas as pd


def load_data(source_data: str) -> pd.DataFrame:
    """
    Loads dataset
    """
    source_df = pd.read_csv(source_data, lineterminator="\n")
    return source_df


def update_dataset(dataset: str):
    """
    Updates selected columns in existing dataset with new data extracted from
    Reddit API
    """
    for i in range(len(dataset)):
        comment_id = dataset.loc[i, "id"]
        comment = reddit.comment(comment_id)
        dataset.loc[i, "ups"] = comment.ups
        dataset.loc[i, "downs"] = comment.downs
        dataset.loc[i, "link_id"] = comment.link_id
        dataset.loc[i, "total_awards_received"] = comment.total_awards_received
        print(f"record {i} updated")
    return dataset


if __name__ == "__main__":
    with open("creds.json", mode="r", encoding="utf-8") as fh:
        creds = json.loads(fh.read())[0]

    reddit = praw.Reddit(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        user_agent=creds["user_agent"],
    )
    source_dataset = load_data("./data/UkrainianConflict-comments-labeled.csv")
    updated_dataset = update_dataset(source_dataset)

    updated_dataset.to_csv(
        "./data/UkrainianConflict-comments-labeled-updated.csv",
        header=True,
        index=False,
    )
