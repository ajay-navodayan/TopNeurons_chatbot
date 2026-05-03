from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, TOP_K
from vector_store import retrieve

ELIGIBILITY_KEYWORDS = [
    "am i eligible", "can i apply", "do i qualify", "eligibility criteria",
    "who can apply", "what are the requirements", "minimum marks", "minimum percentage",
    "class 10 required", "age limit", "income limit",
]

SYSTEM_PROMPT = """You are a helpful assistant for TopNeurons Foundation, an educational NGO.
Answer questions ONLY based on the provided context. If the answer is not in the context, say:
"I don't have that information. Please contact TopNeurons directly at info@topneurons.org"

Key facts you must always remember:
- Top Neurons is an initiative of Pratham Shiksha Charitable Trust, Jaipur, Rajasthan.
- Founder: Puneet Mittal
- Managing Director: Yogesh Sharma
- Coaching partner: Earlier associated with Allen Career Institute, Jaipur. Now associated with Narayana Coaching, Jaipur.
- Classes are held in person in Jaipur, Rajasthan only.
- Free PG accommodation is provided to all selected students.
- The program is 100% free for selected students from economically weaker sections.
- Top Neurons students have secured admissions in top IITs, NITs, AIIMS, ISM Dhanbad, and top medical colleges across India.
- First batch alumni are placed in Top PSUs, HFT firms, IT companies, healthcare, and various sectors with excellent salary packages.
- Top Neurons Parinde Pink City Program: Full-time residential coaching program in Jaipur for JEE/NEET aspirants from class 10 pass-outs. Provides free coaching, free PG accommodation, school admission support (66% fees covered), and continuous mentorship.
- Top Neurons Yuva Udaan Scholarship Program: Part-time scholarship program. Students pay only Rs 5000/year. For students who cannot relocate to Jaipur.

Be concise, friendly, and accurate."""

client = Groq(api_key=GROQ_API_KEY)


def eligibility_check(query):
    q = query.lower()
    if any(kw in q for kw in ELIGIBILITY_KEYWORDS):
        return (
            "To check your eligibility for TopNeurons programs, please review the eligibility criteria "
            "on the website or contact the foundation directly. Generally, eligibility depends on academic "
            "merit, financial need, and age criteria. Would you like more details from our knowledge base?"
        )
    return None


def chat(query, history=None):
    # Rule-based check first
    rule_response = eligibility_check(query)
    if rule_response:
        return rule_response, []

    chunks = retrieve(query, top_k=TOP_K)
    context = "\n\n".join(
        f"[Source: {c['url']}]\n{c['text']}" for c in chunks
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-6:])  # last 3 turns
    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {query}"
    })

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=512,
    )
    answer = response.choices[0].message.content.strip()
    return answer, chunks
