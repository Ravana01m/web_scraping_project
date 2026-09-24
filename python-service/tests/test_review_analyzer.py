import pytest
from analysis.review_analyzer import analyze_reviews

def test_analyze_empty():
    res = analyze_reviews([])
    assert res["totalReviews"] == 0
    assert res["averageRating"] == 0.0
    
def test_analyze_no_ratings():
    reviews = [{"review": "good"}]
    res = analyze_reviews(reviews)
    assert res["totalReviews"] == 1
    assert res["averageRating"] == 0.0
    
def test_analyze_valid():
    reviews = [
        {"rating": "5", "review": "great"},
        {"rating": "4.0", "review": "good"},
        {"rating": "3", "review": "ok"},
        {"rating": "1", "review": "bad"},
        {"rating": "invalid", "review": "invalid"}
    ]
    res = analyze_reviews(reviews)
    assert res["totalReviews"] == 5
    assert res["averageRating"] == 3.25
    assert res["sentiment"]["positive"] == 50.0
    assert res["sentiment"]["neutral"] == 25.0
    assert res["sentiment"]["negative"] == 25.0
    assert "5" in res["ratingDistribution"]
    assert "1" in res["ratingDistribution"]
