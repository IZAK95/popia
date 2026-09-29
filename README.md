# POPIA Compliance Manager

A self-hosted web app that acts as your business's **POPIA compliance framework**. It explains South Africa's
Protection of Personal Information Act in plain language and gives you the tools to comply with it:

| Area | What the app gives you |
| --- | --- |
| **Compliance checklist** | 47 requirements from POPIA, the POPIA Regulations (as amended April 2025), the 2026 Health Information Regulations and PAIA. Each item says why it matters, how to do it and which section applies, and stores your evidence. |
| **Dashboard** | Progress score, next steps, overdue requests, breaches that still need reporting, and the PAIA report window. |
| **Processing register** (s17) | What personal information you process, why, the lawful ground, special information, recipients, retention and security. Comes with draft entries for payroll/HR, recruitment and customers & suppliers. |
| **Operators register** (s20–21, s72) | Service providers, their written agreements and the legal basis for storing data outside South Africa. |
| **Retention schedule** (s14) | South African legal minimum periods (BCEA, Tax Administration Act, Companies Act, UIF, COIDA and others) plus sensible policy defaults. |
| **Risk register** | Your personal information impact assessment (reg. 4(1)(b)) with a heat map. |
| **Requests** (s23–25, s11(3), PAIA) | Log access, correction, deletion and objection requests. 30-day deadlines are calculated for you and step-by-step guidance is included. |
| **Incidents** (s22) | A guided breach workflow: contain, assess, report to the Regulator's eServices portal, notify affected people, learn. |
| **PAIA annual report** (s83(4)) | Works out the figures you need to submit between 1 April and 30 June. |
| **Documents** | POPIA policy, privacy notice, employee notice and consents, **PAIA manual**, Information Officer appointment, breach plan and letter, operator agreement, retention schedule, record of processing, and request response letters. Filled in from your data. Print to PDF or download for Word. |
| **Learn** | Ten short lessons: POPIA in plain language. They also work as a staff training script. |
| **Evidence** | Training log, recurring compliance tasks, an audit log of every change, JSON export and daily backups. |

> This app gives practical guidance based on research done in September 2026. It is not legal advice. Have an
> attorney review your final PAIA manual and notices if you can, and re-check the Information Regulator's
> website every year. See [`docs/RESEARCH.md`](docs/RESEARCH.md) for the research behind the app.

## Security

The app stores personal information, so it is locked down:

- You sign in with a password and then a code from an authenticator app (TOTP two-factor authentication). Every login needs both.
- After 5 failed logins, that username and IP address are locked out for 1 hour (django-axes).
- Traffic is HTTPS only with HSTS. Cookies are secure and HttpOnly, sessions last 8 hours, and a strict Content-Security-Policy is set. Pages can't be embedded in other sites and search engines are told not to index them.
- Every change is written to an audit log that can't be edited.
- A backup is taken automatically every day and kept for 30 days.

---

## Choose where to run it

| | **Your own computer** | **Hetzner server** |
| --- | --- | --- |
| Reach it from | Only that computer | Anywhere (phone, laptop) |
| Data location | South Africa, so no cross-border transfer | Germany or Finland: a POPIA s72 transfer, allowed but it must be documented |
| Your responsibilities | Turn on disk encryption, back up the `backups` folder | Keep the server updated, accept Hetzner's DPA |
| Setup effort | ~10 minutes | ~30 minutes |

For a single user, **running it on your own computer is simpler and lower-risk**. Your published documents (PAIA
manual, privacy notice) go on your public website either way. The app itself never needs to be public.

### Option A: your own computer (Windows, Mac or Linux)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and turn on **full-disk encryption**
   (BitLocker on Windows, FileVault on Mac).
2. Download this repository and open a terminal in its folder.
3. Create your settings file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set:
   - `SECRET_KEY`: a long random string. Run `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`, or just type about 50 random characters.
   - `ADMIN_USERNAME` and `ADMIN_PASSWORD`: your login. The password must be at least 12 characters.
   - You can ignore `DOMAIN`.
4. Start it:
   ```bash
   docker compose -f docker-compose.local.yml up -d --build
   ```
5. Open <http://localhost:8000>, sign in and scan the QR code with an authenticator app.
6. Remove `ADMIN_PASSWORD` from `.env`.
7. In the app, delete the "Hetzner Online GmbH" entry from **Operators**, because you're not using Hetzner.

Your data lives in `./data` and daily backups in `./backups`. Copy `./backups` regularly to an encrypted external
drive or an encrypted cloud folder.

### Option B: Hetzner Cloud server

1. **Create the server** in the [Hetzner Console](https://console.hetzner.cloud):
   - Location: **Falkenstein, Nuremberg (Germany) or Helsinki (Finland)**, both of which are EU/GDPR.
   - Image: **Ubuntu 24.04**. A CX22 or larger is plenty.
   - Add your SSH key. Tick **Backups** if you want server-level snapshots too.
   - Create a **Firewall** that allows inbound TCP 22 (ideally only from your own IP address), 80 and 443, and nothing else.
2. **Accept Hetzner's Data Processing Agreement.** In the Hetzner Console, go to your account's data protection / DPA
   section and file a copy. This covers POPIA s21 and s72, and the app's Operators register already lists Hetzner.
3. **Point a domain** at the server. Create a DNS A record such as `popia.yourcompany.co.za` pointing to the server's IPv4 address.
4. **Prepare the server.** SSH in as root, then:
   ```bash
   apt update && apt -y upgrade
   apt -y install unattended-upgrades git
   dpkg-reconfigure -plow unattended-upgrades        # automatic security updates
   curl -fsSL https://get.docker.com | sh            # install Docker
   ```
5. **Install the app:**
   ```bash
   git clone <this-repository-url> /opt/popia && cd /opt/popia
   cp .env.example .env && nano .env
   ```
   Set `DOMAIN`, `SECRET_KEY`, `ADMIN_USERNAME` and `ADMIN_PASSWORD`.
6. **Start it:**
   ```bash
   docker compose up -d --build
   ```
   Caddy obtains a Let's Encrypt certificate automatically. Open `https://<your domain>`, sign in and set up
   two-factor authentication. Then remove `ADMIN_PASSWORD` from `.env`.

**Off-site backups (recommended).** Daily backups are stored in the `app-backups` Docker volume and can be downloaded
from **Export & backup** in the app. For an automatic off-site copy, use [restic](https://restic.net/), which
encrypts backups, to send `/var/lib/docker/volumes/popia_app-backups/_data` to a
[Hetzner Storage Box](https://www.hetzner.com/storage/storage-box) (also in the EU).

### Everyday commands

```bash
docker compose logs -f app                                # view logs
docker compose pull && docker compose up -d --build       # update after `git pull`
docker compose exec app python manage.py reset_2fa <user> # lost your phone: re-enrol 2FA at next login
docker compose exec app python manage.py changepassword <user>
docker compose exec app python manage.py backup_db        # extra backup now
```
(Add `-f docker-compose.local.yml` for the local setup.)

**Restore a backup:** stop the app, then `gunzip` the chosen `popia-*.sqlite3.gz` and replace `popia.sqlite3` in the
data volume or folder with it. Start the app again.

---

## Development

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export DEBUG=1
python manage.py migrate && python manage.py seed_popia && python manage.py createsuperuser
python manage.py runserver
python manage.py test
```

Built with Django 5.2 LTS, SQLite (WAL mode), django-otp, django-axes, WhiteNoise, Gunicorn and Caddy. There are no
JavaScript frameworks or external CDNs.

### Where things live

- `compliance/knowledge.py`: checklist content, retention periods, example registers and recurring tasks, with sources.
- `compliance/templates/compliance/documents/`: the generated documents.
- `compliance/templates/compliance/learn/`: the plain-language lessons.
- `compliance/seed.py`: loads the content. The checklist text is refreshed on every start (your status and evidence are kept), while example entries are only added once.
