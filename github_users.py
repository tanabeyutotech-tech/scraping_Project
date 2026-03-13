# github_users.py
import requests
from config import HEADERS
import time

def get_usernames(location, language, followers_start, followers_end,  pages_start, page_end):
    users = []

    for page in range(pages_start + 1, page_end + 1):
        url = f"https://api.github.com/search/users?q=location:{location}&per_page=100&page={page}"
        # https://github.com/search?q=location%3A%22Prince+Edward%22+followers%3A0..100&type=Users&ref=advsearch&l=&l=&p=7
        # url = f"https://api.github.com/search/users?q=location:{location}+language:{language}&per_page=100&page={page}"
        # url = f"https://api.github.com/search/users?q=location:{location}+language:{language}+followers:{followers_start}..{followers_end}&per_page=100&page={page}"

        print(f"Scanning page {page}")
        r = requests.get(url, headers=HEADERS)
        data = r.json()

        if "items" not in data or len(data["items"]) == 0:
            break

        for user in data["items"]:
            users.append(user["login"])

        time.sleep(0.5)  # polite delay

    return users