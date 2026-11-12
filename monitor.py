import os
import sys
import json
import whois
import requests
from google import genai
from google.genai import types

DOMAIN = os.environ.get("DOMAIN", "jamyvetter.net")


def main():
    # Load secrets
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY environment variable is missing.")
        sys.exit(1)

    print(f"Checking WHOIS for {DOMAIN}...")
    try:
        domain_info = whois.whois(DOMAIN)
        raw_whois_text = str(domain_info)
        print(f"Successfully retrieved WHOIS data for {DOMAIN}.")
    except Exception as e:
        print(f"Error fetching WHOIS data: {e}")
        sys.exit(1)

    # Configure Gemini client via official google-genai SDK
    client = genai.Client(api_key=gemini_api_key)

    prompt = f"""
    You are an expert domain name and DNS analyst. I will provide you with raw WHOIS data for {DOMAIN}.

    The domain might have been overlooked and could be in a "Redemption Period", "Pending Delete", or it might be "Available".
    Your task is to analyze the text and determine the current status of the domain according to RFC 3915 / EPP lifecycle standards.

    You MUST output valid JSON ONLY, with the following keys:
    - "status": A short string describing the current status (e.g. "RedemptionPeriod", "PendingDelete", "Available", "Registered")
    - "drop_date_estimate": Your best estimate of when the domain will drop and become available to the public. If unknown or not applicable, return null.
    - "requires_action": Boolean true if the domain is close to dropping (e.g. PendingDelete) or currently available, meaning I need to buy it NOW. False otherwise.
    - "reasoning": A short string explaining your decision.

    Raw WHOIS Data:
    {raw_whois_text}
    """

    print("Asking Gemini to analyze WHOIS data (LLM-as-a-Judge)...")
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        result_text = response.text
        print(f"Gemini analysis result: {result_text}")

        analysis = json.loads(result_text)
    except Exception as e:
        print(f"Error calling Gemini or parsing response: {e}")
        sys.exit(1)

    # Deterministic alert triage guard:
    # We do not blindly trust LLM boolean output for critical alert triggering.
    # We enforce strict deterministic keyword evaluation on the classified status.
    status_lower = str(analysis.get('status', '')).lower()

    if "available" in status_lower or "ok" in status_lower:
        emoji = "🟢"
        header = f"{emoji} **GO QUICKLY BUY IT!** {emoji}"
    elif "pendingdelete" in status_lower:
        emoji = "🟠"
        header = f"{emoji} **Domain is Pending Delete (Almost available)** {emoji}"
    else:
        emoji = "🔴"
        header = f"{emoji} **Daily Domain Status** {emoji}"

    print("Preparing Telegram notification...")
    if not telegram_bot_token or not telegram_chat_id:
        print("WARNING: Telegram credentials missing. Cannot dispatch notification.")
        sys.exit(1)

    message = (
        f"{header}\n"
        f"Domain: {DOMAIN}\n"
        f"Status: {analysis.get('status')}\n"
        f"Drop Estimate: {analysis.get('drop_date_estimate')}\n"
        f"Reasoning: {analysis.get('reasoning')}"
    )

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": telegram_chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("Telegram notification dispatched successfully.")
    except Exception as e:
        print(f"Failed to dispatch Telegram notification: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
