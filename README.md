# Attendance Automation System

Employees mark attendance through a three-step verification flow — company
**QR code → GPS → camera** — and administrators manage staff, review records
and export them to Excel or PDF.

The project is split into a **backend** REST API (Flask) and a **frontend**
static site (HTML/CSS/JS), so each half can be deployed on a free plan:
Render for the API, Vercel for the site.

---

## Quick start (one click)

```bash
python app.py
```

That is the only file you need to run. It installs the backend requirements
on first run, creates `backend/.env` if missing, builds the database, serves
the API **and** the frontend on <http://localhost:5000>, and opens your
browser.

Default login:

| Username | Password |
| -------- | -------- |
| `admin`  | `12345`  |

> Change `ADMIN_PASSWORD` in `backend/.env` before deploying anywhere public.

---

## Project structure

```
Attendance_Automation_System/
├── app.py                     # one-click local launcher (runs everything)
├── docker-compose.yml         # backend + frontend containers together
├── README.md
├── .gitignore
│
├── backend/                   # Flask REST API  →  deploy to Render (free)
│   ├── __init__.py            # lets the root launcher import `backend.app`
│   ├── wsgi.py                # Gunicorn entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── render.yaml            # Render Blueprint
│   ├── Procfile               # start command for other free hosts
│   ├── .python-version        # pinned runtime (3.11.9)
│   ├── .env / .env.example    # backend configuration
│   ├── database/attendance.db # SQLite database (local default)
│   └── app/
│       ├── __init__.py        # application factory, CORS, blueprints
│       ├── config.py          # environment variables
│       ├── db.py              # SQLite + PostgreSQL data layer
│       ├── security.py        # password hashing, tokens, route guards
│       ├── routes/
│       │   ├── auth.py        # login, current user
│       │   ├── attendance.py  # mark attendance, personal history
│       │   ├── employees.py   # admin employee CRUD
│       │   ├── admin.py       # dashboard statistics, filtered records
│       │   ├── reports.py     # Excel and PDF exports
│       │   └── qr.py          # company QR code
│       └── scripts/           # init_db, add_employee, clear_attendance, generate_qr
│
├── frontend/                  # static site  →  deploy to Vercel (free)
│   ├── index.html             # landing page
│   ├── login.html
│   ├── dashboard.html         # employee dashboard
│   ├── attendance.html        # QR → GPS → camera flow
│   ├── history.html
│   ├── admin.html             # admin dashboard
│   ├── employees.html
│   ├── add-employee.html
│   ├── qr-poster.html         # printable company QR poster
│   ├── css/style.css
│   ├── js/
│   │   ├── config.js          # API base URL lives here
│   │   ├── api.js             # fetch client, token storage, page guards
│   │   ├── vendor/jsQR.js     # bundled QR decoder (no CDN dependency)
│   │   └── <page>.js          # one script per page
│   ├── vercel.json            # Vercel config
│   ├── Dockerfile + nginx.conf
│   └── .env / .env.example
│
└── docs/                      # report, screenshot, demo video (video is git-ignored)
```

---

## How it works

* **Auth** — `POST /api/auth/login` returns a signed, expiring token. The
  browser stores it and sends it as `Authorization: Bearer <token>`. Passwords
  are hashed with Werkzeug; any old plaintext password from the previous
  version is upgraded automatically on the owner's next successful login.
* **QR** — see [the QR code section](#the-qr-code) below.
* **Attendance** — after QR, GPS and camera checks pass in the browser, the
  page calls `POST /api/attendance/mark`. The server decides `Present` vs
  `Late` (configurable via `LATE_AFTER_HOUR`) and refuses a second record for
  the same day. The captured photo never leaves the device.
* **Exports** — Excel and PDF are generated in memory, so the service works on
  hosts with read-only or disposable filesystems.

### API reference

| Method   | Endpoint                    | Access   | Purpose                          |
| -------- | --------------------------- | -------- | -------------------------------- |
| `GET`    | `/api/health`               | public   | Health check                     |
| `POST`   | `/api/auth/login`           | public   | Sign in, receive a token         |
| `GET`    | `/api/auth/me`              | user     | Current user profile             |
| `GET`    | `/api/qr/image`             | public   | Company QR code (PNG)            |
| `GET`    | `/api/qr/payload`           | public   | What the QR encodes              |
| `POST`   | `/api/qr/verify`            | user     | Validate a scanned code          |
| `POST`   | `/api/attendance/mark`      | user     | Mark today's attendance          |
| `GET`    | `/api/attendance/history`   | user     | Own attendance records           |
| `GET`    | `/api/admin/stats`          | admin    | Dashboard counters               |
| `GET`    | `/api/admin/attendance`     | admin    | All records (`?search=&date=`)   |
| `GET`    | `/api/employees`            | admin    | List employees                   |
| `POST`   | `/api/employees`            | admin    | Create an employee               |
| `DELETE` | `/api/employees/<id>`       | admin    | Delete an employee               |
| `GET`    | `/api/reports/excel`        | admin    | Download `.xlsx`                 |
| `GET`    | `/api/reports/pdf`          | admin    | Download `.pdf`                  |

---

## The QR code

The QR code is generated by the backend itself with the `qrcode` library — no
third-party QR service, so nothing can rate-limit it, start charging, or shut
down. It encodes one permanent string:

```
https://your-project.vercel.app/attendance.html?qr=AAS-COMPANY-QR-001
```

**It never expires.** There is no timestamp, no signature and no session
inside it, so a poster printed today still scans in a year. The only two
things that change it are `FRONTEND_URL` and `COMPANY_CODE`; leave those
alone and the printed code stays valid forever. (Setting `COMPANY_CODE` to a
new value is the deliberate way to invalidate old posters.)

**Printing it** — sign in as admin → *Admin Dashboard → QR Poster* → **Print
Poster**. Or generate a file: `python -m app.scripts.generate_qr poster.png`
from `backend/`. The image uses the highest error-correction level, so it
still scans when the paper is scuffed or partly covered.

**The three ways an employee can pass QR verification**, all validated
server-side against `COMPANY_CODE`:

1. **Scan the poster with their phone camera.** The link opens the attendance
   page with the code attached and step 1 completes on its own. If they are
   not signed in, the destination is remembered across the login screen so
   the scan is not lost.
2. **Scan from inside the app** — *Scan Company QR Code* opens the rear
   camera and reads the poster. It uses the browser's native `BarcodeDetector`
   where that exists (Android Chrome, macOS, ChromeOS) and the bundled
   [jsQR](frontend/js/vendor/jsQR.js) decoder everywhere else — which includes
   desktop Chrome on Windows and iOS Safari. jsQR ships inside the repo rather
   than loading from a CDN, so scanning never depends on a third-party host.
3. **Show the code on screen** — the fallback when no poster is nearby, which
   is what the original version of this project did.

A wrong or foreign QR code is rejected with a clear message.

---

## Configuration

### `backend/.env`

| Variable                          | Default                 | Meaning                                            |
| --------------------------------- | ----------------------- | -------------------------------------------------- |
| `SECRET_KEY`                      | `dev-secret-change-me`  | Signs auth tokens — **change in production**        |
| `TOKEN_TTL_HOURS`                 | `12`                    | How long a login stays valid                        |
| `DATABASE_URL`                    | *(empty)*               | Postgres URL; empty means SQLite                    |
| `SQLITE_PATH`                     | `database/attendance.db`| SQLite file location                                |
| `CORS_ORIGINS`                    | `*`                     | Allowed frontend origins (set your Vercel URL)      |
| `FRONTEND_URL`                    | `http://localhost:5000` | Encoded into the company QR code                    |
| `COMPANY_CODE`                    | `AAS-COMPANY-QR-001`    | Permanent code inside the QR — keep it stable       |
| `SERVE_FRONTEND`                  | `true`                  | Serve `frontend/` from Flask (`false` on Render)    |
| `LATE_AFTER_HOUR` / `..._MINUTE`  | `9` / `0`               | After this time attendance counts as *Late*         |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | `admin` / `12345`     | Account seeded on first run                         |

### `frontend/.env` and `frontend/js/config.js`

A static site has no server to read environment variables, so the browser
reads `js/config.js`. `frontend/.env` documents the same value for your own
records — set the API URL in **both**:

```js
// frontend/js/config.js
API_BASE_URL: "https://attendance-api.onrender.com"
```

Leave it empty when the backend also serves the pages (local `python app.py`
or Docker Compose).

---

## Deployment

### Backend → Render (free)

1. Push this repository to GitHub.
2. In Render: **New → Blueprint**, select the repo. It reads
   `backend/render.yaml`. (Or **New → Web Service** with
   *Root Directory* `backend`, build `pip install -r requirements.txt`,
   start `gunicorn --bind 0.0.0.0:$PORT wsgi:app`.)
3. Set the environment variables — at minimum `SECRET_KEY` (Render can
   generate it), `ADMIN_PASSWORD`, `SERVE_FRONTEND=false`, and, once the
   frontend is live, `CORS_ORIGINS` and `FRONTEND_URL` set to your Vercel URL.
4. Copy the service URL, e.g. `https://attendance-api.onrender.com`.

**Two things to know about the free plan:**

* The service sleeps after ~15 minutes idle; the first request afterwards
  takes up to a minute. The login page shows a "waking up the server" hint.
  Optional fix: create a free job at [cron-job.org](https://cron-job.org) that
  requests `https://<your-api>/api/health` every 10 minutes.
* The disk is disposable, so the SQLite file is **wiped on every redeploy or
  restart**. Use a free PostgreSQL database instead — see below.

### Database → Supabase or Neon (free, does not expire)

Render's *own* free Postgres expires after 30 days, so avoid it if you want a
deployment you can leave alone. These free tiers do not expire:

* **[Supabase](https://supabase.com)** — *Project Settings → Database →
  Connection string → URI*
* **[Neon](https://neon.tech)** — *Dashboard → Connection string*

Copy the `postgresql://...` URL into the `DATABASE_URL` environment variable
on Render and redeploy. The backend detects it automatically, creates its
tables on boot and seeds the admin account — no code change, no migration
step. Attendance then survives every redeploy, restart and sleep cycle.

### Frontend → Vercel (free)

1. In Vercel: **Add New → Project**, import the same repository.
2. Set **Root Directory** to `frontend`. Framework preset: **Other**.
   No build command, no output directory — it is plain static HTML.
3. Before or right after deploying, set `API_BASE_URL` in
   `frontend/js/config.js` to your Render URL and push. (Forget this and every
   page shows a "Setup needed" banner telling you exactly this.)
4. Add the resulting Vercel URL to `CORS_ORIGINS` and `FRONTEND_URL` on
   Render, then redeploy the backend so the QR code points at the live site.
5. Print the poster from *Admin Dashboard → QR Poster*.

Vercel's free plan has no expiry, and the `*.vercel.app` domain stays yours as
long as the project exists — which is what keeps the printed QR code valid.

### Deployment checklist

| Step | Where  | What                                                            |
| ---- | ------ | --------------------------------------------------------------- |
| 1    | GitHub | Push the repo (`.env` files stay local — they are git-ignored)   |
| 2    | Neon / Supabase | Create a free database, copy the connection URL         |
| 3    | Render | Blueprint from `backend/render.yaml`; set `DATABASE_URL`, `ADMIN_PASSWORD` |
| 4    | Vercel | Import repo, Root Directory `frontend`, framework *Other*        |
| 5    | Code   | `API_BASE_URL` in `frontend/js/config.js` → Render URL, push     |
| 6    | Render | `FRONTEND_URL` + `CORS_ORIGINS` → Vercel URL, redeploy           |
| 7    | App    | Sign in as admin, open *QR Poster*, print it                      |

### Docker

Run both halves in containers (backend on `:5000`, frontend on `:8080` with
nginx proxying `/api` to the backend, so no CORS setup is needed):

```bash
cp backend/.env.example backend/.env   # .env is git-ignored, so create it first
docker compose up --build
# open http://localhost:8080
```

Backend only:

```bash
docker build -t attendance-api ./backend
docker run -p 5000:5000 --env-file backend/.env attendance-api
```

---

## Maintenance scripts

Run these from the `backend/` folder:

```bash
python -m app.scripts.init_db                 # create tables + seed admin
python -m app.scripts.add_employee jdoe pass123 "Jane Doe" "IT" employee
python -m app.scripts.clear_attendance        # wipe attendance, keep employees
python -m app.scripts.generate_qr poster.png  # printable company QR code
```

---

## Tech stack

Flask 3 · Gunicorn · SQLite / PostgreSQL · openpyxl · ReportLab · qrcode —
vanilla HTML, CSS and JavaScript on the frontend, with Font Awesome and
Google Fonts.
