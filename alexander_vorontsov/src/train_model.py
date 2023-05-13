import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import pickle


class Classifier:
    def __init__(
            self,
            train_file_name: str,
            test_file_name: str,
            text_column: str = "content",
            ans_column: str = "grade3",
    ):
        self.train_file_name = train_file_name
        self.test_file_name = test_file_name
        self.vectorizer = TfidfVectorizer()
        self.label_encoder = LabelEncoder()
        self.model = LogisticRegression(multi_class='multinomial', solver='lbfgs')
        self.text_column = text_column
        self.ans_column = ans_column

    def train(self):
        df_train = pd.read_csv(self.train_file_name)

        self.vectorizer.fit(df_train[self.text_column])
        x = self.vectorizer.transform(df_train[self.text_column])

        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(df_train[self.ans_column])
        y = self.label_encoder.transform(df_train[self.ans_column])

        self.model.fit(x, y)

    def save(self):
        pickle.dump(self.label_encoder, open("data/label_encoder.pickle", "wb"))
        pickle.dump(self.vectorizer, open("data/vectorizer.pickle", "wb"))
        pickle.dump(self.model, open("data/model.pickle", "wb"))


if __name__ == '__main__':
    cls = Classifier("data/train.csv", "data/test.csv")
    cls.train()
    cls.save()
