from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime
import json
import urllib.request
import uuid

app = Flask(__name__)

# -------------------------------------------------
# DEMO DATA
# -------------------------------------------------
ME = {
    "name": "Aarav Shrestha",
    "faculty": "Computer Engineering",
    "year": "4th Year",
    "interests": ["AI", "Hackathons", "Photography"],
    "avatar": "🧑‍💻",
    "coins": 120,
}

STUDENTS = [
    {"id": 1, "name": "Saanvi Rai", "faculty": "Management", "year": "3rd Year", "interests": ["Entrepreneurship", "Design", "Music"], "avatar": "🎨", "bio": "I love turning ideas into useful products and meeting creative people."},
    {"id": 2, "name": "Rohan Thapa", "faculty": "Civil Engineering", "year": "2nd Year", "interests": ["Robotics", "Football", "Photography"], "avatar": "📸", "bio": "Always up for a project, a football match, or a photo walk."},
    {"id": 3, "name": "Mina Gurung", "faculty": "Biotechnology", "year": "4th Year", "interests": ["Research", "Biotech", "Hiking"], "avatar": "🧬", "bio": "Interested in interdisciplinary research and outdoor adventures."},
    {"id": 4, "name": "Daniel Karki", "faculty": "International Student", "year": "2nd Year", "interests": ["AI", "Travel", "Basketball"], "avatar": "🌏", "bio": "I want to meet more people across KU and explore Nepal together."},
    {"id": 5, "name": "Prisha Joshi", "faculty": "Law", "year": "3rd Year", "interests": ["Debate", "Social Impact", "Books"], "avatar": "⚖️", "bio": "Interested in social innovation, debates and meaningful conversations."},
]

COMMUNITIES = [
    {"name": "KUCC", "icon": "⚡", "members": 186, "description": "Builders, developers and tech enthusiasts."},
    {"name": "Superteam KU", "icon": "🟣", "members": 94, "description": "Open source, Web3 and community-led innovation."},
    {"name": "KU Hackathon Hub", "icon": "🚀", "members": 231, "description": "Find teammates, build projects and compete."},
    {"name": "International Connect", "icon": "🌏", "members": 73, "description": "A welcoming space for international and local students."},
]

EVENTS = [
    {"date": "Oct 08", "title": "Hacktoberfest Demo Day", "time": "3:30 PM", "location": "KU Innovation Hub"},
    {"date": "Oct 10", "title": "KUCC Open Meetup", "time": "12:00 PM", "location": "Block 4"},
    {"date": "Oct 12", "title": "Interfaculty Football", "time": "4:00 PM", "location": "KU Ground"},
]

# -------------------------------------------------
# FILES / MEMORIES
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
MEMORY_FILE = BASE_DIR / "data" / "memories.json"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB per request


def load_memories():
    if not MEMORY_FILE.exists():
        return []
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_memories(memories):
    MEMORY_FILE.write_text(json.dumps(memories, indent=2), encoding="utf-8")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------------------------
# AI
# -------------------------------------------------
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"


def ask_ai(prompt):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
        return data["message"]["content"]


def fallback_matches():
    my_interests = {x.lower() for x in ME["interests"]}
    results = []
    for student in STUDENTS:
        shared = len(my_interests.intersection({x.lower() for x in student["interests"]}))
        score = min(97, 70 + shared * 10 + (10 if student["faculty"] != ME["faculty"] else 0))
        results.append({
            "id": student["id"],
            "score": score,
            "reason": "Different faculty + shared interests make this a great connection.",
        })
    return results


@app.get("/")
def home():
    return render_template(
        "index.html",
        me=ME,
        students=STUDENTS,
        communities=COMMUNITIES,
        events=EVENTS,
        memories=load_memories(),
    )


@app.post("/api/matches")
def matches():
    prompt = f"""
You are the AI inside KINDER, a university social connection app for Kathmandu University.
KINDER IS NOT A DATING APP. It helps students make friends, find project partners,
join communities and meet students from different faculties.

My profile:
Name: {ME['name']}
Faculty: {ME['faculty']}
Year: {ME['year']}
Interests: {', '.join(ME['interests'])}

Students:
{json.dumps(STUDENTS)}

Return ONLY a JSON array. For every student return id, score (0-100), and reason.
The reason must be one short sentence (maximum 18 words).
Prioritize shared interests, complementary skills, and cross-faculty discovery.
"""
    try:
        raw = ask_ai(prompt)
        start, end = raw.find("["), raw.rfind("]") + 1
        result = json.loads(raw[start:end])
        return jsonify({"source": "Qwen2.5", "matches": result})
    except Exception:
        return jsonify({"source": "Demo fallback", "matches": fallback_matches()})


@app.post("/api/icebreaker")
def icebreaker():
    data = request.get_json() or {}
    try:
        student_id = int(data.get("student_id"))
    except (TypeError, ValueError):
        return jsonify({"source": "error", "message": "Invalid student ID."}), 400

    student = next((s for s in STUDENTS if s["id"] == student_id), None)
    if not student:
        return jsonify({"source": "error", "message": "Student not found."}), 404

    prompt = f"""
You are KINDER AI, a friendly campus connection assistant for Kathmandu University.
KINDER is NOT a dating app. It helps students make friendships, find project collaborators,
and discover campus communities.

SENDER (the person writing the message):
Name: {ME['name']}
Faculty: {ME['faculty']}
Program: {ME['faculty']}
Year: {ME['year']}
Interests: {', '.join(ME['interests'])}

RECIPIENT (the person being contacted):
Name: {student['name']}
Faculty: {student['faculty']}
Year: {student['year']}
Interests: {', '.join(student['interests'])}

Write ONE short, natural message from the SENDER's perspective to the RECIPIENT.
Mention one shared or complementary interest. Never pretend to be the recipient.
Do not mention dating or romance. Return only the message.
"""
    try:
        message = ask_ai(prompt).strip().strip('"')
        return jsonify({"source": "Qwen2.5", "message": message})
    except Exception:
        return jsonify({
            "source": "Demo fallback",
            "message": f"Hey {student['name'].split()[0]}! I noticed you're interested in {student['interests'][0]}. I'm also into {ME['interests'][0]}. Want to connect?"
        })


# -------------------------------------------------
# SHARED MEMORIES
# -------------------------------------------------
@app.post("/api/memories")
def add_memory():
    photo = request.files.get("photo")
    friend = request.form.get("friend", "KINDER Friend")
    caption = request.form.get("caption", "A KINDER memory")
    month = request.form.get("month") or datetime.now().strftime("%Y-%m")

    if not photo or not photo.filename:
        return jsonify({"error": "Please choose a photo."}), 400
    if not allowed_file(photo.filename):
        return jsonify({"error": "Please upload PNG, JPG, JPEG, GIF or WEBP."}), 400

    safe_name = secure_filename(photo.filename)
    unique_name = f"{uuid.uuid4().hex[:10]}_{safe_name}"
    photo.save(UPLOAD_DIR / unique_name)

    memories = load_memories()
    memory = {
        "id": uuid.uuid4().hex,
        "friend": friend,
        "caption": caption.strip() or "A KINDER memory",
        "month": month,
        "filename": unique_name,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    memories.insert(0, memory)
    save_memories(memories)
    return jsonify({"memory": memory})


@app.get("/api/memories")
def get_memories():
    month = request.args.get("month")
    memories = load_memories()
    if month:
        memories = [m for m in memories if m["month"] == month]
    return jsonify({"memories": memories})


@app.post("/api/rewind")
def rewind():
    data = request.get_json() or {}
    month = data.get("month") or datetime.now().strftime("%Y-%m")
    memories = [m for m in load_memories() if m["month"] == month]

    if not memories:
        return jsonify({
            "source": "Demo",
            "title": "Your KINDER month",
            "story": "Add a few shared memories first, then create your AI rewind.",
            "count": 0,
        })

    friend_names = sorted({m["friend"] for m in memories})
    captions = [m["caption"] for m in memories]
    prompt = f"""
You are KINDER Rewind, an AI memory storyteller for Kathmandu University students.
KINDER is about friendships, collaboration and campus life, not dating.

Month: {month}
Number of shared memories: {len(memories)}
Friends in the memories: {', '.join(friend_names)}
Memory captions:
- """
    prompt += "\n- ".join(captions)
    prompt += """

Create a warm, short monthly recap.
Return exactly two lines:
TITLE: a creative title of 3-7 words
STORY: one sentence of 15-30 words describing the month.
Do not invent specific events that are not in the captions.
"""

    try:
        raw = ask_ai(prompt).strip()
        title = "Your KINDER Rewind"
        story = raw
        for line in raw.splitlines():
            if line.upper().startswith("TITLE:"):
                title = line.split(":", 1)[1].strip()
            elif line.upper().startswith("STORY:"):
                story = line.split(":", 1)[1].strip()
        return jsonify({"source": "Qwen2.5", "title": title, "story": story, "count": len(memories), "friends": friend_names})
    except Exception:
        return jsonify({
            "source": "Demo fallback",
            "title": "A Month We Shared",
            "story": f"You created {len(memories)} memories with {len(friend_names)} friend(s) across your KINDER journey this month.",
            "count": len(memories),
            "friends": friend_names,
        })


if __name__ == "__main__":
    app.run(debug=True)
