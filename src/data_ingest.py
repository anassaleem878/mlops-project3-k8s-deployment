from sklearn.datasets import load_iris
import pandas as pd
import os

def ingest_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['target'] = iris.target
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/iris.csv', index=False)
    print(f"[DATA INGEST] Complete. Shape: {df.shape}")

if __name__ == "__main__":
    ingest_data()
