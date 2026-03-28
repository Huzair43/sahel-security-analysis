from src.acled_pipeline import ACLEDPipeline

def main():
    print("Sahel Conflict Monitor: Pipeline ACLED\n")
    pipeline = ACLEDPipeline()

    df_raw   = pipeline.fetch_all_countries()
    df_clean = pipeline.clean_data(df_raw)
    pipeline.save_data(df_clean)
    pipeline.summary(df_clean)

    print("\n Pipeline completed successfully !")
    return df_clean

if __name__ == "__main__":
    df = main()