import pandas as pd
from typing import List


def clean_intent(df: pd.DataFrame, intent: str, limit: int) -> pd.DataFrame:
    counts = df[intent].value_counts()
    return df[~df[intent].isin(counts[counts < limit].index)]


def imbalances(train_df, intent: str, small_classes: List[str], duplicate_counts: List[int]):
    for small_class, duplicate_count in zip(small_classes, duplicate_counts):
        for _ in range(duplicate_count):
            train_df = pd.concat([train_df, train_df[train_df[intent] == small_class]])
    return train_df.sample(frac=1)
