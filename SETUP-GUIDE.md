# NFL Injury Agent: Setup Guide

This guide takes you from a zip file to a tracker that updates itself. It takes about 20 minutes, and everything happens in your web browser. You don't need to install anything for this first setup.

## What's in the project

| File | What it does |
|---|---|
| `update_injuries.py` | The agent. Pulls ESPN's injury report, compares it to the last one, logs changes. |
| `.github/workflows/update-injuries.yml` | The schedule. Tells GitHub to run the agent every 3 hours. |
| `index.html` | Your tracker page, same look as before, now reading the agent's data. |
| `data/snapshot.json` | Every player's latest status (starts empty). |
| `data/log.json` | The change log (starts empty). |
| `data/meta.json` | When the agent last ran. |

---

## Step 1: Unzip the project

1. Find `nfl-injury-agent.zip` in your Downloads folder.
2. Right-click it and choose **Extract All…**, then click **Extract**.
3. Open the new `nfl-injury-agent` folder. You should see `.github`, `data`, `index.html`, `update_injuries.py`, and this guide.

## Step 2: Create a repository on GitHub

A repository ("repo") is a project folder that lives on GitHub.

1. Go to **github.com** and sign in.
2. Click the **+** in the top-right corner, then **New repository**.
3. Repository name: `nfl-injury-agent`
4. Choose **Public**. (Free GitHub Pages hosting needs a public repo. Everything in it is public ESPN data, so nothing private is exposed.)
5. Leave all the "Initialize" checkboxes **unchecked**.
6. Click **Create repository**.

## Step 3: Upload the files

1. On the new repo's page, click the link that says **uploading an existing file**.
2. In File Explorer, open your `nfl-injury-agent` folder and select **everything inside it** (click inside the folder, press **Ctrl+A**).
3. Drag the selected items onto the GitHub upload page.
4. Wait until the file list stops growing, then scroll down and click **Commit changes**.

## Step 4: Check that the schedule file uploaded

Folders that start with a dot sometimes get skipped by drag-and-drop, so confirm it's there.

1. On your repo's main page, look for a folder named **`.github`**.
2. If it's there, click into it and confirm you see `workflows/update-injuries.yml`. Skip to Step 5.
3. **If it's missing**, create it by hand:
   - Click **Add file → Create new file**.
   - In the filename box, type exactly: `.github/workflows/update-injuries.yml` (typing the `/` creates folders automatically).
   - Open `update-injuries.yml` from your unzipped folder in Notepad, copy all of it, and paste it into GitHub's editor.
   - Click **Commit changes**, then **Commit changes** again.

## Step 5: Let the agent save its work

The agent needs permission to save updated data back into the repo.

1. In your repo, click **Settings** (top menu, far right).
2. In the left sidebar, click **Actions → General**.
3. Scroll to **Workflow permissions**.
4. Select **Read and write permissions**.
5. Click **Save**.

## Step 6: Run the agent for the first time

1. Click the **Actions** tab at the top of your repo.
2. If you see a message about enabling workflows, click the green button to enable them.
3. In the left sidebar, click **Update NFL injuries**.
4. On the right, click **Run workflow**, then the green **Run workflow** button.
5. After a few seconds a run appears. Click it to watch. It takes about 30 seconds.
6. A **green check** means it worked. Click the **update** job and expand **Run the injury agent** to see something like *"Baseline saved: 312 players."*

To confirm, go back to the **Code** tab and open `data/snapshot.json`. It should now be full of players.

The first run only saves a baseline. Changes start appearing in the log from the second run onward.

## Step 7: Put your tracker online with GitHub Pages

1. Go to **Settings → Pages** (left sidebar).
2. Under **Build and deployment → Source**, choose **Deploy from a branch**.
3. Under **Branch**, choose **main** and **/ (root)**, then click **Save**.
4. Wait 1–2 minutes, then refresh the Settings → Pages screen. A link appears at the top, like:
   `https://YOUR-USERNAME.github.io/nfl-injury-agent/`
5. Open it. You'll see your tracker with the status board filled in. Bookmark it.

## You're done 🎉

From now on, GitHub runs the agent every 3 hours, even when your computer is off. The page reloads its data every 10 minutes while open, or you can click **Refresh page data**.

To force a check right now (say, right before a game), repeat Step 6.

---

## Changing how often it runs

Open `.github/workflows/update-injuries.yml` on GitHub, click the pencil icon, and edit the `cron` line:

| You want | Change the line to |
|---|---|
| Every 3 hours (default) | `- cron: "0 */3 * * *"` |
| Every 6 hours | `- cron: "0 */6 * * *"` |
| Once a day, 9am Eastern | `- cron: "0 13 * * *"` |
| Every hour | `- cron: "0 * * * *"` |

Commit the change and the new schedule takes effect. Note that GitHub's scheduled runs sometimes start 5–15 minutes late during busy times. That's normal.

## Troubleshooting

**Red X on a run.** Click the run, then the **update** job, then the step with the red X to read the message. The agent's messages are written in plain English.

**"could not reach ESPN"** means ESPN was down or slow. Nothing was changed, and the next run will try again. If this happens on every run for a day or more, ESPN may be blocking the request or has changed its feed. Paste the error message to Claude.

**"only X players found, but Y were listed last time"** is the safety check working. ESPN sent back something incomplete, so the agent refused to mark everyone as Cleared. It usually fixes itself on the next run.

**"Permission denied" or "403" in the Save updated data step.** Step 5 wasn't saved. Redo it, then run the workflow again.

**The Pages link shows a 404.** Wait a few more minutes after Step 7, then try again. Also make sure `index.html` is in the top level of the repo, not inside a folder.

**The page says "Couldn't load the data files."** You probably opened `index.html` straight from your computer. Browsers block that. Use your GitHub Pages link instead.

**The page status dot turns red ("no run in Xh").** Check the Actions tab. If GitHub paused the schedule (it emails you when this happens), click **Enable workflow** on the Actions tab.

**About the data source.** The ESPN feed is public but unofficial, so ESPN can change it without notice. If that happens, the safety checks keep your existing data intact, and the parsing section of `update_injuries.py` is the only part that needs updating.

---

## Next: editing the project in VS Code

Once this is running, you can use VS Code to change it, for example adding a daily email summary.

1. Install **Git for Windows** from git-scm.com (the default options are fine).
2. Open VS Code, press **Ctrl+Shift+P**, type **Git: Clone**, and press Enter.
3. Choose **Clone from GitHub**, sign in when asked, and pick `nfl-injury-agent`.
4. Choose a folder to save it in, then click **Open** when VS Code asks.
5. Make changes, then use the **Source Control** icon in the left sidebar: type a short message, click **Commit**, then **Sync Changes**.

One important habit: **click Sync (or Pull) before you start editing.** The agent saves new data to GitHub every few hours, so your computer's copy goes out of date quickly.
