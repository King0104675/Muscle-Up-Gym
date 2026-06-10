"""
Muscle Up Gym (Salt Lake, Kolkata) — Flask Website
===================================================
A production multi-page website for Muscle Up Gym, built with Python Flask,
Jinja2 templates and HTML/CSS. Includes Home, About, Programs, Memberships,
Branches and Contact pages, plus WhatsApp integration for enquiry and contact.

All business data below (name, addresses, phone/WhatsApp numbers, email,
opening hours, programs and amenities) is sourced from the gym's public
listings. Pricing is intentionally NOT shown because it is not published
publicly — membership enquiries are routed to WhatsApp instead.

Run locally:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""
from flask import Flask, render_template, request, redirect, url_for
import urllib.parse
import os

_BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(_BASE, "templates"),
    static_folder=os.path.join(_BASE, "static"),
)
# Secret key is read from the environment in production. The fallback is for
# local development only and is NOT a real/confidential secret.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-not-secret")

# ---------------------------------------------------------------------------
# Verified business information
# ---------------------------------------------------------------------------
GYM = {
    "name": "Muscle Up Gym",
    "tagline": "Salt Lake's home of strength, fitness and community.",
    "phone_primary_display": "+91 86177 77413",
    "phone_primary_tel": "+918617777413",
    "phone_secondary_display": "+91 78941 96766",
    "phone_secondary_tel": "+917894196766",
    # WhatsApp number in international format WITHOUT '+' or spaces
    "whatsapp": "918617777413",
    "email": "muscleupgymkolkata@gmail.com",
    "city": "Salt Lake City (Bidhannagar), Kolkata",
    "hours_line": "Open Monday – Sunday, 6:00 AM – 10:00 PM",
    "hours": [
        ("Monday – Saturday", "6:00 AM – 10:00 PM"),
        ("Sunday", "6:00 AM – 10:00 PM"),
    ],
    "socials": {
        "website": "https://muscleupgymkolkata.in",
    },
}

# Two real branches
BRANCHES = [
    {
        "name": "Sector 3 Branch",
        "address": "IB-20, IB Block, near IB Block Park, Salt Lake Bypass, Sector 3, Bidhannagar, Kolkata, West Bengal 700106",
        "landmark": "Near IB Block Park",
        "maps": "https://www.google.com/maps/search/?api=1&query=Muscle+Up+Gym+IB-20+IB+Block+Sector+3+Salt+Lake+Kolkata",
    },
    {
        "name": "Sector 1 Branch",
        "address": "BF-239, near the Swimming Pool, Salt Lake City Sector 1, Bidhannagar, Kolkata, West Bengal",
        "landmark": "Near the Swimming Pool",
        "maps": "https://www.google.com/maps/search/?api=1&query=Muscle+Up+Gym+Sector+1+Salt+Lake+Kolkata",
    },
]

# Programs the gym actually offers (per their public listings)
PROGRAMS = [
    {
        "title": "Weight-Loss Plans",
        "short": "Structured fat-loss programming combining cardio and resistance training.",
        "desc": "Guided weight-loss plans that pair smart training with progress check-ins to help you shed fat sustainably and keep it off.",
        "level": "All Levels",
    },
    {
        "title": "Muscle-Gain Plans",
        "short": "Progressive hypertrophy programs to build size and lean mass.",
        "desc": "Muscle-gain plans built around progressive overload, structured splits and recovery guidance to help you add quality lean mass.",
        "level": "All Levels",
    },
    {
        "title": "Bodybuilding",
        "short": "Dedicated bodybuilding training for shape, symmetry and definition.",
        "desc": "Focused bodybuilding programming for members chasing aesthetics, conditioning and stage-ready physiques, guided by experienced trainers.",
        "level": "Intermediate +",
    },
    {
        "title": "HIIT Sessions",
        "short": "High-intensity interval training to torch calories and build conditioning.",
        "desc": "Fast, efficient HIIT sessions that spike your metabolism, improve cardiovascular fitness and fit into a busy schedule.",
        "level": "All Levels",
    },
    {
        "title": "CrossFit-Style Plans",
        "short": "Functional, varied, high-intensity training for all-round fitness.",
        "desc": "Constantly varied functional movements performed at intensity to build strength, stamina and athleticism.",
        "level": "All Levels",
    },
    {
        "title": "Yoga Classes",
        "short": "Improve flexibility, mobility and recovery with guided yoga.",
        "desc": "Yoga classes to balance your strength training — building flexibility, mobility and calm while supporting recovery.",
        "level": "Beginner",
    },
]

# Personal training is offered, but no public pricing — routed to enquiry.
PERSONAL_TRAINING = {
    "title": "Personal Training",
    "desc": "One-on-one coaching with the gym's certified trainers — personalised programming, technique coaching and accountability tailored to your goals.",
}

# Amenities cited across the gym's listings (verified, not invented)
AMENITIES = [
    "Air-conditioned floor",
    "Cardio machines & treadmills",
    "Free weights & dumbbells",
    "Strength training equipment",
    "Certified, supportive trainers",
    "Lockers",
    "Parking",
    "First-aid",
    "Wi-Fi",
    "Free trial sessions",
]


# Gallery images — license-free photographs (Pexels License, free for
# commercial use, no attribution required) chosen to represent the gym's
# actual facilities: strength equipment, free weights, cardio, HIIT, yoga
# and personal training.
GALLERY = [
    {"img": "g1.jpg", "caption": "Strength & weight-training floor", "span": "wide", "layout": "area-a", "category": "Strength"},
    {"img": "g4.jpg", "caption": "Barbell & free-weight area", "span": "tall", "layout": "area-b", "category": "Free Weights"},
    {"img": "g3.jpg", "caption": "Cardio zone & treadmills", "span": "", "layout": "area-c", "category": "Cardio"},
    {"img": "g2.jpg", "caption": "Dumbbell & free-weight rack", "span": "", "layout": "area-d", "category": "Free Weights"},
    {"img": "g7.jpg", "caption": "Cable & machine strength training", "span": "tall", "layout": "area-e", "category": "Strength"},
    {"img": "g6.jpg", "caption": "HIIT & functional training", "span": "", "layout": "area-f", "category": "HIIT"},
    {"img": "g8.jpg", "caption": "Personal training & coaching", "span": "wide", "layout": "area-g", "category": "Personal Training"},
    {"img": "g5.jpg", "caption": "Yoga & mobility classes", "span": "", "layout": "area-h", "category": "Yoga"},
]

GALLERY_CATEGORIES = [
    "Strength",
    "Free Weights",
    "Cardio",
    "HIIT",
    "Yoga",
    "Personal Training",
]


def wa_link(message: str) -> str:
    """Build a WhatsApp click-to-chat URL with a prefilled message."""
    return f"https://wa.me/{GYM['whatsapp']}?text=" + urllib.parse.quote(message)


@app.context_processor
def inject_globals():
    return {
        "gym": GYM,
        "branches": BRANCHES,
        "wa_general": wa_link(f"Hi {GYM['name']}! I'd like to know more about your gym and a free trial."),
        "current_year": 2025,
    }


@app.route("/")
def home():
    return render_template("index.html", programs=PROGRAMS[:4], amenities=AMENITIES, pt=PERSONAL_TRAINING)


@app.route("/about")
def about():
    return render_template("about.html", amenities=AMENITIES)


@app.route("/programs")
def programs():
    return render_template("programs.html", programs=PROGRAMS, pt=PERSONAL_TRAINING, wa_link=wa_link)


@app.route("/memberships")
def memberships():
    return render_template("memberships.html", amenities=AMENITIES, programs=PROGRAMS, wa_link=wa_link)


@app.route("/branches")
def branches_page():
    return render_template("branches.html", wa_link=wa_link)


@app.route("/gallery")
def gallery():
    return render_template("gallery.html", gallery=GALLERY, gallery_categories=GALLERY_CATEGORIES)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        interest = request.form.get("interest", "General Enquiry")
        message = request.form.get("message", "").strip()
        return redirect(
            f"https://wa.me/{GYM['whatsapp']}?text="
            + urllib.parse.quote(
                f"New enquiry for {GYM['name']}\nName: {name}\nPhone: {phone}\n"
                f"Interest: {interest}\nMessage: {message}"
            )
        )
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
