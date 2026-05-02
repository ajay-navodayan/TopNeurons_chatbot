TAG_KEYWORDS = {
    "admission": [
        "admission", "apply", "application", "enroll", "registration", "join", "form",
        "apply for", "application form", "last date", "deadline", "phase", "batch",
        "online application", "apply now", "open now", "applications are open",
    ],
    "eligibility": [
        "eligibility", "eligible", "criteria", "qualify", "requirement",
        "age", "income", "merit", "class 10", "cbse", "rbse", "board",
        "percentage", "marks", "85%", "90%", "92%", "95%", "passing marks",
        "class 9", "provisional", "exempt", "qualifying",
    ],
    "exam": [
        "exam", "examination", "prelims", "mains", "test", "jee", "neet",
        "physics", "chemistry", "mathematics", "biology", "mental ability",
        "mock test", "negative marking", "marking scheme", "question paper",
        "200 questions", "engineering stream", "medical stream", "strategy",
        "preparation", "syllabus", "competitive",
    ],
    "results": [
        "result", "declared", "shortlisted", "selected", "interview",
        "merit list", "list declared", "result declared", "view result",
        "click here", "score", "rank",
    ],
    "program": [
        "program", "programme", "coaching", "batch", "classes", "mentorship",
        "hostel", "accommodation", "study material", "books", "guidance",
        "allen", "narayana", "jaipur", "rajasthan", "parinde", "yuva udaan", "udaan",
        "top neurons program", "free coaching", "structured",
    ],
    "benefits": [
        "benefit", "scholarship", "stipend", "support", "financial", "aid",
        "grant", "reward", "free education", "free coaching", "underprivileged",
        "economically weaker", "social mobility", "opportunity", "empower",
    ],
    "about": [
        "about", "mission", "vision", "founded", "history", "team",
        "organization", "foundation", "pratham shiksha", "charitable trust",
        "prem shanti", "ngo", "top neurons", "topneurons", "initiative",
        "committed", "dedicated", "registered trust",
    ],
    "contact": [
        "contact", "email", "phone", "address", "reach", "helpline",
        "whatsapp", "get in touch", "write to us", "call us",
    ],
    "faq": [
        "faq", "frequently asked", "question", "answer", "query", "doubt",
        "how to", "what is", "when is", "where is", "who can",
    ],
    "success": [
        "success", "achievement", "selected", "iit", "nit", "aiims",
        "topper", "rank", "congratulations", "alumni", "story", "result",
        "secured admission", "cleared", "cracked",
    ],
    "notice": [
        "notice", "notice board", "announcement", "update", "important",
        "notification", "inform", "declared", "extended", "postponed",
    ],
}


def classify_tag(text):
    text_lower = text.lower()
    scores = {tag: sum(kw in text_lower for kw in kws) for tag, kws in TAG_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"
