# App deploy walkthrough

By the end of this lab you have a web app at a public URL that reads from a database: **browser (frontend) → Flask (backend) → Postgres (database)**.

**Most common issues**

1. `.env` appears in `git status` — STOP before pushing. It must be ignored.
2. Works locally, fails on Railway with "connection refused" or no response — the app is listening on `localhost` or a fixed port. Railway needs `0.0.0.0` and the `PORT` variable it provides. Paste the deploy log to the agent.
3. Deploy fails with "DATABASE_URL not set" — the variable exists in your laptop's `.env` but was never added in Railway's Variables tab.
4. Agent hardcoded the database address in the Python — ask it to read `DATABASE_URL` from the environment instead. Never paste the URL into code.
5. The `${{Postgres.DATABASE_URL}}` reference shows as literal text — your app is in a different Railway project than your database. Either move it (New → GitHub repo *inside* the Postgres project) or paste the `DATABASE_PUBLIC_URL` value instead. Both work; the first is what production looks like.

## Stage 0 — Where you are

Open the project folder from Class 7 in Cursor. You should have `schema.sql`, your loader script, `class_dataset.csv`, `.env`, `.gitignore`. Your Railway project has one service: Postgres, with the tables loaded.

```
>> git status        (clean tree, .env NOT listed)
```

Give the agent the high level context for what you are trying to accomplish:
> We are going to walk through building an app piece by piece. local first then we'll do a deploy later. 

## Stage 1a — A page that lists the names

> Build a web page that shows the list of student names from my database. Use Flask for the backend and plain HTML for the page.

Run it the way the agent tells you to. Open the URL it gives you in a browser (usually `http://localhost:5000` or `:8000`). You should see the names.

**Now read what it made.** Find:

- the Python file (`app.py` or similar): where is the SQL? where does it read the database address? (It should be reading `DATABASE_URL` from `.env` / the environment. If you see the actual address in the code, see issue 4.)
- the HTML file: where do the names go into the page?

The agent chose one of two patterns. Either the Python puts the names into the HTML before sending it (server-rendered), or the page is sent empty and a bit of JavaScript asks the Python for the names afterward (an API call).

**What happened** when you loaded the page: browser asks Flask for `/` → Flask asks Postgres `SELECT name FROM students` → Flask sends the page back. That round trip is a *request* and a *response*; the address Flask answers at (`/`) is a *route*.

## Stage 1b — A button that shuffles the names

> Add a button that shuffles the order of the names. Use plain JavaScript.

Reload. Click. The names reorder.

Open Cursor's diff of what the agent changed. There is now JavaScript (a `.js` file or a `<script>` block). Read it: it grabs the list, shuffles it, redraws it. **It never talked to the database.** The shuffle runs in your browser.

The frontend is not just display. It is also behavior: what happens when the user clicks, types, scrolls. HTML is the structure; JavaScript is the behavior; both run in the browser. Flask runs on a server and only hears from the browser when the page asks for something.

```
>> git add . && git commit -m "names page with shuffle"
```

## Stage 2 — Deploy

> Get this ready to deploy on Railway using a Dockerfile.

The agent adds a `Dockerfile` (packaging instructions: which Python, which packages, how to start the app) and may adjust how the app starts so Railway can reach it. Read the last line of the Dockerfile; it should start the app on `0.0.0.0` and the `PORT` environment variable, not a fixed `localhost:5000`. If not, ask the agent to fix it (issue 2).

Then, together:

1. `git status` — `.env` must not be listed. `git add . && git commit -m "dockerfile" && git push`. (If this folder is not on GitHub yet: `GitHub and Railway deploy guide.md`, Part 1.)
2. Railway → open **your existing Postgres project** → **+ New** → **GitHub Repo** → pick this repo. Railway finds the Dockerfile and builds. Do not create a new project; the app and the database should live together.
3. Click the new service → **Variables** → **New Variable**: name `DATABASE_URL`, value `${{Postgres.DATABASE_URL}}`. Railway fills in the private address of the Postgres sitting next to it. Same variable name your laptop uses; different value; different home. The code did not change.
4. **Settings → Networking → Generate Domain.** Open it. Open it on your phone. Click shuffle.

If the build or app fails: deployment → **Deploy Logs** → last 20 lines → paste to the agent verbatim.

**What happened:** your laptop's `.env` said "the database is at this public address." Railway's variable says "the database is at this private address." Your Python asked for `DATABASE_URL` and got whichever one its environment provided. That is what an environment variable is for.

## Stage 3 — Add a model

> Add to the page the average of each of the four skill ratings across all students.

Run locally. Four numbers appear. Look at where the averaging happens: in SQL (`AVG(...)`) or in Python after fetching rows. Either is fine; note which.

```
>> git add . && git commit -m "skill averages" && git push
```

Watch Railway rebuild. Reload the public URL. The averages are live. **Deploying a change is now just a push.**

You just deployed a model. Inputs: every row in `students`. Output: four numbers.

## Stage 4 — Break it on purpose

Railway → your app service → Variables → delete `DATABASE_URL`. Watch it redeploy and fail. Open the Deploy Logs; find the line that says why. Add the variable back.

