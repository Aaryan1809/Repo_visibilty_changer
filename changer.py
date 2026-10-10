"""
Change GitHub repo visibility using two simple text files.

HOW IT WORKS
  private_list.txt  -> repos listed here will be made PRIVATE
  public_list.txt   -> repos listed here will be made PUBLIC
  Only the repos you write in these files are touched. Nothing else.

FILE FORMAT
  One repo name per line. Lines starting with # and blank lines are ignored.
  Example:
      my-portfolio
      old-college-project

SETUP (once)
  pip install requests
  create a .env and add the github token in that .env using (GITHUB_TOKEN=...YOUR_TOKEN...)
    
RUN
  python change_visibility.py
  It shows a plan first and asks you to type YES before changing anything.
"""

import os
import sys
import time

import requests
from dotenv import load_dotenv

API = "https://api.github.com"
HERE = os.path.dirname(os.path.abspath(__file__))


def read_list(filename):
    path = os.path.join(HERE, filename)
    if not os.path.exists(path):
        return []
    names = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # allow pasting full URLs or owner/repo; keep just the repo name
            name = line.rstrip("/").split("/")[-1]
            if name.endswith(".git"):
                name = name[:-4]
            names.append(name)
    return names


def main():
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        sys.exit(
            "Set the GITHUB_TOKEN environment variable first (see top of this file).")

    to_private = read_list("private_list.txt")
    to_public = read_list("public_list.txt")

    both = set(to_private) & set(to_public)
    if both:
        sys.exit("These repos are in BOTH files, fix that first: " +
                 ", ".join(sorted(both)))
    if not to_private and not to_public:
        sys.exit(
            "Both list files are empty. Add repo names to private_list.txt / public_list.txt.")

    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })

    me = s.get(f"{API}/user")
    if me.status_code != 200:
        sys.exit(
            f"Could not log in with that token: {me.json().get('message')}")
    owner = me.json()["login"]
    print(f"Logged in as: {owner}\n")

    # build the plan by checking each repo's current state
    plan, problems = [], []
    for names, want_private in ((to_private, True), (to_public, False)):
        for name in names:
            r = s.get(f"{API}/repos/{owner}/{name}")
            if r.status_code != 200:
                problems.append(f"{name}: not found or no access")
                continue
            data = r.json()
            if data["private"] == want_private:
                state = "private" if want_private else "public"
                problems.append(f"{name}: already {state}, skipping")
                continue
            plan.append((name, want_private, data["fork"]))

    for p in problems:
        print(f"[skip] {p}")
    if problems:
        print()

    if not plan:
        sys.exit("Nothing to change.")

    print("PLAN:")
    for name, want_private, is_fork in plan:
        arrow = "public -> PRIVATE" if want_private else "private -> PUBLIC"
        print(f"  {name}: {arrow}{'  (fork)' if is_fork else ''}")

    if any(not wp for _, wp, _ in plan):
        print("\nWARNING: making a repo public exposes all its code AND git history.")
        print("Check for API keys, .env files, passwords and client data first.")

    if input("\nType YES to apply these changes: ").strip() != "YES":
        sys.exit("Cancelled. Nothing was changed.")

    print()
    ok, failed = 0, []
    for name, want_private, _ in plan:
        r = s.patch(f"{API}/repos/{owner}/{name}",
                    json={"private": want_private})
        if r.status_code == 200:
            print(f"[done]   {name}")
            ok += 1
        else:
            print(
                f"[failed] {name} -> {r.status_code}: {r.json().get('message', r.text)}")
            failed.append(name)
        time.sleep(1)

    print(f"\nChanged: {ok} | Failed: {len(failed)}")


if __name__ == "__main__":
    main()
