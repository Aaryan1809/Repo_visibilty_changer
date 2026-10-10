# GitHub Visibility Changer

A small Python script that changes your GitHub repositories between **public** and **private** in bulk, using two plain text files as input.

Instead of opening every repo → Settings → scrolling to the Danger Zone → changing visibility → typing the repo name to confirm (over and over), you write the repo names in a file, run one command, and the script does the boring part for you.

> **Safe by design:** the script only touches repos whose names you write in the list files. There is no "change everything" mode. It also shows you a plan and asks for confirmation before it changes anything.

---

## Table of Contents

1. [What this project does](#what-this-project-does)
2. [How it works (the big picture)](#how-it-works-the-big-picture)
3. [Is this allowed by GitHub?](#is-this-allowed-by-github)
4. [Project files explained](#project-files-explained)
5. [Before you start (prerequisites)](#before-you-start-prerequisites)
6. [Step-by-step setup](#step-by-step-setup)
7. [How to run it](#how-to-run-it)
8. [Example run](#example-run)
9. [Things to know before changing visibility](#things-to-know-before-changing-visibility)
10. [Troubleshooting](#troubleshooting)
11. [Security tips](#security-tips)
12. [Limitations](#limitations)
13. [FAQ](#faq)

---

## What this project does

- Reads two files: `private_list.txt` and `public_list.txt`.
- Makes every repo named in `private_list.txt` **private**.
- Makes every repo named in `public_list.txt` **public**.
- Skips repos that are already in the state you asked for.
- Skips (and tells you about) repo names that don't exist or that your token can't access.
- Shows you a full plan first, and only continues if you type `YES`.

---

## How it works (the big picture)

```
 private_list.txt ─┐
                   ├──►  change_visibility.py  ──►  GitHub REST API  ──►  your repos change
 public_list.txt  ─┘            ▲
                                │
                              .env  (holds your secret GitHub token)
```

1. The script loads your GitHub token from the `.env` file.
2. It logs in to GitHub and finds out your username.
3. It reads both list files and checks the **current** visibility of each repo.
4. It prints a plan, for example `old-project: public -> PRIVATE`.
5. You type `YES` to confirm.
6. It sends one API request per repo to change the visibility (with a 1 second pause between requests to avoid GitHub's rate limits).
7. It prints a summary of what worked and what failed.

---

## Is this allowed by GitHub?

Yes. This script uses GitHub's **official REST API**, which GitHub provides specifically so people can automate things like this. It does not scrape the website or bypass any rule. You authenticate with your own **Personal Access Token**, which you can revoke at any time.

---

## Project files explained

| File | What it is |
|---|---|
| `change_visibility.py` | The main script. This is the file you run. |
| `private_list.txt` | You write repo names here that you want to make **private**. |
| `public_list.txt` | You write repo names here that you want to make **public**. |
| `.env` | **You create this.** It stores your secret GitHub token. Never upload this file to GitHub. |
| `requirements.txt` | The list of Python packages needed (`requests`, `python-dotenv`). |
| `.gitignore` | Tells Git to ignore `.env` so your token can't be uploaded by accident. |
| `README.md` | This guide. |

---

## Before you start (prerequisites)

You need three things:

1. **A GitHub account** (the one that owns the repos you want to change).
2. **Python 3.8 or newer** installed on your computer.
3. **Git** installed (only needed if you want to use `git clone`; you can also download the ZIP from GitHub instead).

### Check if Python is installed

Open a terminal (Command Prompt / PowerShell on Windows, Terminal on Mac/Linux) and run:

```bash
python --version
```

On Mac/Linux you may need to use `python3` instead:

```bash
python3 --version
```

If you see something like `Python 3.11.4`, you're good. If you get an error, download Python from <https://www.python.org/downloads/>.

> **Windows users:** during Python installation, tick the box **"Add Python to PATH"**. Otherwise the `python` command won't work.

### Check if Git is installed

```bash
git --version
```

If it's missing, download it from <https://git-scm.com/downloads>.

> **Note:** If your computer uses `python3` and `pip3` instead of `python` and `pip`, use those everywhere in this guide.

---

## Step-by-step setup

### Step 1: Clone the repository

Open a terminal in the folder where you want the project, then run:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
```

Replace `<your-username>` and `<repo-name>` with the real values from this repository's URL. Then go inside the project folder:

```bash
cd <repo-name>
```

> **No Git?** On the repository page click the green **Code** button → **Download ZIP**, extract it, and open a terminal inside the extracted folder.

### Step 2 (optional but recommended): Create a virtual environment

A virtual environment keeps this project's packages separate from the rest of your computer.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

When it's active you'll see `(venv)` at the start of your terminal line. You can skip this step, the script will still work.

### Step 3: Install the required packages

The easy way (installs everything at once):

```bash
pip install -r requirements.txt
```

Or install them one by one:

```bash
pip install requests
pip install python-dotenv
```

- `requests` lets Python talk to the GitHub API.
- `python-dotenv` lets the script read your token from the `.env` file.

### Step 4: Create a GitHub Personal Access Token

The token is like a password that lets the script act on your account.

1. Log in to GitHub and click your **profile picture** (top right) → **Settings**.
2. Scroll down the left sidebar and click **Developer settings** (at the very bottom).
3. Click **Personal access tokens**.

You can use either type of token:

#### Option A: Token (classic) — simplest

1. Click **Tokens (classic)** → **Generate new token** → **Generate new token (classic)**.
2. **Note:** give it a name, e.g. `visibility-changer`.
3. **Expiration:** choose a short time, e.g. 7 or 30 days. You can always make a new one.
4. **Scopes:** tick **`repo`** (this is the full "repo" checkbox).
5. Click **Generate token** at the bottom.
6. **Copy the token immediately.** It starts with `ghp_`. GitHub will never show it again.

#### Option B: Fine-grained token — more restricted

1. Click **Fine-grained tokens** → **Generate new token**.
2. Give it a name and expiration.
3. Under **Repository access**, choose **All repositories** (or **Only select repositories** and pick the ones you want to change).
4. Under **Repository permissions**, set **Administration** to **Read and write**. (Metadata: Read-only is added automatically.)
5. Click **Generate token** and copy it (starts with `github_pat_`).

> Changing visibility is an admin action, so a token without Administration permission will fail with a 403 or 404 error.

### Step 5: Create the `.env` file

In the project folder (next to `change_visibility.py`), create a new file named exactly `.env` (with the dot at the start and nothing after `env`).

Put this single line inside it, replacing the placeholder with your real token:

```
GITHUB_TOKEN=paste_your_token_here
```

Rules:
- No spaces around the `=`.
- No quotes around the token.
- Nothing else on that line.

**Easy ways to create it:**

- **Mac / Linux terminal:**
  ```bash
  echo "GITHUB_TOKEN=paste_your_token_here" > .env
  ```
- **Windows PowerShell:**
  ```powershell
  "GITHUB_TOKEN=paste_your_token_here" | Out-File -Encoding ascii .env
  ```
- **Any OS:** open the folder in VS Code (or any editor), create a new file, name it `.env`, paste the line, save.

> **Windows warning:** Notepad often saves the file as `.env.txt` by accident. If you use Notepad, choose **Save as type: All files** and make sure the name is exactly `.env`. Turn on **File name extensions** in File Explorer (View → Show) to double-check.

### Step 6: Fill in the list files

Open `private_list.txt` and add the names of repos you want to make **private**, one per line:

```
old-college-project
test-repo-1
random-experiment
```

Open `public_list.txt` and add the names of repos you want to make **public**, one per line:

```
my-portfolio
cool-open-source-tool
```

Rules for the list files:

- **One repo name per line.**
- Use the **repo name only**, not your username. If your repo URL is `https://github.com/yourname/my-portfolio`, write `my-portfolio`. (Pasting the full URL also works, the script extracts the name.)
- Lines starting with `#` are comments and are ignored. Blank lines are ignored.
- Spelling matters. A wrong name is reported as "not found" and skipped.
- A repo must **not** be in both files. If it is, the script stops and tells you.
- You can leave one file empty if you only want to go in one direction.

---

## How to run it

Make sure you are inside the project folder in your terminal, then run:

```bash
python change_visibility.py
```

(Use `python3 change_visibility.py` on Mac/Linux if `python` doesn't work.)

What you'll see:

1. `Logged in as: your-username`: confirms the token works.
2. Any `[skip]` lines: repos that don't exist, can't be accessed, or are already in the requested state.
3. A **PLAN:** listing every change that will be made.
4. A prompt: `Type YES to apply these changes:`

Type `YES` (capital letters) and press Enter to go ahead. Type anything else (or press Ctrl+C) to cancel, and nothing will be changed.

---

## Example run

`private_list.txt`
```
old-college-project
already-private-repo
typo-repo-nmae
```

`public_list.txt`
```
my-portfolio
```

Output:

```
Logged in as: yourname

[skip] already-private-repo: already private, skipping
[skip] typo-repo-nmae: not found or no access

PLAN:
  old-college-project: public -> PRIVATE
  my-portfolio: private -> PUBLIC

WARNING: making a repo public exposes all its code AND git history.
Check for API keys, .env files, passwords and client data first.

Type YES to apply these changes: YES

[done]   old-college-project
[done]   my-portfolio

Changed: 2 | Failed: 0
```

---

## Things to know before changing visibility

**Making repos private:**
- **Forks:** GitHub does not let you make a fork of a public repo private. These will show as `[failed]`, which is expected.
- **GitHub Pages:** on a free account, a private repo cannot publish a Pages site, so any live website hosted from that repo will go offline.
- **Stars and watchers** can be lost when a repo goes private, and public forks of it get detached.
- **Integrations:** services like Vercel or Netlify may need their GitHub access re-checked for private repos.

**Making repos public:**
- Everything becomes visible: all files **and the entire commit history**. A password, API key, or `.env` you committed once and later deleted is **still visible in old commits**.
- Double-check client work, credentials, and personal data before making anything public.

**Reversibility:** you can switch any repo back at any time, but lost stars and watchers will not return.

---

## Troubleshooting

| Problem | What it means / how to fix it |
|---|---|
| `ModuleNotFoundError: No module named 'requests'` | Run `pip install requests`. |
| `ModuleNotFoundError: No module named 'dotenv'` | Run `pip install python-dotenv` (the package name differs from the import name). |
| `'python' is not recognized...` (Windows) | Python isn't on PATH. Reinstall Python with "Add Python to PATH" ticked, or try `py change_visibility.py`. |
| `Set the GITHUB_TOKEN environment variable first` | The `.env` file is missing, misnamed (check for `.env.txt`), in the wrong folder, or the line is wrong. It must sit next to `change_visibility.py` and contain `GITHUB_TOKEN=...`. |
| `Could not log in with that token: Bad credentials` | The token was copied incorrectly, has expired, or was revoked. Generate a new one. |
| `[skip] name: not found or no access` | Typo in the repo name, the repo isn't owned by your account, or your token doesn't have access to it (fine-grained tokens must include that repo). |
| `[failed] ... 403` or `404` | The token lacks permission. Classic token: tick `repo`. Fine-grained: set Administration to Read and write. |
| `[failed] ... 422` | GitHub refused the change, commonly because the repo is a fork of a public repo, or your plan doesn't allow it. |
| `Both list files are empty` | Add at least one repo name (without a leading `#`) to one of the files. |
| `These repos are in BOTH files` | Remove the repo from one of the two files. |

---

## Security tips

- **Never upload your `.env` file or token to GitHub.** The included `.gitignore` already ignores `.env`, so don't remove that line.
- If you ever accidentally expose your token, go to GitHub → Settings → Developer settings → Personal access tokens and **delete it immediately**, then create a new one.
- Use a short expiration date, and delete the token when you're done with it.
- Only give the token the permissions it needs.

---

## Limitations

- It works on repositories **owned by your personal account**. Repos owned by an organization are not handled by this script.
- It cannot change forks of public repos to private (a GitHub rule).
- It needs an internet connection and a valid token.

---

## FAQ

**Will it change all my repos?**
No. It only changes the repos whose names you write in the two list files.

**What if I run it twice?**
Nothing bad happens. Repos already in the requested state are skipped.

**Can I undo a change?**
Yes. Move the repo name to the other list file and run the script again.

**Can I use it for just one repo?**
Yes. Put only that one name in a list file.

**Does it delete anything?**
No. It only changes the visibility setting.

**Do I need to run it as administrator?**
No. Run it as a normal user in your own project folder.

---

## Contributing

Found a bug or have an idea? Open an issue or send a pull request.

## License

Add the license of your choice here (for example MIT).