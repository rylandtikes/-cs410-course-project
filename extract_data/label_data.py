#!/usr/bin/env python3
"""
Cleans and labels data extracted from Reddit API.
Input: Raw Reddit headline and comment CSV
Output: Labeled and clean headline and comment CSV
"""

import string
from datetime import datetime
import argparse
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd
import nltk

nltk.download("vader_lexicon")


def load_data(source_data: str) -> pd.DataFrame:
    """
    Loads the raw data extracted from Reddit
    """
    source_df = pd.read_csv(source_data, lineterminator='\n')
    return source_df


def rank_data(source_df: pd.DataFrame) -> list:
    """
    Uses Vader Sentiment Analyzer to rank text as positive, negative, or
    nuetral using lexicon.
    """
    sia = SIA()
    sia_data = []
    for i in range(len(source_df)):
        author = source_df.loc[i, "author"]
        # Comments made by AutoModerator should be excluded / cleaning step
        if author == "AutoModerator":
            continue

        headline = clean_body(source_df.loc[i, "body"])
        pol_score = sia.polarity_scores(headline)

        # Adding data from input dataframe to pol_score dictionary
        pol_score["created_utc"] = datetime.utcfromtimestamp(
            int(source_df.loc[i, "created_utc"])
        ).strftime("%Y-%m-%d")
        pol_score["id"] = source_df.loc[i, "id"]
        pol_score["subreddit_id"] = source_df.loc[i, "subreddit_id"]
        pol_score["downs"] = source_df.loc[i, "downs"]
        pol_score["ups"] = source_df.loc[i, "ups"]
        pol_score["author"] = author
        pol_score["total_awards_received"] = source_df.loc[i, "total_awards_received"]
        pol_score["headline"] = headline
        pol_score["city"] = contains_city(headline)

        sia_data.append(pol_score)

    return sia_data


def clean_body(line: str) -> str:
    """
    Filters comment/headline to remove all but String of ASCII characters which
    are considered printable. This is a combination of digits, ascii_letters,
    punctuation, and whitespace. / cleaning step
    """
    printable = set(string.printable)
    return "".join(filter(lambda x: x in printable, line)).strip()


def contains_city(headline: str) -> str:
    """
    Returns first city found in comment/headline from top 10 by population
    """
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


def process_dataset(input_dataset: str, output_dataset: str) -> None:
    """
    Executes load, rank, and label steps on the input dataset and
    writes a labeled CSV
    """
    source_df = load_data(input_dataset)

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
    # Sort by date
    sorted_labeled_df = labeled_df.sort_values(by="created_utc", ascending=False)

    # Write labeled data to CSV
    sorted_labeled_df.to_csv(output_dataset, encoding="utf-8", index=False)


def main():
    # process headlines
    process_dataset(
        input_dataset=args.headlines_input_dataset,
        output_dataset=args.headlines_output_dataset,
    )

    # process comments
    process_dataset(
        input_dataset=args.comments_input_dataset,
        output_dataset=args.comments_output_dataset,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--headlines-input-dataset",
        type=str,
        required=False,
        help="raw headlines dataset extracted from Reddit API",
        default="./data/UkrainianConflict-headlines.csv",
    )
    parser.add_argument(
        "--headlines-output-dataset",
        type=str,
        required=False,
        help="cleaned and labeled headlines dataset",
        default="./data/UkrainianConflict-headlines-labeled.csv",
    )
    parser.add_argument(
        "--comments-input-dataset",
        type=str,
        required=False,
        help="raw comments dataset extracted from Reddit API",
        default="./data/UkrainianConflict-comments.csv",
    )
    parser.add_argument(
        "--comments-output-dataset",
        type=str,
        required=False,
        help="cleaned and labeled comments dataset",
        default="./data/UkrainianConflict-comments-labeled.csv",
    )
    args = parser.parse_args()
    main()
