import pandas as pd
from typing import List, Dict, Any


def clean_intent(df: pd.DataFrame, intent: str, limit: int) -> pd.DataFrame:
    counts = df[intent].value_counts()
    return df[~df[intent].isin(counts[counts < limit].index)]


def imbalances(train_df: pd.DataFrame, intent: str, small_classes: List[str], duplicate_counts: List[int]):
    for small_class, duplicate_count in zip(small_classes, duplicate_counts):
        for _ in range(duplicate_count):
            train_df = pd.concat([train_df, train_df[train_df[intent] == small_class]])
    return train_df.sample(frac=1)


def pretty_print(answer_dict: Dict[str, Any], print_type: str) -> str:
    if print_type == "cut":
        message = "Сокращённый текст: \n"
        for cur_msg in answer_dict['main_words']:
            message += ' '.join(cur_msg)
        message += '.'
    else:
        message = ""
    return message
