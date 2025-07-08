from openai import OpenAI
from dotenv import load_dotenv
import os

# -------------------------------
# Load your API key
# -------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def detect_scam(message_text: str) -> str:
    prompt = f"""
    You are an expert fraud detection AI.

    Below is a list of common scam types and how they often appear:

    1. Prize Scams: Messages claiming you've won prizes or gift cards, especially for contests you never entered.
    2. IRS or Government Scams: Messages claiming to be from tax agencies or government bodies demanding action.
    3. Refund Scams: Messages claiming you’re owed money and requesting bank details.
    4. Bank Verification Scams: Messages pretending to be your bank, asking to verify your account or warning it's locked.
    5. Package Delivery Scams: Messages about package deliveries requesting money or personal information.
    6. Boss or Manager Scams: Scammers pretending to be your boss requesting urgent help or gift cards.
    7. Subscription Renewal Scams: Messages about renewing services you might not recognize.
    8. Low-Interest Credit Card Scams: Messages offering unrealistically low credit rates.
    9. Apple ID/iCloud Scams: Messages attempting to verify Apple IDs or other tech accounts.
    10. Crypto Scams: Messages offering free Bitcoin or crypto opportunities, or blackmail scams demanding crypto payments.
    11. Family Emergency Scams: Messages claiming family members are in trouble and need money urgently.
    12. Account Reactivation Scams: Messages warning accounts are compromised and asking for credentials.
    13. Fake Billing Statement Scams: Messages about new billing statements or “thank you for your payment” messages that are fake.
    14. Spoofed Messages: Messages appearing to come from your own phone number (spoofing).
    15. Two-Factor Authentication Scams: Requests for your 2FA code or suspicious links related to security codes.

    TASK:
    - Classify the following message as either:
        - LEGITIMATE
        - SCAM

    If it is a scam, specify:
    - The scam type (from the list above)
    - A brief explanation why you believe it is a scam.

    MESSAGE:
    \"{message_text}\"
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return completion.choices[0].message.content
