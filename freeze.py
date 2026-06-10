"""
Freeze the Flask app into static HTML files so the exact same Jinja-rendered
pages can be served as a static bundle (e.g. on Vercel's static hosting),
while remaining a fully runnable Flask app via `python app.py`.

Usage: python freeze.py <output_dir>
"""
import os, sys, shutil, re

_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BASE)
from app import app, GYM

OUT = sys.argv[1] if len(sys.argv) > 1 else "build"

# route -> output file
PAGES = {
    "/": "index.html",
    "/about": "about.html",
    "/programs": "programs.html",
    "/memberships": "memberships.html",
    "/branches": "branches.html",
    "/gallery": "gallery.html",
    "/contact": "contact.html",
}

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)

    # copy static assets, preserving the /static/... url prefix used in templates
    shutil.copytree(os.path.join(_BASE, "static"), os.path.join(OUT, "static"))

    client = app.test_client()
    for route, filename in PAGES.items():
        resp = client.get(route)
        html = resp.get_data(as_text=True)
        # rewrite internal route links to static .html files so they work without a server
        for r, fn in PAGES.items():
            if r == "/":
                html = html.replace('href="/"', 'href="index.html"')
            else:
                html = html.replace(f'href="{r}"', f'href="{fn}"')
        # contact form has no backend when static -> point form action straight to WhatsApp via JS
        out_path = os.path.join(OUT, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print("froze", route, "->", out_path)

if __name__ == "__main__":
    main()
