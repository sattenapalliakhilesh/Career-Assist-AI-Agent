# Career Assist AI Agent

An AI-powered job search agent that automatically finds Scrum Master and Project Manager roles on LinkedIn Canada, tailors your resume for each job, and emails you the results as professionally formatted Word documents.

## What it does

- Searches LinkedIn for Scrum Master and Project Manager jobs in Canada posted in the last 7 days
- Filters to **active postings only** — skips closed, expired, or filled roles
- Filters by **salary minimum** — $75/hour or $180,000/year (jobs with no salary listed are still included)
- Prioritizes the most recently posted jobs — newest first
- Filters by location — Remote Canada or Hybrid Vancouver BC
- Tailors your resume and writes a cover letter for each matching job
- Generates professionally formatted `.docx` files matching a clean resume template
- Emails you a full report with Word document attachments for every job
- Runs automatically at 8AM and 1PM daily (when scheduler is enabled)
- Also available as a manual web interface

## Tech stack

| Package | Purpose |
|---|---|
| Python 3.12 | Runtime |
| Flask | Web framework |
| Anthropic Claude API | AI for job search, resume tailoring, cover letters |
| Serper API | Google search to find LinkedIn job postings |
| APScheduler | Background job scheduler |
| python-docx | Generates formatted Word document resumes and cover letters |
| BeautifulSoup | Web page parsing |
| Gmail SMTP | Email delivery |

## Project structure

```
career-assist-ai-agent/
├── app.py              # Main application — agent logic, Flask routes, scheduler
├── resume.txt          # Your master resume — paste your full resume here
├── templates/
│   └── index.html      # Web UI
├── .env                # API keys and config — never commit this
└── .gitignore
```

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/sattenapalliakhilesh/career-assist-ai-agent.git
cd career-assist-ai-agent
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install flask anthropic python-dotenv requests beautifulsoup4 apscheduler python-docx
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
SERPER_API_KEY=your-serper-key
GMAIL_ADDRESS=your@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
NOTIFY_EMAIL=email-to-receive-results@gmail.com
SCHEDULER_ENABLED=false
```

**Getting your API keys:**
- **Anthropic API key** — [console.anthropic.com](https://console.anthropic.com) → API Keys
- **Serper API key** — [serper.dev](https://serper.dev) — free account gives 2,500 searches/month
- **Gmail app password** — Google Account → Security → 2-Step Verification → App Passwords

### 5. Add your resume

Paste your full resume as plain text into `resume.txt`. The more detail the better — the agent selects and reframes what's relevant for each job.

### 6. Run the app

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Usage

### Web interface

**Find jobs for me tab** — fill in your preferences and click "Find matching jobs & tailor resumes" to run the agent and see results in the browser.

**Tailor for a specific job tab** — paste a job description or LinkedIn URL. The agent analyzes it and produces a tailored resume and cover letter you can copy directly.

**Run now and email me results** — triggers the scheduled search immediately and sends results to your inbox.

### Scheduled runs

Set `SCHEDULER_ENABLED=true` in `.env` to enable automatic runs at 8AM and 1PM daily. Each email includes:

- Job title, company, location, and posting date
- Match score and summary
- Direct link to the LinkedIn posting
- Two `.docx` attachments per job — tailored resume and cover letter

## Job search filters

| Filter | Rule |
|---|---|
| Platform | LinkedIn only |
| Roles | Scrum Master, Project Manager |
| Location | Remote Canada or Hybrid Vancouver BC |
| Posting age | Last 7 days, sorted newest first |
| Status | Active postings only (no closed/expired/filled) |
| Salary | Min $75/hr or $180,000/year — included if not listed |

To change search criteria edit the `criteria` string inside `run_daily_job_search()` in `app.py`.

## Resume document format

Generated `.docx` files follow a clean professional template:

- Large bold name, bold title/credentials, contact info in the header
- Thin horizontal rules between sections
- ALL CAPS bold section headers
- Job entries with bold title left and italic date right-aligned
- Justified body paragraphs with inline bold support
- Calibri 11pt throughout, standard margins

## Cost

The agent uses two Claude models to keep costs low:

| Task | Model | Why |
|---|---|---|
| Job search | claude-haiku-4-5 | Fast and cheap for structured searches |
| Resume tailoring | claude-sonnet-4-6 | Higher quality for writing |

Estimated cost: ~$0.10–0.20 per run. Two runs/day ≈ $6–12/month.

Set a billing cap at [console.anthropic.com](https://console.anthropic.com) → Settings → Billing.

## Deployment

The app runs locally by default. To run 24/7, deploy to Railway or Render:

1. Push to GitHub
2. Connect your repo at [railway.app](https://railway.app)
3. Add all `.env` variables in Railway's environment settings
4. Set `SCHEDULER_ENABLED=true`
5. Deploy — Railway keeps the app running and the scheduler firing daily

## Notes

**LinkedIn:** This agent searches publicly visible LinkedIn job postings via Google. It does not log into LinkedIn or scrape behind authentication.

**API keys:** Never commit your `.env` file. It is excluded automatically by `.gitignore`.

**Resume privacy:** `resume.txt` is excluded from git via `.gitignore`. Never commit personal information to a public repo.

---

Built by Akhilesh Sattenapalli — PM turned AI engineer.
