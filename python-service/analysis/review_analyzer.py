import pandas as pd
import math

def analyze_reviews(reviews: list[dict]) -> dict:
    if not reviews:
        return {
            "totalReviews": 0,
            "averageRating": 0.0,
            "ratingDistribution": {},
            "sentiment": {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        }
        
    df = pd.DataFrame(reviews)
    if 'rating' not in df.columns:
        return {
            "totalReviews": len(reviews),
            "averageRating": 0.0,
            "ratingDistribution": {},
            "sentiment": {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        }
        
    df['rating_numeric'] = pd.to_numeric(df['rating'], errors='coerce')
    valid_ratings = df.dropna(subset=['rating_numeric'])
    
    total_reviews = len(reviews)
    avg_rating = 0.0
    dist = {}
    sentiment = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
    
    if not valid_ratings.empty:
        avg_rating = round(valid_ratings['rating_numeric'].mean(), 2)
        
        counts = valid_ratings['rating_numeric'].value_counts().to_dict()
        dist = {str(int(k) if k == int(k) else k): int(v) for k, v in counts.items()}
        
        pos = len(valid_ratings[valid_ratings['rating_numeric'].isin([4, 5])])
        neu = len(valid_ratings[valid_ratings['rating_numeric'] == 3])
        neg = len(valid_ratings[valid_ratings['rating_numeric'].isin([1, 2])])
        
        total_valid = len(valid_ratings)
        sentiment["positive"] = round((pos / total_valid) * 100, 2)
        sentiment["neutral"] = round((neu / total_valid) * 100, 2)
        sentiment["negative"] = round((neg / total_valid) * 100, 2)
        
    return {
        "totalReviews": total_reviews,
        "averageRating": avg_rating,
        "ratingDistribution": dist,
        "sentiment": sentiment
    }
