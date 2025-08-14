
import requests
import re
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials


RAPIDAPI_KEY = "5d2f47a088msh1929673ba0c9655p1e6c10jsn9d5190d7dd7b" 
RAPIDAPI_HOST = "jsearch.p.rapidapi.com"
CHECK_INTERVAL = 7200  # every 2 hours
SEEN_JOB_IDS = set()

# Google Sheets setup
def get_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1JHdGeuWj77TPWzW8E8nZYomNNd4w4hPPimuMs2DTXuA/edit?gid=0#gid=0").sheet1


    # Create header row if empty
    if not sheet.get_all_values():
        sheet.append_row([
            "Company", "Role", "Location", "Type", "Remote", "CTC", "Posted On",
            "Expected Skills", "Good to Have", "Topics", "Buzzwords", "Rounds", "Cutoff", "Apply Link"
        ])
    return sheet

sheet = get_gsheet()

# ---------------- EXTRACTOR ----------------
def extract_details_from_description(desc):
    details = {
        "expected_skills": [],
        "good_to_have": [],
        "buzzwords": [],
        "rounds": None,
        "cutoff": None,
        "topics": []
    }

    if not desc:
        return details

    skills_keywords = [
        "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Ruby", "PHP", "Swift", "Kotlin", "R",
        "React", "Angular", "Vue", "Next.js", "Node.js", "Express", "HTML", "CSS", "Bootstrap", "Tailwind",
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "NoSQL", "Oracle", "Redis",
        "Machine Learning", "Deep Learning", "AI", "TensorFlow", "Keras", "PyTorch",
        "AWS", "Azure", "Google Cloud",
        "Docker", "Kubernetes", "Terraform", "Jenkins", "CI/CD"
    ]
    good_to_have_keywords = ["Leadership", "Communication", "Teamwork", "Problem-solving", "Git"]
    topics_keywords = ["Data Structures", "Algorithms", "OOP", "Database", "Cloud Computing"]

    details["expected_skills"] = [skill for skill in skills_keywords if skill.lower() in desc.lower()]
    details["good_to_have"] = [skill for skill in good_to_have_keywords if skill.lower() in desc.lower()]
    details["topics"] = [topic for topic in topics_keywords if topic.lower() in desc.lower()]

    buzzword_candidates = re.findall(r'\b[A-Z][a-zA-Z0-9]+\b', desc)
    details["buzzwords"] = list(set(buzzword_candidates) - set(details["expected_skills"]))

    rounds_match = re.search(r"(\d+)\s+rounds?", desc, re.IGNORECASE)
    if rounds_match:
        details["rounds"] = rounds_match.group(1)

    cutoff_match = re.search(r"(\d+%|\d+\.\d+ CGPA)", desc, re.IGNORECASE)
    if cutoff_match:
        details["cutoff"] = cutoff_match.group(1)

    return details

# ---------------- API CALL ----------------
def get_opportunities(query: str, num_pages: int = 1):
    url = f"https://{RAPIDAPI_HOST}/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY.strip(),
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    params = {
        "query": query,
        "page": "1",
        "num_pages": str(num_pages)
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

# ---------------- MAIN ----------------
def run_job_checker():
    queries = [
        "full stack developer",
        "backend developer",
        "frontend developer",
        "software engineer",
        
    ]

    while True:
        for query in queries:
            print(f"\n🔍 Checking for new jobs with query: {query}\n")
            jobs = get_opportunities(query)

            if not jobs:
                print("No results found.")
                continue

            for item in jobs:
                job_id = item.get("job_id")
                if job_id in SEEN_JOB_IDS:
                    continue
                SEEN_JOB_IDS.add(job_id)

                job_title = item.get("job_title", "N/A")
                company = item.get("employer_name", "N/A")
                location = item.get("job_city", "N/A")
                employment_type = item.get("job_employment_type", "N/A")
                remote = "Yes" if item.get("job_is_remote", False) else "No"
                date_posted = (item.get("job_posted_at_datetime_utc") or "N/A")[:10]
                salary_info = item.get("job_salary") or {}
                salary = salary_info.get("salary", "Not specified")
                description = item.get("job_description", "")
                url = item.get("job_apply_link", item.get("job_google_link", "#"))

                extracted = extract_details_from_description(description)

                # Add to Google Sheet
                sheet.append_row([
                    company, job_title, location, employment_type, remote, salary, date_posted,
                    ", ".join(extracted["expected_skills"]) or "Not specified",
                    ", ".join(extracted["good_to_have"]) or "Not specified",
                    ", ".join(extracted["topics"]) or "Not specified",
                    ", ".join(extracted["buzzwords"]) or "None",
                    extracted["rounds"] or "Not specified",
                    extracted["cutoff"] or "Not specified",
                    url
                ])

                # Print to console too
                print(f"🏢 Company: {company}")
                print(f"🎯 Role: {job_title}")
                print(f"📍 Location: {location}")
                print(f"🕒 Type: {employment_type}")
                print(f"🌐 Remote: {remote}")
                print(f"💰 CTC: {salary}")
                print(f"📅 Posted on: {date_posted}")
                print(f"📌 Expected Skills: {', '.join(extracted['expected_skills']) or 'Not specified'}")
                print(f"✨ Good to Have: {', '.join(extracted['good_to_have']) or 'Not specified'}")
                print(f"📚 Topics: {', '.join(extracted['topics']) or 'Not specified'}")
                print(f"🔍 Buzzwords: {', '.join(extracted['buzzwords']) or 'None'}")
                print(f"🏁 Rounds: {extracted['rounds'] or 'Not specified'}")
                print(f"🎯 Cutoff: {extracted['cutoff'] or 'Not specified'}")
                print(f"🔗 Apply: {url}")
                print("-" * 40)

        print(f"⏳ Waiting {CHECK_INTERVAL/3600} hours before next check...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_job_checker()
