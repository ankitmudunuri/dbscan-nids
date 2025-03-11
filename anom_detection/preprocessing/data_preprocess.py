import pandas as pd
from sklearn.preprocessing import StandardScaler

def create_df(packet_features_list, output_csv=None):
    try:
        if not packet_features_list:
            print("No packet features to process.")
            return pd.DataFrame()

        df = pd.DataFrame([packet_features_list])



        if output_csv:
            df.to_csv(output_csv, index=False)
            print(f"Preprocessed features saved to {output_csv}")

        return df
    except Exception as e:
        print("Error:", e)
        return pd.DataFrame()
    
def scaling(df) -> pd.DataFrame:
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(df)       
    df_scaled = pd.DataFrame(scaled_values, columns=df.columns).astype(float)

    return df_scaled

# def preprocess_features(input_csv="data/testdata/features.csv", output_csv="data/testdata/features_preprocessed.csv"):
#     df = pd.read_csv(input_csv)
#     scaler = StandardScaler()
#     scaled_features = scaler.fit_transform(df)
#     df_scaled = pd.DataFrame(scaled_features, columns=df.columns)
#     df_scaled.to_csv(output_csv, index=False)
#     print(f"Preprocessed features saved to {output_csv}")
#     return df_scaled


if __name__ == "__main__":
    create_df()
