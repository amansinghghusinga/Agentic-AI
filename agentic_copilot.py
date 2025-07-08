from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import time

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Import your copilots
from scam_detector import detect_scam
from data_cleaning_copilot import run_data_cleaning

def decide_next_step(user_text):
    prompt = f"""
    You are an agentic AI assistant helping with data tasks.

    The user said:
    "{user_text}"

    Decide the next action:
    - Should we clean a CSV?
    - Should we check for scams?
    - Should we run both?
    - Or should we ask for more detailsexit?

    Keep your answer short.
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    suggestion = completion.choices[0].message.content.strip()
    return suggestion

if __name__ == "__main__":
    print("🤖 Welcome to your Agentic AI Copilot!")

    while True:
        user_input = input("\nHow can I help you? (or type 'exit')\n> ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        suggestion = decide_next_step(user_input)
        print("\nCopilot suggests:", suggestion)

        if "clean" in suggestion.lower():
            csv_path = input("\nPlease provide the CSV path for cleaning:\n> ").strip()
            cleaned_csv = run_data_cleaning(csv_path)

            next_step = input(
                "\nDo you want to check the cleaned file for scam messages? (y/n): "
            ).strip().lower()

            if next_step == "y":
                df_cleaned = pd.read_csv(cleaned_csv)

                if "message_text" not in df_cleaned.columns:
                    print("⚠️ ERROR: No 'message_text' column found.")
                    continue

                labels = []
                scam_types = []
                explanations = []

                for idx, row in df_cleaned.iterrows():
                    message = row["message_text"]
                    print(f"Processing message {idx+1}/{len(df_cleaned)}...")
                    result_text = detect_scam(message)

                    label = "SCAM" if "SCAM" in result_text else "LEGITIMATE"
                    scam_type = ""
                    explanation = result_text

                    labels.append(label)
                    scam_types.append(scam_type)
                    explanations.append(explanation)

                    time.sleep(0.5)

                df_cleaned["label"] = labels
                df_cleaned["scam_type"] = scam_types
                df_cleaned["explanation"] = explanations

                output_path = "bulk_results_from_cleaned.csv"
                df_cleaned.to_csv(output_path, index=False)
                print(f"\n✅ Scam detection complete. Results saved to {output_path}")

        elif "scam" in suggestion.lower():
            mode = input("\nChoose scam detection mode:\n[1] Single message\n[2] Bulk CSV\n> ").strip()

            if mode == "1":
                msg = input("Enter the message:\n> ")
                result = detect_scam(msg)
                print(result)

            elif mode == "2":
                csv_path = input("CSV path:\n> ").strip()
                df = pd.read_csv(csv_path)

                if "message_text" not in df.columns:
                    print("⚠️ ERROR: No 'message_text' column found.")
                    continue

                labels = []
                scam_types = []
                explanations = []

                for idx, row in df.iterrows():
                    message = row["message_text"]
                    print(f"Processing message {idx+1}/{len(df)}...")
                    result_text = detect_scam(message)

                    label = "SCAM" if "SCAM" in result_text else "LEGITIMATE"
                    scam_type = ""
                    explanation = result_text

                    labels.append(label)
                    scam_types.append(scam_type)
                    explanations.append(explanation)

                    time.sleep(0.5)

                df["label"] = labels
                df["scam_type"] = scam_types
                df["explanation"] = explanations

                output_path = "bulk_results.csv"
                df.to_csv(output_path, index=False)
                print(f"\n✅ Bulk scam detection complete. Results saved to {output_path}")

        else:
            print("\nCopilot needs more details. Please try rephrasing your request.")
