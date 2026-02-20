import re
from datetime import datetime

def extract_keywords(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    stopwords = {
        "the","and","or","of","to","a","in","on","for","with","as","is","are",
        "this","that","it","be","by","an","from","at","about","into","over"
    }
    freq = {}
    for w in words:
        if w not in stopwords and len(w) > 3:
            freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=freq.get, reverse=True)[:6]

def extract_sentences(text):
    sentences = re.split(r"[.!?]+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 0]

def summarize(text):
    sentences = extract_sentences(text)
    if not sentences:
        return []
    # Prendi le prime 2 frasi come mini‑riassunto
    return sentences[:2]

def run(query, session_id, chat_id):
    text = query.replace("analysis:", "").replace("analizza:", "").strip()

    keywords = extract_keywords(text)
    summary = summarize(text)

    result = {
        "tool": "analysis",
        "keywords": keywords,
        "summary": summary,
        "original_text": text,
        "session_id": session_id,
        "chat_id": chat_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    return result
