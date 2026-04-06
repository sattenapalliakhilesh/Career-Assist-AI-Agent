import os
import json
import smtplib
import threading
import requests
from flask import Flask, render_template, request, jsonify
from anthropic import Anthropic
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = Flask(__name__)
client = Anthropic()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def load_resume():
    with open("resume.txt", "r") as f:
        return f.read()

def search_web(query):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": 5}
    response = requests.post(url, headers=headers, json=payload)
    results = response.json()
    output = []
    for r in results.get("organic", [])[:5]:
        output.append(f"Title: {r.get('title')}\nSnippet: {r.get('snippet')}\nURL: {r.get('link')}")
    return "\n\n".join(output)

def fetch_url(url):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text[:5000]
    except Exception as e:
        return f"Could not fetch URL: {str(e)}"

TOOLS = [
    {
        "name": "search_web",
        "description": "Search the web for information about a company, job role, or industry.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_url",
        "description": "Fetch the contents of a webpage. Use this to read a job posting URL directly.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to fetch"}
            },
            "required": ["url"]
        }
    }
]

def run_tool(tool_name, tool_input):
    if tool_name == "search_web":
        return search_web(tool_input["query"])
    elif tool_name == "fetch_url":
        return fetch_url(tool_input["url"])
    return "Tool not found"

def run_agent(system_prompt, user_message, max_tokens=4000):
    messages = [{"role": "user", "content": user_message}]
    agent_log = []

    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=max_tokens,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    log_entry = f"Using {block.name}: {list(block.input.values())[0]}"
                    agent_log.append(log_entry)
                    print(log_entry)
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            return final_text, agent_log

        else:
            return "", agent_log

def parse_json(text):
    clean = text.strip()
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            if part.startswith("json"):
                clean = part[4:].strip()
                break
            elif "{" in part:
                clean = part.strip()
                break
    return json.loads(clean)

def analyze_job(job_input):
    resume = load_resume()
    system_prompt = f"""You are an expert career coach and resume writer with deep knowledge of the tech and AI industry.

Analyze the job posting, research the company, and produce:
1. A match score (0-100)
2. A tailored resume highlighting relevant experience
3. A compelling cover letter

Always search for company information first to understand their culture and tech stack.
Extract keywords from the job description and weave them into the resume.
Keep the resume truthful — reframe and reorder existing experience, never fabricate.

The candidate's master resume:
{resume}

Return ONLY valid JSON in this exact format:
{{
    "match_score": 85,
    "match_summary": "2-3 sentence explanation",
    "key_requirements": ["req 1", "req 2", "req 3"],
    "missing_skills": ["skill 1", "skill 2"],
    "tailored_resume": "Full tailored resume text",
    "cover_letter": "Full cover letter text",
    "keywords_added": ["keyword 1", "keyword 2"]
}}"""

    text, agent_log = run_agent(
        system_prompt,
        f"Analyze this job and tailor my resume:\n\n{job_input}",
        max_tokens=4000
    )

    try:
        result = parse_json(text)
        result["agent_log"] = agent_log
        return result
    except:
        return {"error": "Could not parse response", "raw": text, "agent_log": agent_log}

def find_and_tailor_jobs(criteria):
    resume = load_resume()
    system_prompt = f"""You are an expert career coach and job search specialist.

Your job:
1. Search for real current job postings matching the candidate's criteria
2. Find 4-5 strong matches using multiple targeted searches
3. Fetch job URLs when available to get full descriptions
4. For each job tailor the candidate's resume and write a cover letter

Search strategy:
- Use multiple searches with different angles and keywords
- Try job boards like LinkedIn, Indeed, Greenhouse, Lever, Workday
- Search company career pages directly
- Focus on recently posted jobs

The candidate's master resume:
{resume}

Return ONLY valid JSON in this exact format:
{{
    "jobs": [
        {{
            "title": "Job title",
            "company": "Company name",
            "location": "Location or Remote",
            "url": "Job posting URL",
            "salary": "Salary range if mentioned",
            "match_score": 85,
            "match_summary": "Why this is a good match in 2 sentences",
            "key_requirements": ["req 1", "req 2", "req 3"],
            "missing_skills": ["skill 1"],
            "tailored_resume": "Full tailored resume for this job",
            "cover_letter": "Full cover letter for this job",
            "keywords_added": ["keyword 1", "keyword 2"]
        }}
    ],
    "search_summary": "Summary of what you searched and found"
}}"""

    text, agent_log = run_agent(
        system_prompt,
        f"Find jobs matching these criteria and tailor my resume for each:\n\n{criteria}",
        max_tokens=8000
    )

    try:
        result = parse_json(text)
        result["agent_log"] = agent_log
        return result
    except:
        return {"error": "Could not parse response", "raw": text, "agent_log": agent_log}

def send_email(subject, html_body, attachments=[]):
    gmail = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")
    recipient = os.getenv("NOTIFY_EMAIL")

    msg = MIMEMultipart("mixed")
    msg["From"] = gmail
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    for filename, content in attachments:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(content.encode())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail, password)
        server.sendmail(gmail, recipient, msg.as_string())

    print(f"Email sent to {recipient}")

def build_email_html(jobs, search_summary):
    html = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <h1 style="color: #3b5bdb; font-size: 24px;">Daily Job Report</h1>
    <p style="color: #666;">{datetime.now().strftime('%A, %B %d %Y')} — {len(jobs)} jobs found</p>
    <p style="background: #f8fafc; padding: 12px; border-radius: 8px; color: #555; font-size: 14px;">{search_summary}</p>
    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
    """

    for i, job in enumerate(jobs):
        score = job.get("match_score", 0)
        color = "#16a34a" if score >= 70 else "#d97706" if score >= 50 else "#dc2626"
        bg = "#f0fdf4" if score >= 70 else "#fffbeb" if score >= 50 else "#fff5f5"
        html += f"""
        <div style="border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 20px; overflow: hidden;">
            <div style="padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                <h2 style="font-size: 16px; color: #111; margin: 0 0 4px;">{job.get('title', '')}</h2>
                <p style="font-size: 13px; color: #666; margin: 0;">{job.get('company', '')} · {job.get('location', '')} {('· ' + job.get('salary')) if job.get('salary') else ''}</p>
                <span style="display:inline-block;margin-top:8px;background:{bg};color:{color};font-weight:700;padding:4px 10px;border-radius:20px;font-size:12px;">{score}% match</span>
            </div>
            <div style="padding: 16px 20px;">
                <p style="font-size: 13px; color: #555; line-height: 1.6; margin-bottom: 12px;">{job.get('match_summary', '')}</p>
                <p style="font-size: 12px; font-weight: 600; color: #888; margin-bottom: 4px;">KEY REQUIREMENTS</p>
                <p style="font-size: 13px; color: #3b5bdb;">{' · '.join(job.get('key_requirements', []))}</p>
                {f'<p style="font-size: 12px; font-weight: 600; color: #888; margin: 10px 0 4px;">SKILLS TO DEVELOP</p><p style="font-size: 13px; color: #dc2626;">{" · ".join(job.get("missing_skills", []))}</p>' if job.get('missing_skills') else ''}
                {f'<p style="margin-top: 14px;"><a href="{job.get("url")}" style="background: #3b5bdb; color: #fff; padding: 8px 16px; border-radius: 7px; text-decoration: none; font-size: 13px;">View job posting</a></p>' if job.get('url') else ''}
                <p style="font-size: 12px; color: #888; margin-top: 10px;">Resume + cover letter attached as Job_{i+1}_{job.get('company','').replace(' ','_')}.txt</p>
            </div>
        </div>"""

    html += "</body></html>"
    return html

def build_attachments(jobs):
    attachments = []
    for i, job in enumerate(jobs):
        filename = f"Job_{i+1}_{job.get('company','Company').replace(' ','_')}.txt"
        content = f"""JOB: {job.get('title')} at {job.get('company')}
LOCATION: {job.get('location')}
MATCH SCORE: {job.get('match_score')}%
URL: {job.get('url', 'Not available')}

{'='*60}
TAILORED RESUME
{'='*60}
{job.get('tailored_resume', '')}

{'='*60}
COVER LETTER
{'='*60}
{job.get('cover_letter', '')}
"""
        attachments.append((filename, content))
    return attachments

def run_daily_job_search():
    print(f"\n[{datetime.now()}] Running scheduled job search...")
    criteria = """
Role: AI Product Manager, AI Engineer, Technical PM
Location: Vancouver, Remote Canada, Remote
Experience: Senior, Mid-level
Salary: $100k+
Preferences: Tech companies, startups, AI-focused roles
"""
    try:
        result = find_and_tailor_jobs(criteria)
        jobs = result.get("jobs", [])
        search_summary = result.get("search_summary", "")
        if not jobs:
            print("No jobs found this run.")
            return
        html = build_email_html(jobs, search_summary)
        attachments = build_attachments(jobs)
        subject = f"Daily Job Report — {len(jobs)} matches — {datetime.now().strftime('%b %d %Y')}"
        send_email(subject, html, attachments)
        print(f"Done. Found {len(jobs)} jobs. Email sent.")
    except Exception as e:
        print(f"Scheduled job search failed: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(
    run_daily_job_search,
    trigger="cron",
    hour=8,
    minute=0,
    id="daily_job_search"
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    job_input = request.json.get("job_input", "").strip()
    if not job_input:
        return jsonify({"error": "Please paste a job description or URL."})
    try:
        result = analyze_job(job_input)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/find-jobs", methods=["POST"])
def find_jobs():
    criteria = request.json.get("criteria", "").strip()
    if not criteria:
        return jsonify({"error": "Please describe what jobs you're looking for."})
    try:
        result = find_and_tailor_jobs(criteria)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/trigger-now", methods=["POST"])
def trigger_now():
    thread = threading.Thread(target=run_daily_job_search)
    thread.daemon = True
    thread.start()
    return jsonify({"message": "Running in background — check your email in 2 minutes"})

if __name__ == "__main__":
    scheduler.start()
    print("Scheduler started — daily job search runs at 8:00 AM")
    print("Visit http://127.0.0.1:5000 to also run manually")
    try:
        app.run(debug=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()