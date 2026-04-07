markdown# Job Application Agent

An AI-powered job search agent that automatically finds Scrum Master and Project Manager roles on LinkedIn Canada, tailors your resume for each job, and emails you the results with Word document attachments.

## What it does

- Searches LinkedIn for Scrum Master and Project Manager jobs in Canada posted in the last 7 days
- Prioritizes the most recently posted jobs — newest first
- Filters by location: Remote Canada or Hybrid Vancouver BC
- Tailors your resume and writes a cover letter for each job found
- Emails you a formatted report with .docx attachments for every job
- Runs automatically at 8AM and 1PM daily (when scheduler is enabled)
- Also available as a manual web interface at localhost

## Tech stack

- Python 3.12
- Flask — web framework
- Anthropic Claude API — AI model for job analysis and resume tailoring
- Serper API — Google search for LinkedIn job postings
- APScheduler — background job scheduler
- python-docx — generates Word document resumes and cover letters
- BeautifulSoup — web page parsing
- Gmail SMTP — email delivery

## Project structure
JobAgent/
├── app.py              # Main application — agent logic, routes, scheduler
├── resume.txt          # Your master resume — paste your full resume here
├── .env                # API keys and config — never commit this
├── .gitignore          # Excludes sensitive files from git
├── requirements.txt    # Python dependencies
└── templates/
└── index.html      # Web interface

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR-USERNAME/job-agent.git
cd job-agent
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
SERPER_API_KEY=your-serper-key
GMAIL_ADDRESS=your@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
NOTIFY_EMAIL=email-to-receive-results@gmail.com
SCHEDULER_ENABLED=false

**Getting your API keys:**
- Anthropic API key: [console.anthropic.com](https://console.anthropic.com) → API Keys
- Serper API key: [serper.dev](https://serper.dev) → free account gives 2,500 searches/month
- Gmail app password: Google Account → Security → 2-Step Verification → App Passwords

### 5. Add your resume

Paste your full resume into `resume.txt`. The more detail the better — the agent selects and reframes what is relevant for each job.

### 6. Run the app
```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Usage

### Web interface

**Find jobs for me tab** — fill in your role, location, experience, and salary preferences. Click "Find matching jobs and tailor resumes" to run the agent manually and see results in the browser.

**Tailor for a specific job tab** — paste a job description or LinkedIn URL. The agent analyzes it and produces a tailored resume and cover letter you can copy directly.

**Run now and email me results** — triggers the scheduled search immediately and sends results to your inbox.

### Scheduled runs

Set `SCHEDULER_ENABLED=true` in your `.env` to enable automatic runs at 8AM and 1PM daily. The agent emails you a report with:

- Job title, company, location, and posting date
- Match score and summary
- Direct link to the LinkedIn posting
- Two .docx attachments per job — tailored resume and cover letter

## Job search criteria

The scheduler searches for:

- **Roles:** Scrum Master, Project Manager only
- **Platform:** LinkedIn only
- **Location:** Remote anywhere in Canada, or Hybrid in Vancouver BC
- **Salary:** $75/hour minimum or $180,000 annual minimum (included even if not listed)
- **Age:** Posted within the last 7 days, sorted newest first

To change the search criteria edit the `criteria` string inside `run_daily_job_search()` in `app.py`.

## Cost management

This agent uses two Claude models to keep costs low:

- **Job search:** claude-haiku-4-5 — cheapest model, used for searching
- **Resume tailoring:** claude-sonnet-4-6 — mid-tier model, used for writing

Estimated cost per run is $0.10–0.20. Two runs per day = roughly $6–12/month.

Set a billing cap at [console.anthropic.com](https://console.anthropic.com) → Settings → Billing to prevent unexpected charges.

## Deployment

This app runs locally by default. To run it 24/7 deploy to Railway or Render:

1. Push to GitHub
2. Connect repo to [railway.app](https://railway.app)
3. Add your `.env` variables in Railway's environment settings
4. Set `SCHEDULER_ENABLED=true`
5. Deploy — Railway gives you a live URL and keeps the app running continuously

## Important notes

**LinkedIn automation:** This agent searches publicly visible LinkedIn job postings through Google search. It does not log into LinkedIn or scrape behind authentication. Automated login to LinkedIn violates their Terms of Service.

**API keys:** Never commit your `.env` file to GitHub. The `.gitignore` file in this repo excludes it automatically.

**Resume privacy:** Your `resume.txt` is excluded from git via `.gitignore`. Never commit personal information to a public repository.

## Built by

Akhilesh — PM turned AI engineer.
Built with Python, Flask, and the Anthropic Claude API.

Also create a requirements.txt file so anyone can install dependencies easily. Run this in your terminal:
pip freeze > requirements.txt
And create a .gitignore file with this content:
.venv/
__pycache__/
*.pyc
.env
resume.txt
uploads/
*.docx
.DS_Store
