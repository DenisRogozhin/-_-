import pandas as pd
from utils import clean_intent, imbalances


class Preprocessing:
    def __init__(self, train_df_name: str = "data/train.csv", save: bool = True):
        self.train_df_name = train_df_name
        self.save = save

    def run(self):
        train_df = pd.read_csv(self.train_df_name)
        train_df = clean_intent(train_df, 'author', 3)
        train_df = clean_intent(train_df, 'movie_name', 6)
        train_df = train_df[['content', 'grade3']]
        train_df = imbalances(train_df, 'grade3', ['Bad', 'Neutral'], [2, 2])
        if self.save:
            train_df.to_csv(self.train_df_name)


if __name__ == '__main__':
    preprocessor = Preprocessing()
    preprocessor.run()
