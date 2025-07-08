from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd

# -------------------------------
# Load your API key
# -------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def run_data_cleaning(csv_path: str) -> str:
    """
    Loads the CSV, generates cleaning suggestions,
    and executes cleaning operations if desired.
    """

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return csv_path

    print("\nColumns in CSV:")
    print(df.columns.tolist())
    print("\nSample data:")
    print(df.head())

    instructions = input("\nEnter your data cleaning instructions:\n> ")

    # Generate cleaning suggestions from the LLM
    prompt = f"""
    You are an expert data cleaning assistant.

    The user has uploaded a CSV file with these columns:
    {df.columns.tolist()}

    Sample rows:
    {df.head(5).to_string(index=False)}

    The user wants:
    \"{instructions}\"

    Summarize additional cleaning steps you recommend. Do NOT produce Pandas code.
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful data cleaning assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    suggestions = completion.choices[0].message.content
    print("\n✅ Suggestions from AI:\n", suggestions)

    # Ask which columns are date fields
    date_cols_input = input(
        "\nEnter names of any date columns, separated by commas (or leave blank if none):\n> "
    ).strip()

    if date_cols_input:
        date_cols = [col.strip() for col in date_cols_input.split(",")]
    else:
        date_cols = []

    execute = input("\nDo you want to execute automatic cleaning? (y/n): ").strip().lower()

    if execute == "y":
        for col in date_cols:
            print(f"Processing date column: {col}")

            df[col] = df[col].astype(str).str.strip()
            df.loc[df[col].str.lower() == 'nan', col] = None

            parsed_dates = pd.to_datetime(
                df[col],
                errors='coerce'
            )

            mask = parsed_dates.isna() & df[col].notna()
            if mask.any():
                parsed_dates.loc[mask] = pd.to_datetime(
                    df.loc[mask, col],
                    dayfirst=True,
                    errors='coerce'
                )

            parsed_dates = parsed_dates.fillna(pd.Timestamp("1900-01-01"))
            df[col] = parsed_dates.dt.strftime('%Y-%m-%d')

        drop_nulls = input("\nDrop rows where revenue is null? (y/n): ").strip().lower()
        if drop_nulls == "y":
            if "revenue" in df.columns:
                df = df.dropna(subset=["revenue"])

        cleaned_path = "cleaned_data_v2.csv"
        df.to_csv(cleaned_path, index=False)
        print(f"\n✅ Cleaning complete. File saved to {cleaned_path}.")
        return cleaned_path
    else:
        print("\nSkipped cleaning.")
        return csv_path
