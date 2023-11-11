import pandas as pd
from sklearn.linear_model import LinearRegression


class LinearModel:
    def __init__(self):
        self.LR = LinearRegression()

    def fit_predict(self, X: pd.DataFrame, Y: pd.Series, X_prediction) -> float:
        self.LR.fit(X, Y)
        return round(abs(self.LR.predict(X_prediction)[0]), 2)