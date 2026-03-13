# main.py
from github_users import get_usernames
from github_emails import find_email
from config import HEADERS
import requests

location = input("Location: ")
language = input("Language: ")

followers_start = int(input("Start followers: "))
followers_end = int(input("End followers: "))

pages_start = 0
page_end = 1
pages_start = int(input("pages start: "))
page_end = int(input("pages end: "))

# get users
users = get_usernames(location, language, followers_start, followers_end, pages_start, page_end)
print(f"Total users collected: {len(users)}")

emails_only = []
full_data = []

for user in users:
    print(f"Processing {user}")
    #get display name
    profile_url = f"https://api.github.com/users/{user}"
    r = requests.get(profile_url, headers=HEADERS)

    if not r.text.strip():
        print(f"Empty response for {user}")
        continue

    profile = r.json()

    #skip organizations
    # Skip organizations
    if profile.get("type") != "User":
        print(f"Skipping organization: {user}")
        continue

    display_name = profile.get("name")

    if not display_name:
        display_name = ""
    
    latest_repo, email = find_email(user)

    if email:
        emails_only.append(email)
        full_data.append(f"{display_name} | {user} | {email}")


# Save outputs
with open("output/emails_only.txt", "w", encoding="utf-8") as f:
    for e in emails_only:
        f.write(e + "\n")

with open("output/emails_full.txt", "w", encoding="utf-8") as f:
    for line in full_data:
        f.write(line + "\n")

print("Done! Saved emails_only.txt and emails_full.txt")