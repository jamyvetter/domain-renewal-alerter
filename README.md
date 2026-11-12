# Domain Renewal Alerter

<h4 align="center">Automated Domain Drop Alerter with GitHub Actions, RFC 3915, and Controlled AI</h4>
<h5 align="center"><a href="https://jamyvetter.net/posts/beating-icann-redemption-fees-domain-drop-alerter/">Read the Full Technical Article Here</a></h5>

<p align="center">
  <a href="https://github.com/jamyvetter/domain-renewal-alerter/issues">
    <img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat" alt="Contributions Welcome">
  </a>
  <a href="https://github.com/jamyvetter/domain-renewal-alerter/actions/workflows/domain-monitor.yml">
    <img src="https://img.shields.io/badge/workflow-automated-blue.svg?style=flat" alt="GitHub Actions">
  </a>
  <a href="https://jamyvetter.net/posts/beating-icann-redemption-fees-domain-drop-alerter/">
    <img src="https://img.shields.io/badge/%20-jamyvetter.net-2C3E50?style=flat&labelColor=7F6754&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAYNQTFRFAAAAAgkbAQ4oAg4qFg4xBQwmEggmAQwkAA8qARAsAg8rKg48qQxypwtulQtoAAwhABArABAsAQ8sAg8sEw4y1wyF/AyV8w2SAA8qWg1Q/gyW/AyVAA0lABAtBQ0pwwx8/gyV+A2TAA8rABAtDA8vXw1T0wyE/AyUAA4nARItBi9NCTteCTpdBypHCg4tdgxc+QyU+QyUAwoaABAsARQxDV6IFYa4E3elDluGC053DE94D16JFHimF4S1E1J9ShBL8AyQAA8oCDteEGiTBjRVABItAhEtDTRZUzmKvg9/+gyUDFB1C0VpVFlnWVxrDRs1AA8sGiU8aWt3Nz5RAw8rBA4qcw1b/AyUF4GuEyA5c3V+XWBtAREsBxUwb3B7Z2l1CxcxBA8rBg4q4g2KHanlAhk2HQ018QyRHbb1FH2uABEuwgx99g2RHbX3EnSjABIvCw4tuQ58+g6dHLP4Em6aARMvDQ8vrw557hCZJsr5DlNyABEtAQ8rAQ8sCA8tgxBp/BGoSgeKTgAAAIF0Uk5TAAF05ttaABvH/////7AOFOX//////88JpP//cDP7///yFsP/////jVD/////////+yUB1v///////////////6Vi//////////0w0v/9/P///v7+////qPf//f3//v38////5Mf//6M2+P/wIDrn///pLBjC//+8HAWK/v/++m8Ec4VCOAAAALxJREFUeJxjZAABRjD4BWaCCHaIAOMnqAA/I+MPTrDIS4iAxE8Ghh9c34HiT8ECMoxfQPQPEaCS+yABJSB+x8AoxMj4hfcmUEDjN8M7CZABd1SBxHlGI0YUcIDREUSdAbvABCzkzXiUwYaR8ZA9TE3EaYZ3HlD2F14gkcK4D2gH0CEMjF4MvKyMjBmMjDvhArdsGRkZchkZF0EFZBgZ+4COKmZknAO04ztjDiNjB9gvlYyM0xiyQaY2MDAAAGiFKeiOfi4zAAAAAElFTkSuQmCC" alt="Jamy's badge">
  </a>
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#-notes">Notes</a>
</p>

---

# Overview

**Domain Renewal Alerter** is a lightweight, zero-maintenance, automated pipeline running on **GitHub Actions**. It continuously inspects the WHOIS lifecycle status of an expiring or expired domain name to alert you the exact moment it drops back into the public pool.

This project was born out of a real-world scenario: an expired `.net` domain moved into the ICANN **Redemption Grace Period**, where the registrar demanded an exorbitant **50€ to 60€ restoration penalty** instead of the standard **~10€ registration fee**. Rather than paying the redemption ransom or manually refreshing WHOIS queries like a bot, this automated watcher monitors RFC 3915 lifecycle transitions and notifies you immediately on **Telegram**.

---

# Features

- **Automated Scheduling**: Scheduled twice daily via GitHub Actions `cron` (11:00 UTC and 13:00 UTC), strategically bracketing target domain registration/expiration hours.
- **Port 43 WHOIS Ingestion**: Queries authoritative TLD registry servers using `python-whois`.
- **Controlled LLM-as-a-Judge**: Leverages Google Gemini (`gemini-3.5-flash` via `google-genai`) to parse messy, multi-registrar WHOIS outputs into structured JSON.
- **Deterministic Alert Guards**: Hardened Python logic overrides LLM outputs to prevent false alarms, ensuring 🟢 alerts only fire when availability is strictly confirmed.
- **Push Alerts via Telegram**: Instant push notifications directly to your phone with prioritized emojis:
  - 🔴 **Daily Status**: Domain is still in `RedemptionPeriod` or active hold.
  - 🟠 **Imminent Drop**: Domain transitioned to `PendingDelete` (5-day final countdown).
  - 🟢 **Action Required**: Domain is released! Go register it immediately at regular cost.

---

# Architecture

```text
┌─────────────────────────┐
│  GitHub Actions (Cron)  │  (Scheduled 11:00 & 13:00 UTC)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Port 43 WHOIS Query   │  (Raw unstandardized text dump)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Gemini AI (Judge)     │  (Extracts status & drop estimates to JSON)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Python Guard & Filter   │  (Strict deterministic keyword validation)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Telegram Bot Webhook   │  (Instant mobile push notification)
└─────────────────────────┘
```

---

# Domain Lifecycle (RFC 3915)

```mermaid
flowchart TD
    P0["0. Available in Public Pool<br>Status: Available / Free (~10€)"]
    P1["1. Registered & Active Ownership<br>Status: ok / active (1–10 yrs)"]
    P2["2. Reminder Window (T - 60d to T - 7d)<br>Registrar renewal emails (ICANN ERRP)"]
    P3["3. Expiration Timestamp (T = 0)<br>Registry bills registrar in credit"]
    P4["4. Auto-Renew Grace Period (0–45 days)<br>Status: autoRenewPeriod / clientHold"]
    P5["5. Redemption Grace (~30d, RFC 3915)<br>Status: redemptionPeriod (DNS dead, 60€)<br><b>🔴 WHERE I WAS TRAPPED</b>"]
    P6["6. Pending Delete (5 days, RFC 3915)<br>Status: pendingDelete (Death row, locked)<br><b>🟠 TARGET ALERT 1: Warning</b>"]
    P7["7. Dropped / Purged Back to Pool<br>Status: Available (~10€ normal registration)<br><b>🟢 TARGET ALERT 2: Buy Immediately!</b>"]

    P0 -->|"Register domain (~10€)"| P1
    P1 -->|"Approaching expiry"| P2
    P2 -->|"Missed reminder emails"| P3
    P3 -->|"Enters registrar grace"| P4
    P4 -->|"Registrar cancels lease"| P5
    P5 -->|"Restoration window expires"| P6
    P6 -->|"Registry purges record"| P7
    P7 -.->|"Re-purchase at ~10€"| P1

    style P2 fill:#fff3bf,stroke:#fab005,stroke-width:2px,color:#000
    style P5 fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style P6 fill:#ffa94d,stroke:#d9480f,stroke-width:3px,color:#fff
    style P7 fill:#51cf66,stroke:#2b8a3e,stroke-width:3px,color:#fff
```

```text
  [ 0. Available Pool ] ──(Buy at ~10€)──> [ 1. Active Ownership (ok) ]
                                                        │
                                                        ▼
                                           [ 2. Pre-Expiry Reminders (T-60d) ]
                                           (Missed emails in cluttered inbox!)
                                                        │
                                                        ▼
                                           [ 3. Expiration Timestamp (T=0) ]
                                                        │
                                                        ▼
                                           [ 4. Auto-Renew Grace (0–45d) ]
                                           (Standard ~10€ renewal still valid)
                                                        │ (Registrar cancels)
                                                        ▼
  🔴 WHERE I WAS TRAPPED (60€ Ransom)      [ 5. Redemption Grace (~30d) ]
                                           (DNS dead, heavy 50€–60€ penalty fee)
                                                        │
                                                        ▼
  🟠 TARGET ALERT 1 (Drop Imminent)        [ 6. Pending Delete (5 days) ]
                                           (Irreversible death row, no restoration)
                                                        │
                                                        ▼
  🟢 TARGET ALERT 2 (Buy Immediately!)     [ 7. Dropped / Available (~10€) ]
                                                        │
                                                        └──────(Re-purchase)──────┘
```

---

# Quick Start

### 1. Fork or Clone this Repository

```bash
git clone https://github.com/jamyvetter/domain-renewal-alerter.git
cd domain-renewal-alerter
```

### 2. Configure GitHub Secrets & Variables

In your GitHub repository, navigate to **Settings > Secrets and variables > Actions**:

#### Repository Secrets (Required):
- `GEMINI_API_KEY`: Your Google Gemini API Key (get one free at [Google AI Studio](https://aistudio.google.com/app/apikey)).
- `TELEGRAM_BOT_TOKEN`: The API token of your Telegram bot (created via [@BotFather](https://t.me/BotFather)).
- `TELEGRAM_CHAT_ID`: Your personal or group chat ID (obtained via [@userinfobot](https://t.me/userinfobot)).

> 💡 **Important Telegram Step**: Before running the alert, open your bot in Telegram and send it `/start`. Telegram bots are not permitted to message users without prior user interaction.

#### Repository Variables (Optional):
- `DOMAIN`: The domain name you want to track (e.g. `example.com`). Defaults to `jamyvetter.net` if omitted.

### 3. Run Manually or Wait for Cron

1. Go to the **Actions** tab in your GitHub repository.
   *(Note: If you forked this repository, click "I understand my workflows, go ahead and enable them" first).*
2. Select **Domain Renewal Monitor** in the left sidebar.
3. Click **Run workflow** to test execution immediately.

---

# Configuration

### Local Testing

To test the monitoring script on your local machine:

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Export environment variables
export GEMINI_API_KEY="your-gemini-api-key"
export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
export DOMAIN="jamyvetter.net"

# 4. Execute the script
python monitor.py
```

---

# 📋 Notes

- **RFC 3915 Compliance**: Accurately tracks EPP status values including `redemptionPeriod`, `pendingDelete`, and `ok`.
- **Zero Running Costs**: Runs entirely within GitHub Actions free public runner tier and Google Gemini free/developer tier limits.
- **Safety First**: The pipeline does not execute automated purchases—it alerts human buyers immediately, avoiding unpredictable registrar billing APIs.
- **Controlled Surface Area**: By using Python for network and alerting while restricting LLM execution to semantic classification, the system avoids prompt injection and hallucination loops.

---

If you find this useful or have ideas for multi-domain support, feel free to open an issue or submit a pull request!
