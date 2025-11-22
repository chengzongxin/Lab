
import logging
from ai_title_cleaner import clean_title_with_fallback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cleaning():
    test_titles = [
        "Men's Winter Warm Knit Beanie - Premium Quality Soft Comfortable Hat",
        "Cute Cartoon Cotton Socks for Women - Breathable Casual Crew Socks",
        "Stylish Wool Scarf for Winter - Warm and Soft Neck Warmer"
    ]
    
    logger.info("Starting verification of AI cleaning improvements...")
    
    for title in test_titles:
        logger.info(f"\nOriginal Title: {title}")
        # Force fallback to rule-based cleaning if API key is not set or fails
        # But here we want to test the logic, so we'll see what happens.
        # If API is working, it should follow the new prompt.
        # If API fails, it should follow the new fallback rules.
        result = clean_title_with_fallback(title)
        
        cleaned = result['cleaned_keywords']
        keywords = result['keywords_list']
        model = result.get('model_used', 'unknown')
        
        logger.info(f"Model Used: {model}")
        logger.info(f"Cleaned Keywords: {cleaned}")
        logger.info(f"Keywords List: {keywords}")
        
        # Check for forbidden words
        forbidden = ['beanie', 'hat', 'sock', 'socks', 'scarf', 'cap']
        found_forbidden = [word for word in forbidden if word in cleaned.lower().split()]
        
        if found_forbidden:
            logger.error(f"❌ FAILED: Found forbidden words: {found_forbidden}")
        else:
            logger.info("✅ PASSED: No forbidden words found.")

if __name__ == "__main__":
    test_cleaning()
