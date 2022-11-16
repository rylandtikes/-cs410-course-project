#!/usr/bin/env python3

import nltk

nltk.download("vader_lexicon")

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd
import string
from datetime import datetime


def load_data(source_data: str) -> pd.DataFrame:
    """
    Loads the raw data extracted from Redis
    """
    source_df = pd.read_csv(source_data)
    return source_df


def rank_data(source_df: pd.DataFrame) -> pd.DataFrame:
    """
    Uses Vader Sentiment Analyzer to rank text as positive, negative, or
    nuetral using lexicon.
    """
    sia = SIA()
    sia_data = []
    for i in range(len(source_df)):
        headline = clean_body(source_df.loc[i, "body"])
        pol_score = sia.polarity_scores(headline)

        pol_score["created_utc"] = datetime.utcfromtimestamp(
            int(source_df.loc[i, "created_utc"])
        ).strftime("%Y-%m-%d")
        pol_score["id"] = source_df.loc[i, "id"]
        pol_score["subreddit_id"] = source_df.loc[i, "subreddit_id"]
        pol_score["downs"] = source_df.loc[i, "downs"]
        pol_score["ups"] = source_df.loc[i, "ups"]
        pol_score["author"] = source_df.loc[i, "author"]
        pol_score["total_awards_received"] = source_df.loc[i, "total_awards_received"]
        pol_score["headline"] = headline
        pol_score["city"] = contains_city(headline)

        sia_data.append(pol_score)

    return sia_data


def clean_body(line: str) -> str:
    printable = set(string.printable)
    return "".join(filter(lambda x: x in printable, line)).strip()


def contains_city(headline: str) -> str:
    ukraine_top_cities = [
        "Kyiv",
        "Kharkiv",
        "Odesa",
        "Dnipro",
        "Donetsk",
        "Zaporizhzhia",
        "Lviv",
        "Kryvyi Rih",
        "Mykolaiv",
        "Sevastopol",
    ]

    for city in ukraine_top_cities:
        if city.lower() in headline.lower():
            return city
    return ""


def label_data(sia_data: list, thresh_neg: float, thresh_pos: float) -> pd.DataFrame:
    """
    -1 (Extremely Negative) to 1 (Extremely Positive)
    """
    labeled_df = pd.DataFrame.from_records(sia_data)
    labeled_df["label"] = 0
    labeled_df.loc[labeled_df["compound"] > thresh_pos, "label"] = 1
    labeled_df.loc[labeled_df["compound"] < thresh_neg, "label"] = -1
    return labeled_df


def process_dataset(input_datset: str, output_dataset: str) -> None:
    source_df = load_data(input_datset)

    sia_data = rank_data(source_df)

    labeled_df = label_data(sia_data, -0.2, 0.2)

    # Change order of dataframe columns
    labeled_df = labeled_df[
        [
            "created_utc",
            "id",
            "subreddit_id",
            "downs",
            "ups",
            "author",
            "total_awards_received",
            "neg",
            "neu",
            "pos",
            "compound",
            "label",
            "city",
            "headline",
        ]
    ]

    # Write labeled data to CSV
    labeled_df.to_csv(output_dataset, encoding="utf-8", index=False)


def main():
    # process headlines
    process_dataset(
        input_datset="./data/UkrainianConflict-headlines.csv",
        output_dataset="./data/UkrainianConflict-headlines-labeled.csv",
    )

    # process comments
    process_dataset(
        input_datset="./data/UkrainianConflict-comments.csv",
        output_dataset="./data/UkrainianConflict-comments-labeled.csv",
    )


if __name__ == "__main__":
    main()
