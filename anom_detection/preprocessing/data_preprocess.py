import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_packet_features(packet_features_list, output_csv=None):
    try:
        if not packet_features_list:
            print("No packet features to process.")
            return pd.DataFrame()
        
        print(f"Type: {type(packet_features_list)}, Data: {packet_features_list}")

        df = pd.DataFrame([packet_features_list])

        print("Created dataframe:", df)

        scaler = StandardScaler()
        print("Made scaler")
        scaled_values = scaler.fit_transform(df)
        print("Transformed data:",scaled_values)
        df_scaled = pd.DataFrame(scaled_values, columns=df.columns)
        print("Scaled data")


        if output_csv:
            df_scaled.to_csv(output_csv, index=False)
            print(f"Preprocessed features saved to {output_csv}")

        return df_scaled
    except Exception as e:
        print("Error:", e)
        return pd.DataFrame()


if __name__ == "__main__":
    preprocess_packet_features()
