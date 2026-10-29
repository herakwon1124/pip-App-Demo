# Deploy lab walkthrough

By the end of this lab you have: your own Postgres database on Railway with a schema you designed and the class dataset loaded into it deployed at a public URL. Three parts: **database / deploy**, **backend + frontend / deploy**, **communication (APIs and env vars)**.

**Database note** Railway's Postgres is private by default: only
services running INSIDE Railway can reach it. Your laptop is outside, so it needs the PUBLIC url; your deployed app is inside, so it uses the PRIVATE one.  In your code, the variable name (`DATABASE_URL`) stays constant and the address swap is controlled by the execution environment.

Most common issues:
1. `.env` appearing in `git status` — STOP before pushing. It must be ignored.
2. Schema/loader script hangs or "could not connect" from your laptop — you copied the PRIVATE url (host ends in `railway.internal`). That host only exists inside Railway. Use the public one locally.
3. Deploy fails with a missing env var — the variable exists on your laptop's `.env` but was never added in Railway's Variables tab.

## Part 0

```
>> git status   (clean tree, .env NOT listed)
>> git add . && git commit -m "before deploy lab"   (if anything was pending)
```

Download `class_dataset.csv` from Brightspace into your project's folder.

## Part 1 — Design the schema with the agent, then deploy it

What are the entities, what are the attributes, what links them. The schema is the computer language for that. 

### 1a — Provision the database (3 min)

1. Railway → **New Project** → **Deploy PostgreSQL**. Ths provisions the database.
2. Click the Postgres service → **Connect**. It opens on the **Private Network** tab but your laptop needs the **Public Network** tab → **Add Public Access**. (If a `something.proxy.rlwy.net:PORT` address is already listed there or under Settings → Networking, public access is already on — skip the button.)
3. Deploy the changes
4. On the Variables tab, copy the value of **`DATABASE_PUBLIC_URL`** into your local `.env` as `DATABASE_URL=...` This is the only place this URL should ever go for security reasons (Railway warns you about this)

### 1b — Design the schema interactively (12 min)

Open `data/class_dataset.csv` in Cursor and look at it first. One row per
student. Most columns are plain attributes. Two are not: `tools` and
`availability` hold several values per cell, joined by semicolons. This is a hint that they may be better suited to their own tables

Attach the CSV to the agent chat and start a conversation:

> Here is a CSV of student intake responses (data/class_dataset.csv). Before
> writing any code, propose a relational schema for it: the entities, their
> attributes with types, primary keys, and the relationships between them. Point
> out any columns that hold more than one value per row and say how you would
> handle them. Ask me if anything is ambiguous.

Aspects to look for in the discussion:

- **"Name can't be the primary key."** Two students can share a name. Ask for a generated `student_id`.
- **"`tools` is many-to-many."** A student uses many tools; a tool is used by many students. That is a `tools` table and a `student_tools` bridge table, not a text column. Same for `availability`.
- **"The four skill columns are attributes of the student,"** integers 1–5 so they stay on `students`.
- **"What type is `submitted_at`?"** It is a timestamp, not text.

Ask for the result as `CREATE TABLE` statements and read them against the three rules: entity → table, 1:N → foreign key, M:N → bridge table. Iterate with the agent as necessary. Tell the agent to create a schema file.


### 1c — Deploy the schema and load the data

> Write and run a Python script (psycopg2) that connects to the Postgres at
> DATABASE_URL from my .env, creates the tables from the schema we agreed on,
> and loads data/class_dataset.csv into them — splitting the semicolon-joined
> tools and availability values into the bridge tables. Print the row count of
> every table when done.

Watch what it does: it creates the structure first (`CREATE TABLE`, in
dependency order — parents before bridges), then fills it (`INSERT`). That is the schema doing its job: the database refuses rows that don't fit.

**Verify yourself** in Railway's **Data** tab

### 1d - Interact with the database via Python
Tell the agent:
>> Write a script to connect and run the following queries so we have a base for interacting
>> with the database and paste the following:

```sql
SELECT count(*) FROM students;              -- must match the CSV's row count
SELECT name, school_year FROM students LIMIT 5;

SELECT t.name, COUNT(*) AS n_students        -- the lab's query 5, on your data
FROM student_tools st
JOIN tools t ON st.tool_id = t.id
GROUP BY t.name
ORDER BY n_students DESC;
```

(Table and column names may differ slightly depending on what you and the agent agreed — that is fine; read your own schema.)
