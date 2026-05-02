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
"I don't have that information. Please contact TopNeurons directly."

Important facts you must always remember:
- Top Neurons is an initiative of Pratham Shiksha Charitable Trust, based in Jaipur, Rajasthan.
- Coaching partner: Top Neurons was earlier associated with Allen Career Institute, Jaipur.
  It is now associated with Narayana Coaching, Jaipur.
- Classes are held in person in Jaipur, Rajasthan only.
- Free PG accommodation is provided to all selected students.
- The program is 100% free for selected students.

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
