# 🌊 AquaVerse — Water Park & Family Resort

A modern, vibrant, fully responsive website for a water park, swimming pool and family resort business, built with **Flask** + Jinja2 templates and vanilla HTML/CSS/JS.

## ✨ Features

- **8 pages**: Home, About, Attractions, Ticket Booking, Swimming Pool, Gallery, Events, Contact
- Fullscreen hero with image background and animated stats
- Sticky transparent navbar that solidifies on scroll + mobile slide-in menu
- Interactive **ticket calculator** with live totals and steppers
- Online **booking form** with date/time slots and a payment UI (demo, no real charges)
- **Membership registration** and **event inquiry** forms (async, JSON APIs)
- **Lightbox photo gallery** with category filtering
- Animated counters, scroll reveals, wave section dividers, glassmorphism cards
- Floating **WhatsApp** + **Call Now** buttons
- **Special offer popup**, "20% off" banner, "limited slots" alerts
- FAQ accordion, safety & hygiene, food court / lockers / parking, weather widget, map embed
- SEO meta tags, responsive down to mobile, fast-loading

## 🎨 Design
Aqua/ocean blue, cyan, white and sunshine yellow palette · playful **Baloo 2** headings with clean **Nunito** body text.

## 🚀 Run locally

```bash
pip install -r requirements.txt
python app.py
```

Then open <http://127.0.0.1:5000>.

## 📁 Structure

```
app.py                 # Flask routes + demo JSON APIs + content data
wsgi.py                # WSGI entry point (PythonAnywhere / gunicorn)
requirements.txt
templates/             # base.html + 8 page templates
static/css/style.css   # full design system
static/js/main.js      # navbar, calculator, lightbox, forms, counters, popup
```

> Images are loaded from Unsplash and forms/payment are demo-only (no data is stored or charged).

## ☁️ Deploy to PythonAnywhere

1. **Upload the code.** Either push this folder to GitHub and clone it in a
   PythonAnywhere **Bash console**, or upload it via the **Files** tab:

   ```bash
   git clone https://github.com/<you>/Water_Park.git
   ```

2. **Create a virtualenv and install deps** (in a Bash console):

   ```bash
   mkvirtualenv aquaverse --python=python3.10
   pip install -r Water_Park/requirements.txt
   ```

3. **Create the web app.** Web tab → *Add a new web app* → *Manual configuration*
   → choose the same Python version (3.10).

4. **Point it at your virtualenv.** In the Web tab, set
   *Virtualenv* to `/home/<you>/.virtualenvs/aquaverse`.

5. **Edit the WSGI file.** Click the *WSGI configuration file* link in the Web
   tab, delete everything, and paste:

   ```python
   import sys
   project_home = "/home/<you>/Water_Park"
   if project_home not in sys.path:
       sys.path.insert(0, project_home)
   from app import app as application
   ```

6. **Map static files (optional, faster).** Web tab → *Static files*:
   - URL `/static/`  →  Directory `/home/<you>/Water_Park/static`

7. **Set your real UPI ID (optional).** Web tab → *Environment variables*:
   - `UPI_VPA` = `yourname@okbank`
   - `UPI_NAME` = `Your Park Name`

8. **Reload** the web app from the Web tab. Your site is live at
   `https://<you>.pythonanywhere.com`.

> Notes: the page loads fonts/images from Google Fonts, Unsplash and an
> OpenStreetMap iframe — these are fetched by the visitor's browser, so they
> work on PythonAnywhere's free tier without whitelisting. UPI deep links and
> QR codes are generated server-side and need no external network access.

### Other hosts (gunicorn)

```bash
pip install gunicorn
gunicorn wsgi:application
```

