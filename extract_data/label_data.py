#!/usr/bin/env python3

import nltk

nltk.download("vader_lexicon")

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd


DATASET = "./data/UkrainianConflict-comments-1000.csv"
LABELED_CSV_OUTFILE = "./data/UkrainianConflict-comments-1000-labeled-n.csv"


def load_data(source_data: str) -> list:
    """
    Loads the raw data extracted from Redis
    """
    with open(source_data) as fh:
        loaded_source_data = fh.readlines()
    return loaded_source_data


def rank_data(loaded_source_data: list) -> list:
    """
    Uses Vader Sentiment Analyzer to rank text as positive, negative, or
    nuetral using lexicon.
    """
    sia = SIA()
    sia_data = []
    for line in loaded_source_data:
        pol_score = sia.polarity_scores(line)
        pol_score["headline"] = line
        sia_data.append(pol_score)
    return sia_data


def label_data(sia_data: list, thresh_neg: float,  thresh_pos: float) -> pd.DataFrame:
    """
    -1 (Extremely Negative) to 1 (Extremely Positive)
    """
    labeled_df = pd.DataFrame.from_records(sia_data)
    labeled_df["label"] = 0
    labeled_df.loc[labeled_df["compound"] > thresh_pos, "label"] = 1
    labeled_df.loc[labeled_df["compound"] < thresh_neg, "label"] = -1
    return labeled_df


def main():
    loaded_source_data = load_data(DATASET)
    sia_data = rank_data(loaded_source_data)
    labeled_df = label_data(sia_data, -0.2, 0.2)

    # Change order of dataframe columns
    labeled_df = labeled_df[["headline", "neg", "neu", "pos", "compound", "label"]]

    # Write labeled data to CSV
    labeled_df.to_csv(LABELED_CSV_OUTFILE, encoding="utf-8", index=False)


if __name__ == "__main__":
    main()
