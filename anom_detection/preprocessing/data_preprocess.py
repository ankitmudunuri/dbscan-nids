import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_features(input_csv="data/testdata/features.csv", output_csv="data/testdata/features_preprocessed.csv"):
    df = pd.read_csv(input_csv)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df)
    df_scaled = pd.DataFrame(scaled_features, columns=df.columns)
    df_scaled.to_csv(output_csv, index=False)
    print(f"Preprocessed features saved to {output_csv}")
    return df_scaled

if __name__ == "__main__":
    preprocess_features()
