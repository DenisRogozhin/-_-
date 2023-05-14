import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import pickle
from typing import Any


class Classifier:
    def __init__(
            self,
            new_init: bool = False,
            train_file_name: str = "data/train.csv",
            test_file_name: str = "data/test.csv",
            text_column: str = "content",
            ans_column: str = "grade3",
    ):
        self.train_file_name = train_file_name
        self.test_file_name = test_file_name
        self.vectorizer = TfidfVectorizer() if new_init else pickle.load(open('./data/vectorizer.pickle', 'rb'))
        self.label_encoder = LabelEncoder() if new_init else pickle.load(open('./data/label_encoder.pickle', 'rb'))
        self.model = LogisticRegression(
            multi_class='multinomial',
            solver='lbfgs'
        ) if new_init else pickle.load(open('./data/model.pickle', 'rb'))
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

    def predict(self, content: Any, inverse_transform: bool = False) -> Any:
        x = self.vectorizer.transform(content)
        result = self.model.predict(x)
        if inverse_transform:
            return self.label_encoder.inverse_transform(result)
        return result


if __name__ == '__main__':
    cls = Classifier(True)
    cls.train()
    cls.save()
