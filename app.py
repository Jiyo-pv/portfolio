from flask import Flask, render_template, send_from_directory, jsonify, request
import os
import time
from google import genai

# ------------------
# CONFIG
# ------------------

app = Flask(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
PORTFOLIO_CONTEXT = """
FACTS ABOUT JIYO P V (USE ONLY THIS INFORMATION):

Name:
- Jiyo P V
Pronouns:
    he/his/him
Education:
- Bachelor of Computer Applications (BCA), graduated 2025, CGPA 8.17
- Master of Computer Applications (MCA), ongoing, expected 2027

Skills:
- Python, Django, Flask
- Java, Android Development
- MySQL, PostgreSQL, OracleDB
- HTML, CSS, Tailwind, Bootstrap
- Git, OOPs

Projects:
- Library Network System (Django + Android)
- Video Game Store (PHP + AJAX)

Certifications:
- RedTeam – Cyber Security Analyst
- Flutter Development Workshop

Availability:
- Available for internships
- Open to opportunities

Contact Information:
- Email: jiyopv21@gmail.com
- GitHub: https://github.com/jiyo-pv
- LinkedIn: https://www.linkedin.com/in/jiyo-pv

Rules:
- Do NOT invent any new information
- If something is not listed here, say:
  "That information is not available on this portfolio."
"""
PORTFOLIO_FAQ = {
    "education": {
        "keywords": ["education", "degree", "qualification", "study"],
        "answer": "I have completed a Bachelor of Computer Applications (CGPA 8.17) and I am currently pursuing a Master of Computer Applications (MCA)."
    },
    "projects": {
        "keywords": ["project", "projects", "work", "built"],
        "answer": "My projects include a Library Network System (Django + Android) and a Video Game Store (PHP + AJAX)."
    },
    "skills": {
        "keywords": ["skill", "skills", "technology", "tech stack"],
        "answer": "My skills include Python, Django, Java, Android development, Flask, MySQL, and web development."
    },
    "contact": {
        "keywords": ["contact", "email", "reach", "connect"],
        "answer": "You can contact me via email at jiyopv21@gmail.com or through LinkedIn. The contact section is available on this page."
    },
    "internship": {
        "keywords": ["internship", "job", "hire", "opportunity"],
        "answer": "I am currently available for internships and open to opportunities."
    },
     "certifications": {
        "keywords": ["certificate", "certificates", "certifications", "courses","certificate courses"],
        "answer": "My certifications include RedTeam – Cyber Security Analyst and a Flutter Development Workshop."
    }
    ,
     "github": {
        "keywords": ["git", "github", "repo", "repositories","repository"],
        "answer": "you can view  my github @ <a href='https://github.com/Jiyo-pv/'>https://github.com/Jiyo-pv/</a>"
    }
    ,
     "linkedin": {
    "keywords": ["linkedin", "linked"],
    "answer": "You can view my LinkedIn profile here: <a href='https://www.linkedin.com/in/jiyo-p-v/' target='_blank'>LinkedIn</a>"
    }


}
def detect_scroll_target(message: str):
    msg = message.lower()

    if any(k in msg for k in ["project", "projects"]):
        return "projects"
    if any(k in msg for k in ["skill", "skills", "technology"]):
        return "skills"
    if any(k in msg for k in ["education", "degree", "qualification"]):
        return "timeline"
    if any(k in msg for k in ["certificate", "certification"]):
        return "certifications"
    if any(k in msg for k in ["contact", "email", "reach"]):
        return "contact"
    if "github" in msg:
        return "projects"
    if "linkedin" in msg:
        return "contact"

    return None

def get_fallback_reply(message: str):
    msg = message.lower()

    for item in PORTFOLIO_FAQ.values():
        for keyword in item["keywords"]:
            if keyword in msg:
                return item["answer"]

    return (
        "My AI assistant is currently resting due to usage limits. "
        "You can explore my portfolio sections above or contact me directly."
    )

SYSTEM_PROMPT = """
You are an assistant embedded in Jiyo P V’s portfolio.

STRICT RULES (MANDATORY):
- Use ONLY the provided portfolio facts
- DO NOT guess or infer
- DO NOT add degrees, universities, or experience not listed
- If unsure, say you don’t have that information

Your job:
- Answer questions about Jiyo’s portfolio
- Guide visitors to sections like Skills, Projects, Certifications
- Be concise and professional
"""

LAST_CALL = 0
MIN_DELAY = 5  # seconds

# ------------------
# ROUTES
# ------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download-resume")
def download_resume():
    return send_from_directory("static/resume", "resume.pdf", as_attachment=True)

@app.route("/success")
def success():
    return render_template("success.html")
@app.route("/api/chat", methods=["POST"])
def chat_with_ai():
    global LAST_CALL
    now = time.time()

    # Rate-limit to protect quota
    if now - LAST_CALL < MIN_DELAY:
        return jsonify({
            "reply": "Please wait a few seconds before asking again."
        })

    LAST_CALL = now

    user_msg = request.json.get("message", "").strip()
    if not user_msg:
        return jsonify({"reply": "Say something 🙂"})

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"""
{SYSTEM_PROMPT}

PORTFOLIO DATA:
{PORTFOLIO_CONTEXT}

User question:
{user_msg}
"""
        )

        scroll_target = detect_scroll_target(user_msg)

        return jsonify({
        "reply": response.text,
        "scrollTo": scroll_target
        })


    except Exception as e:
        app.logger.error(f"Gemini error: {e}")

        fallback = get_fallback_reply(user_msg)
        scroll_target = detect_scroll_target(user_msg)

        return jsonify({
            "reply": fallback,
            "scrollTo": scroll_target
            })


# ------------------
# LOCAL RUN ONLY
# ------------------

if __name__ == "__main__":
    app.run(debug=True)
