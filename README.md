# AI Daily Digest

An automated pipeline that collects the latest AI news from across the US every morning, filters out noise and duplicates, and delivers a clean HTML digest straight to your inbox. It runs entirely on GitHub Actions, so you don't need a server or an always-on laptop.

**Want your own copy?** Jump to [Get your own daily digest](#get-your-own-daily-digest). It takes about 10 minutes, costs nothing, and needs no coding.

![AI Daily Digest architecture](assets/ai_daily_digest_architecture.gif)

## How it works

1. **Trigger**: a cron schedule in GitHub Actions starts a fresh cloud runner every morning.
2. **Collect**: `fetch_news.py` pulls articles from TechCrunch, The Verge, MIT Technology Review, VentureBeat, and Google News (US edition).
3. **Filter**: it keeps only stories from the last 24 hours, caps each feed at 8 articles so no single source dominates, extracts the real publisher from Google News titles, skips blocked low-quality publishers, and removes duplicate headlines.
4. **Format**: `send_email.py` builds a readable HTML email with clickable headlines and the publisher under each one.
5. **Deliver**: the digest is sent through Gmail SMTP using credentials stored securely in GitHub secrets.

## Tech stack

- **Python 3.12**
- **feedparser** for parsing RSS feeds
- **smtplib / email** (standard library) for building and sending the email
- **python-dotenv** for loading credentials during local runs
- **GitHub Actions** for scheduled cloud execution

## Project structure

```
AI-Daily-Digest/
├── .github/
│   └── workflows/
│       └── daily_digest.yml   # scheduled GitHub Actions workflow
├── assets/
│   └── ai_daily_digest_architecture.gif
├── fetch_news.py              # collects, filters, and deduplicates articles
├── send_email.py              # builds the HTML digest and sends it
├── requirements.txt
└── .gitignore                 # keeps .env and venv/ out of the repo
```

---

## Get your own daily digest

There are two ways to set this up. **Option 1 is recommended** for most people: everything runs in GitHub's cloud and you never install anything.

### What you need

- A **GitHub account** (free)
- A **Gmail account** to send the digest from
- Any **email address** to receive it (Gmail, Outlook, a school or work address, and so on)

### Step 1: Create a Gmail App Password

Gmail doesn't let scripts log in with your normal password, so you create a separate one just for this project.

1. Open your [Google Account security settings](https://myaccount.google.com/security) and turn on **2-Step Verification** if it isn't already on. App Passwords require it.
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
3. Enter a name like `AI Daily Digest` and click **Create**.
4. Copy the 16-character password and remove the spaces. Google only shows it once.

You can revoke this password anytime from the same page without affecting your main Gmail password.

### Option 1: Run it in the cloud with GitHub Actions (recommended)

**1. Fork this repository.** Click the **Fork** button at the top right of this page. This creates your own copy under your GitHub account.

**2. Enable Actions on your fork.** GitHub turns workflows off on forks by default. Open the **Actions** tab in your fork and click **"I understand my workflows, go ahead and enable them."**

**3. Add your secrets.** In your fork, go to **Settings → Secrets and variables → Actions → New repository secret** and add these three:

| Secret name | Value |
|---|---|
| `GMAIL_ADDRESS` | The Gmail address you're sending from |
| `GMAIL_APP_PASSWORD` | The 16-character App Password from Step 1 |
| `RECIPIENT_EMAIL` | The address where you want to receive the digest |

Secrets are encrypted. Nobody, including the original repo owner, can see them.

**4. Set your delivery time.** Open `.github/workflows/daily_digest.yml` in your fork, click the pencil icon to edit, and change the cron line. Times are in **UTC**, so convert from your time zone:

| You want it at | US Eastern (EST) | US Central (CST) | US Mountain (MST) | US Pacific (PST) |
|---|---|---|---|---|
| 7:00 AM | `0 12 * * *` | `0 13 * * *` | `0 14 * * *` | `0 15 * * *` |
| 8:00 AM | `0 13 * * *` | `0 14 * * *` | `0 15 * * *` | `0 16 * * *` |
| 10:00 AM | `0 15 * * *` | `0 16 * * *` | `0 17 * * *` | `0 18 * * *` |

During daylight saving time (mid-March to early November), subtract 1 from the hour to keep the same local time. For other time zones, [crontab.guru](https://crontab.guru) helps you build the line.

Click **Commit changes** when you're done.

**5. Test it.** Go to **Actions → AI Daily Digest → Run workflow**. Within a minute or two you should see a green check and the digest in your inbox. From now on it arrives automatically every day.

### Option 2: Run it on your own computer

Use this if you want to change the code or test locally before pushing.

**1. Clone the repository and install dependencies**

```bash
git clone https://github.com/SIDDHARTH107/AI-Daily-Digest.git
cd AI-Daily-Digest
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

On Windows, if PowerShell blocks the activation script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

**2. Create a `.env` file** in the project root:

```
GMAIL_ADDRESS=your-gmail@gmail.com
GMAIL_APP_PASSWORD=your16charapppassword
RECIPIENT_EMAIL=where-to-send@example.com
```

Never commit this file. It is already listed in `.gitignore`.

**3. Run it**

```bash
python fetch_news.py    # preview today's articles in the terminal
python send_email.py    # fetch and send the digest
```

To run it automatically from your own machine, schedule `python send_email.py` with **Task Scheduler** (Windows) or **cron** (macOS/Linux). It only runs while your computer is on, which is why Option 1 is recommended.

---

## Customization

All settings live at the top of `fetch_news.py`:

| Setting | Default | What it controls |
|---|---|---|
| `FEEDS` | 5 sources | RSS feeds to pull from; add or remove any feed URL |
| `HOURS_BACK` | `24` | How far back to look; set to `168` for a weekly digest |
| `MAX_PER_FEED` | `8` | Maximum articles taken from each feed |
| `BLOCKED_PUBLISHERS` | `tradingview`, `debuglies.com` | Publishers to skip (partial, case-insensitive match) |

For a **weekly digest**, set `HOURS_BACK = 168` and change the cron line to run once a week. For example, `0 13 * * 1` runs every Monday at 8 AM Eastern (EST).

To follow a **different topic**, change the Google News feed URL. For example, replace `artificial+intelligence` with `machine+learning` or `generative+ai`.

## Troubleshooting

| Problem | Fix |
|---|---|
| The email isn't in my inbox | Check your **Junk / Spam** folder and mark it "Not spam" so future digests go to your inbox. |
| `SMTPAuthenticationError` | Make sure 2-Step Verification is on, you're using the App Password (not your normal password), and it has no spaces. |
| The workflow never runs on schedule | Confirm Actions are enabled on your fork, and check the cron line is valid. Scheduled runs can start 5–30 minutes late when GitHub is busy. |
| It stopped running after a while | GitHub pauses scheduled workflows in repos with no activity for 60 days. Re-enable it from the Actions tab. |
| `No articles found, skipping email.` | No feed had stories in the time window. Try increasing `HOURS_BACK`. |
## Author

Built by [Siddharth](https://github.com/SIDDHARTH107). Feel free to fork it, open an issue, or suggest new features.
