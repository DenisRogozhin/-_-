import pickle
import pandas as pd
from sklearn.metrics import accuracy_score


def test_cls():
    vectorizer = pickle.load(open('data/vectorizer.pickle', 'rb'))
    model = pickle.load(open('data/model.pickle', 'rb'))
    label_encoder = pickle.load(open('data/label_encoder.pickle', 'rb'))

    df_test = pd.read_csv("data/test.csv")
    x = vectorizer.transform(df_test["content"])

    y_true = label_encoder.transform(df_test["grade3"])
    y_pred = model.predict(x)
    assert accuracy_score(y_true, y_pred) > 0.8
