import re
from collections import Counter
import math

def clean_text(text: str) -> str:
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]

def generate_summary(reviews: list[dict], max_sentences: int = 4) -> str:
    if not reviews:
        return "No reviews available to summarize."
        
    all_text = " ".join([r.get("review", "") for r in reviews if r.get("review")])
    if not all_text.strip():
        return "No text content available in reviews."
        
    cleaned_text = clean_text(all_text)
    sentences = get_sentences(cleaned_text)
    
    if len(sentences) <= max_sentences:
        return " ".join(sentences)
        
    words = re.findall(r'\w+', cleaned_text.lower())
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'this', 'that', 'these', 'those', 'it', 'i', 'you', 'he', 'she', 'they', 'we'}
    
    word_freq = Counter(w for w in words if w not in stop_words)
    if not word_freq:
        return " ".join(sentences[:max_sentences])
        
    max_freq = max(word_freq.values())
    
    for word in word_freq:
        word_freq[word] = word_freq[word] / max_freq
        
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        words_in_sentence = re.findall(r'\w+', sentence.lower())
        score = 0
        for word in words_in_sentence:
            if word in word_freq:
                score += word_freq[word]
        
        if len(words_in_sentence) > 0:
            sentence_scores[i] = score / math.sqrt(len(words_in_sentence))
        else:
            sentence_scores[i] = 0
            
    top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    top_indices.sort()
    
    summary = " ".join([sentences[i] for i in top_indices])
    return summary
