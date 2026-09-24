import pytest
from analysis.summarizer import generate_summary

def test_summary_empty():
    assert generate_summary([]) == "No reviews available to summarize."
    assert generate_summary([{"review": ""}]) == "No text content available in reviews."

def test_summary_single():
    res = generate_summary([{"review": "This is a single review."}])
    assert res == "This is a single review."
    
def test_summary_multiple():
    reviews = [
        {"review": "The product is amazing. I love the battery life."},
        {"review": "Screen is great. But it gets warm."},
        {"review": "Overall a good purchase. Highly recommended."}
    ]
    res = generate_summary(reviews, max_sentences=2)
    assert len(res.split('.')) > 1
