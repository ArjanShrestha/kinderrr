# KINDER — KU Campus Connections(Tinder For Kathmandu University)

> **Not a dating app. A connection engine for Kathmandu University.**

KINDER is an open-source prototype that helps Kathmandu University students discover friends, project partners and communities beyond their own faculty.

## Why KINDER?

Students often stay inside their own faculty or friend group. KINDER uses an open-weight AI model to recommend cross-faculty connections and generate friendly conversation starters.

## AI

KINDER uses **Qwen2.5-1.5B-Instruct** locally through **Ollama**.

AI features:

- Cross-faculty connection matching
- Match explanations
- Personalized icebreakers

If Ollama is not running, KINDER uses a small deterministic fallback so the demo still works.

## Tech stack

- Python
- Flask
- HTML
- CSS
- JavaScript
- Qwen2.5-1.5B
- Ollama

## Run locally

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open:

`http://127.0.0.1:5000`

### Enable local AI

Install Ollama and run:

```bash
ollama pull qwen2.5:1.5b
ollama run qwen2.5:1.5b
```

Then click **Find my AI matches** or **Icebreaker** in KINDER.

## Open source

This project is released under the MIT License.

## Prototype note

KU Coins are a proposed prototype reward system and are **not an official Kathmandu University currency**. Community names and events shown in the demo are sample data unless officially confirmed.


## New demo feature: KINDER Memories + AI Rewind

Students can upload shared photos, associate them with a friend and month, then trigger an AI monthly rewind. Qwen2.5 turns memory captions into a short recap while the app creates a visual photo montage. The button simulates the month-end trigger for a live demo.

Photos are stored locally in `static/uploads/` for this prototype. User uploads are ignored by Git.
