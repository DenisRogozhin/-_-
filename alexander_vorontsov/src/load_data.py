from datasets import load_dataset
import pandas as pd


class Downloader:
    def __init__(self, dataset_name: str = 'blinoff/kinopoisk', save: bool = True):
        self.dataset_name = dataset_name
        self.save = save

    def run(self):
        train_set = load_dataset(self.dataset_name, split='train')
        test_set = load_dataset(self.dataset_name, split='validation')
        train_df = pd.DataFrame(train_set)
        test_df = pd.DataFrame(test_set)
        if self.save:
            train_df.to_csv("data/train.csv")
            test_df.to_csv("data/test.csv")


if __name__ == '__main__':
    downloader = Downloader()
    downloader.run()
