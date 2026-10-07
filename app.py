from flask import Flask, render_template, request
from pathlib import Path
import re
import numpy as np
from googletrans import Translator

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
translator = Translator()

def load_shlokas():
    with open(BASE_DIR / 'geetamain1.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return extract_full_shlokas(lines)

def clean_shloka(text):
    text = re.sub(r'॥\s*\d+\s*\d*॥', '', text)
    text = re.sub(r'\|\|', '', text)
    return text.strip()

def extract_lines_from_shlokas(shlokas):
    lines = []
    for shloka in shlokas:
        parts = shloka.strip().split('।')
        for line in parts:
            cleaned = clean_shloka(line)
            if cleaned:
                lines.append(cleaned)
    return lines

def extract_full_shlokas(shlokas):
    full_shlokas = []
    buffer = []
    for line in extract_lines_from_shlokas(shlokas):
        buffer.append(line)
        if len(buffer) == 2:
            full_shlokas.append(tuple(buffer))
            buffer = []
    return full_shlokas

def extract_chapter_and_verse(shloka):
    match = re.search(r'॥\s*(\d+)-(\d+)\s*॥', shloka)
    if match:
        return f"This Shlok Belongs to Chapter {match.group(1).strip()}, Verse {match.group(2).strip()}."
    return "Chapter and verse information not found."


def chapter_verse(shloka):
    match = re.search(r'॥\s*(\d+)-(\d+)\s*॥', shloka)
    
    if match:
        return np.array([int(match.group(1).strip()), int(match.group(2).strip())])
    
    return "Chapter and verse information not found."




def translate_shloka(shloka, target_language='en'):
    try:
        return translator.translate(shloka, dest=target_language).text
    except Exception as e:
        return f"Translation error: {e}"



shloka_pairs = load_shlokas()

@app.route("/Generate", methods=["GET", "POST"])
def home():
    matches = []
    seed_submitted = False

    if request.method == "POST":
        seed = request.form["seed"].strip()
        seed_submitted = True
        visited = set()

        for line1, line2 in shloka_pairs:
            full_shloka = f"{line1} ।\n{line2}"
            if full_shloka not in visited and (seed in line1 or seed in line2):
                visited.add(full_shloka)
                matches.append({
                    "shloka": full_shloka,
                    "chapter_verse": extract_chapter_and_verse(full_shloka),
                    "translation": translate_shloka(full_shloka)
                })

    return render_template("index.html", matches=matches, seed_submitted=seed_submitted)


@app.route('/')
def products():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    submitted = False

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if name and email and subject and message:
            submitted = True

    return render_template('contact.html', submitted=submitted)


@app.route('/verse')
def verse():
    return render_template("verse.html")

@app.route('/daily-wisdom')
def daily():
    return render_template("daily_thro.html")

@app.route('/chapter_verse', methods=["GET", "POST"])
def translate():
    matches = []
    seed_submitted = False

    if request.method == "POST":
        seed = request.form["seed"].strip()
        seed_submitted = True
        visited = set()

        for line1, line2 in shloka_pairs:
            full_shloka = f"{line1} ।\n{line2}"
            if full_shloka not in visited and (seed in line1 or seed in line2):
                visited.add(full_shloka)
                matches.append({
                    "shloka": full_shloka,
                    "verse_chapter":chapter_verse(full_shloka)

                }) 
    return render_template("translate.html", matches=matches, seed_submitted=seed_submitted)

if __name__ == "__main__":
    app.run(debug=True)
