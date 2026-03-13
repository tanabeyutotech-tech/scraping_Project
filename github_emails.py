# github_emails.py
import requests
import time
import re
from config import HEADERS

def extract_gmail(text):
    """Extract Gmail address from a string"""
    if not text:
        return None
    match = re.search(r"[A-Za-z0-9._%+-]+@gmail\.com", text)
    return match.group(0) if match else None


def find_email(username):
    """
    Find user's email from profile first, then commits.
    Prefer Gmail, fallback to other email.
    """

    # 1️⃣ Get user profile
    profile_url = f"https://api.github.com/users/{username}"
    try:
        p = requests.get(profile_url, headers=HEADERS)
    except requests.RequestException as e:
        print(f"Network error for {username}: {e}")
        return None, None

    if p.status_code != 200:
        print(f"Cannot fetch profile for {username}, status: {p.status_code}")
        return None, None

    try:
        profile = p.json()
    except ValueError:
        print(f"Invalid JSON response for profile {username}")
        return None, None

    # Skip organizations
    if profile.get("type") != "User":
        print(f"Skipping organization: {username}")
        return None, None

    # Get display name if needed
    display_name = profile.get("name") or ""

    # 2️⃣ Check emails in profile
    profile_email = profile.get("email")
    blog = profile.get("blog")

    gmail = extract_gmail(profile_email)
    if gmail:
        return None, gmail  # Direct Gmail from profile

    gmail = extract_gmail(blog)
    if gmail:
        return None, gmail  # Gmail in blog link

    # 3️⃣ Check latest repo commits
    repo_url = f"https://api.github.com/users/{username}/repos?sort=created&per_page=1"
    try:
        r = requests.get(repo_url, headers=HEADERS)
    except requests.RequestException as e:
        print(f"Network error for repos {username}: {e}")
        return None, None

    if r.status_code != 200:
        print(f"Cannot fetch repos for {username}, status: {r.status_code}")
        return None, None

    try:
        repos = r.json()
    except ValueError:
        print(f"Invalid JSON response for repos {username}")
        return None, None

    if not isinstance(repos, list) or len(repos) == 0:
        print(f"No repos for {username}")
        return None, None

    latest_repo = repos[0]["name"]

    # Fetch commits
    commit_url = f"https://api.github.com/repos/{username}/{latest_repo}/commits?per_page=10"
    try:
        c = requests.get(commit_url, headers=HEADERS)
    except requests.RequestException as e:
        print(f"Network error for commits {username}: {e}")
        return latest_repo, None

    if c.status_code != 200:
        print(f"Cannot fetch commits for {username}/{latest_repo}, status: {c.status_code}")
        return latest_repo, None

    try:
        commits = c.json()
    except ValueError:
        print(f"Invalid JSON response for commits {username}/{latest_repo}")
        return latest_repo, None

    if not isinstance(commits, list) or len(commits) == 0:
        print(f"No commits found for {username}/{latest_repo}")
        return latest_repo, None

    # 4️⃣ Extract emails from commits
    gmail_email = None
    business_email = None

    for commit in commits:
        try:
            email = commit["commit"]["author"]["email"]
            if not email or "noreply" in email:
                continue

            if email.endswith("@gmail.com"):
                gmail_email = email
                break  # prefer Gmail

            if business_email is None:
                business_email = email

        except KeyError:
            continue

    # Prefer Gmail
    email = gmail_email if gmail_email else business_email

    # 5️⃣ Sleep to avoid rate-limit
    time.sleep(0.5)

    return latest_repo, email