"""
AquaVerse Water Park & Resort - Flask backend.
Serves all site pages and exposes lightweight JSON APIs for the
booking, membership, and event inquiry UIs.
"""
import io
import os
from datetime import datetime
from urllib.parse import quote

import qrcode
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)
# WSGI servers (PythonAnywhere, gunicorn, etc.) look for `application`.
application = app

# ---------------------------------------------------------------------------
# Shared data (kept in-module so the demo runs with no database)
# ---------------------------------------------------------------------------
SITE = {
    "name": "AquaVerse",
    "tagline": "Water Park & Family Resort",
    "phone": "+1 (555) 010-2025",
    "whatsapp": "15550102025",
    "email": "hello@aquaverse.com",
    "address": "1200 Splash Boulevard, Sunshine Bay, CA 90210",
    "hours": "Mon–Sun · 9:00 AM – 8:00 PM",
}

# UPI merchant details used for deep links + QR codes.
# Override these in production via environment variables (e.g. on
# PythonAnywhere's Web tab → "Environment variables", or a .env loader).
UPI = {
    "vpa": os.environ.get("UPI_VPA", "aquaverse@okicici"),   # payee VPA (UPI ID)
    "name": os.environ.get("UPI_NAME", "AquaVerse Water Park"),  # payee display name
}


def build_upi_link(amount=0, note="AquaVerse Tickets", ref=None):
    """Return a spec-compliant upi://pay deep link."""
    params = [
        f"pa={UPI['vpa']}",
        f"pn={quote(UPI['name'])}",
        "cu=INR",
        f"tn={quote(note)}",
    ]
    try:
        amt = float(amount)
    except (TypeError, ValueError):
        amt = 0
    if amt > 0:
        params.insert(2, f"am={amt:.2f}")
    if ref:
        params.append(f"tr={quote(str(ref))}")
    return "upi://pay?" + "&".join(params)

TICKET_PRICES = {
    "adult": 799,
    "kid": 499,
    "family": 2499,     # 2 adults + 2 kids
    "senior": 599,
    "school": 349,      # per student, min 20
}

ATTRACTIONS = [
    {
        "name": "Giant Water Slides",
        "img": "https://images.unsplash.com/photo-1530549387789-4c1017266635?auto=format&fit=crop&w=900&q=80",
        "desc": "Plunge down six towering multi-lane slides with twists, drops and tunnels.",
        "safety": "Minimum height 48\". Keep arms crossed. One rider per lane.",
        "tag": "Thrill",
    },
    {
        "name": "Wave Pool",
        "img": "https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?auto=format&fit=crop&w=900&q=80",
        "desc": "Ride rolling ocean-style waves up to 4 ft in our giant beach-entry pool.",
        "safety": "Strong swimmers only past the 4 ft marker. Lifeguards on duty.",
        "tag": "Family",
    },
    {
        "name": "Kids Pool",
        "img": "https://images.unsplash.com/photo-1535392432937-a27c36ec07b5?auto=format&fit=crop&w=900&q=80",
        "desc": "A shallow splash paradise with mini slides and fountains for little ones.",
        "safety": "Children must be supervised by an adult at all times.",
        "tag": "Kids",
    },
    {
        "name": "Rain Dance Zone",
        "img": "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?auto=format&fit=crop&w=900&q=80",
        "desc": "Dance under a tropical rain shower with live DJ beats all day long.",
        "safety": "Non-slip flooring. Follow staff instructions during shows.",
        "tag": "Party",
    },
    {
        "name": "Lazy River",
        "img": "https://images.unsplash.com/photo-1602002418082-a4443e081dd1?auto=format&fit=crop&w=900&q=80",
        "desc": "Float gently along a 400m winding river past waterfalls and gardens.",
        "safety": "Tubes provided. Children under 8 must share with an adult.",
        "tag": "Relax",
    },
    {
        "name": "Deep Swimming Pool",
        "img": "https://images.unsplash.com/photo-1576610616656-d3aa5d1f4534?auto=format&fit=crop&w=900&q=80",
        "desc": "Olympic-grade 2m deep pool for lap swimming, training and diving.",
        "safety": "Certified swimmers only. Diving from marked boards.",
        "tag": "Sport",
    },
    {
        "name": "Family Pool",
        "img": "https://images.unsplash.com/photo-1572331165267-854da2b10ccc?auto=format&fit=crop&w=900&q=80",
        "desc": "A warm, spacious pool designed for the whole family to play together.",
        "safety": "Depth 1.2m. Floatation aids available at the kiosk.",
        "tag": "Family",
    },
    {
        "name": "Waterfall Pool",
        "img": "https://images.unsplash.com/photo-1551918120-9739cb430c6d?auto=format&fit=crop&w=900&q=80",
        "desc": "Relax beneath cascading waterfalls in a lush tropical setting.",
        "safety": "Mind slippery rocks. No climbing the waterfall structure.",
        "tag": "Relax",
    },
    {
        "name": "Splash Zone",
        "img": "https://images.unsplash.com/photo-1519315901367-f34ff9154487?auto=format&fit=crop&w=900&q=80",
        "desc": "Interactive water playground with tipping buckets and water cannons.",
        "safety": "Watch for the giant tipping bucket alarm. Adult supervision advised.",
        "tag": "Kids",
    },
]

MEMBERSHIPS = [
    {"name": "Splash", "price": 799, "period": "month", "perks": [
        "Unlimited weekday entry", "10% food court discount", "Free locker"]},
    {"name": "Wave", "price": 1499, "period": "month", "featured": True, "perks": [
        "Unlimited entry all week", "20% food court discount",
        "Free locker + towel", "2 guest passes / month"]},
    {"name": "Ocean", "price": 2999, "period": "month", "perks": [
        "All-access incl. events", "30% food court discount",
        "Private cabana 1x / month", "Free swim classes", "5 guest passes / month"]},
]

GALLERY = [
    ("https://images.unsplash.com/photo-1530549387789-4c1017266635?auto=format&fit=crop&w=800&q=80", "Slides"),
    ("https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?auto=format&fit=crop&w=800&q=80", "Pools"),
    ("https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?auto=format&fit=crop&w=800&q=80", "Events"),
    ("https://images.unsplash.com/photo-1572331165267-854da2b10ccc?auto=format&fit=crop&w=800&q=80", "Family"),
    ("https://images.unsplash.com/photo-1519315901367-f34ff9154487?auto=format&fit=crop&w=800&q=80", "Family"),
    ("https://images.unsplash.com/photo-1502780402662-acc01917738e?auto=format&fit=crop&w=800&q=80", "Night Party"),
    ("https://images.unsplash.com/photo-1551918120-9739cb430c6d?auto=format&fit=crop&w=800&q=80", "Pools"),
    ("https://images.unsplash.com/photo-1535392432937-a27c36ec07b5?auto=format&fit=crop&w=800&q=80", "Family"),
    ("https://images.unsplash.com/photo-1602002418082-a4443e081dd1?auto=format&fit=crop&w=800&q=80", "Slides"),
    ("https://images.unsplash.com/photo-1571902943202-507ec2618e8f?auto=format&fit=crop&w=800&q=80", "Events"),
    ("https://images.unsplash.com/photo-1576610616656-d3aa5d1f4534?auto=format&fit=crop&w=800&q=80", "Pools"),
    ("https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?auto=format&fit=crop&w=800&q=80", "Night Party"),
]

REVIEWS = [
    {"name": "Sarah M.", "role": "Mom of two", "stars": 5,
     "text": "The kids never wanted to leave! Spotlessly clean and the lifeguards were everywhere. Best family day out we've had all summer."},
    {"name": "James T.", "role": "Tourist", "stars": 5,
     "text": "The wave pool and giant slides are world-class. Booking online with the ticket calculator was so easy. Highly recommend!"},
    {"name": "Priya K.", "role": "School coordinator", "stars": 5,
     "text": "Organised a trip for 60 students. The team handled everything safely and the school package pricing was fantastic value."},
    {"name": "Diego R.", "role": "Member", "stars": 4,
     "text": "Been an Ocean member for a year. The private cabanas and night pool parties are unreal. Worth every penny."},
]

EVENTS = [
    {"name": "Birthday Parties", "icon": "🎂", "desc": "Cabanas, cake, dedicated host and splash-tastic fun for all ages."},
    {"name": "Corporate Events", "icon": "💼", "desc": "Team building, private zones and catering for groups up to 300."},
    {"name": "School Trips", "icon": "🎒", "desc": "Educational + fun packages with supervised zones and meals."},
    {"name": "Pool Parties", "icon": "🏊", "desc": "Private pool hire with music, lights and lifeguards included."},
    {"name": "DJ Nights", "icon": "🎧", "desc": "Weekend poolside DJ sets, neon lights and dance floors."},
    {"name": "Rain Dance Events", "icon": "🌧️", "desc": "Themed rain dance festivals with live performers and food stalls."},
]

FAQS = [
    ("Do I need to book tickets in advance?",
     "We recommend booking online to skip the queue and lock in discounts. Limited pool slots are available, so weekends sell out fast."),
    ("Are outside food and drinks allowed?",
     "Outside food isn't permitted, but our food court offers everything from healthy bites to indulgent treats."),
    ("Is the water regularly tested?",
     "Yes. Our pools use advanced filtration and water is tested every 2 hours to exceed health-authority standards."),
    ("Do you provide lockers and changing rooms?",
     "Absolutely. Secure digital lockers, spacious changing rooms and hot showers are available across the park."),
    ("What is the dress code?",
     "Proper swimwear is required in all pools. Cotton clothing is not permitted in the water for hygiene reasons."),
    ("Is parking available?",
     "Yes, 800+ free parking spaces including accessible and EV-charging bays."),
]


@app.context_processor
def inject_globals():
    return {"site": SITE, "upi": UPI, "year": datetime.now().year}


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template(
        "index.html", attractions=ATTRACTIONS[:6], memberships=MEMBERSHIPS,
        gallery=GALLERY[:8], reviews=REVIEWS, prices=TICKET_PRICES, faqs=FAQS,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/attractions")
def attractions():
    return render_template("attractions.html", attractions=ATTRACTIONS)


@app.route("/booking")
def booking():
    return render_template("booking.html", prices=TICKET_PRICES)


@app.route("/pool")
def pool():
    return render_template("pool.html", memberships=MEMBERSHIPS)


@app.route("/gallery")
def gallery():
    return render_template("gallery.html", gallery=GALLERY)


@app.route("/events")
def events():
    return render_template("events.html", events=EVENTS)


@app.route("/contact")
def contact():
    return render_template("contact.html", faqs=FAQS)


# ---------------------------------------------------------------------------
# Demo JSON APIs (no persistence – returns a friendly confirmation)
# ---------------------------------------------------------------------------
@app.route("/api/book", methods=["POST"])
def api_book():
    data = request.get_json(silent=True) or {}
    adults = int(data.get("adults", 0) or 0)
    kids = int(data.get("kids", 0) or 0)
    method = (data.get("payment_method") or "upi").upper()
    total = adults * TICKET_PRICES["adult"] + kids * TICKET_PRICES["kid"]
    ref = "AQ" + datetime.now().strftime("%y%m%d%H%M%S")
    return jsonify({
        "ok": True,
        "reference": ref,
        "total": total,
        "method": method,
        "upi_link": build_upi_link(total, ref=ref),
        "message": f"Booking confirmed for {adults} adult(s) and {kids} kid(s) via {method}!",
    })


@app.route("/api/upi-qr")
def upi_qr():
    """Return a scannable PNG QR code encoding a UPI deep link."""
    amount = request.args.get("amount", "0")
    ref = request.args.get("ref")
    link = build_upi_link(amount, ref=ref)
    img = qrcode.make(link, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png", max_age=0)


@app.route("/api/upi-link")
def upi_link():
    """Return the raw UPI deep link for the given amount (used by the UI)."""
    amount = request.args.get("amount", "0")
    ref = request.args.get("ref")
    return jsonify({"link": build_upi_link(amount, ref=ref), "vpa": UPI["vpa"]})


@app.route("/api/inquiry", methods=["POST"])
def api_inquiry():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "guest").split(" ")[0]
    return jsonify({"ok": True, "message": f"Thanks {name}! Our team will reach out within 24 hours."})


@app.route("/api/membership", methods=["POST"])
def api_membership():
    data = request.get_json(silent=True) or {}
    plan = data.get("plan", "Splash")
    return jsonify({"ok": True, "message": f"Welcome aboard! Your {plan} membership request is received."})


if __name__ == "__main__":
    # Local development server only. Production (PythonAnywhere/gunicorn)
    # imports the `application` object above and never runs this block.
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
