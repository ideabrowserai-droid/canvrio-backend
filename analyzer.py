import requests
from bs4 import BeautifulSoup
import time
import re

def analyze_cannabis_site(url):
    """
    Cannabis Website Performance Analyzer
    Focuses on measurable metrics that directly impact revenue: Speed, SEO, and Mobile Optimization.
    """
    try:
        start_time = time.time()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        load_time = time.time() - start_time
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = response.text.lower()
        
        # Core performance and SEO analysis
        analysis = {
            'url': url,
            'status_code': response.status_code,
            'load_time': load_time,
            'page_size': len(response.content),
            
            # Metrics kept from original analyzer but reframed for performance
            'mobile_friendly': check_mobile_friendly(soup),
            'has_https': url.startswith('https://'),
            'has_contact': check_contact_info(text_content),
            
            # New SEO-focused metrics
            'title_tag': check_title_tag(soup),
            'meta_description': check_meta_description(soup),
            'h1_tag': check_h1_tag(soup),
        }
        
        # Calculate the new performance-based score
        analysis['score'] = calculate_performance_score(analysis)
        
        return analysis
        
    except requests.RequestException as e:
        # Return a failure result for unreachable sites
        return {
            'url': url,
            'status_code': 0,
            'load_time': 99,
            'mobile_friendly': False,
            'has_https': url.startswith('https://'),
            'has_contact': False,
            'title_tag': {'optimal': False},
            'meta_description': {'optimal': False},
            'h1_tag': {'optimal': False},
            'score': 0,
            'error': str(e)
        }

# --- KEPT AND ENHANCED FUNCTIONS ---

def check_mobile_friendly(soup):
    """Checks for the viewport meta tag, a key indicator of a mobile-responsive site."""
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    return bool(viewport and 'width=device-width' in str(viewport))

def check_contact_info(text_content):
    """Checks if conversion-critical contact info is easily findable."""
    contact_indicators = ['contact', 'phone', 'email', 'address', '@', 'mailto:', 'tel:']
    return any(indicator in text_content for indicator in contact_indicators)

# --- NEW SEO ANALYSIS FUNCTIONS ---

def check_title_tag(soup):
    """Analyzes the <title> tag for SEO best practices."""
    tag = soup.find('title')
    if not tag or not tag.string:
        return {'text': 'Missing', 'length': 0, 'optimal': False}
    
    text = tag.string.strip()
    length = len(text)
    optimal = 50 <= length <= 60
    return {'text': text, 'length': length, 'optimal': optimal}

def check_meta_description(soup):
    """Analyzes the meta description for SEO best practices."""
    tag = soup.find('meta', attrs={'name': 'description'})
    if not tag or not tag.get('content'):
        return {'text': 'Missing', 'length': 0, 'optimal': False}
        
    text = tag['content'].strip()
    length = len(text)
    optimal = 150 <= length <= 160
    return {'text': text, 'length': length, 'optimal': optimal}

def check_h1_tag(soup):
    """Analyzes the <h1> tag for SEO best practices (expects exactly one)."""
    tags = soup.find_all('h1')
    count = len(tags)
    optimal = count == 1
    text = tags[0].get_text(strip=True) if count > 0 else "Missing"
    return {'count': count, 'text': text, 'optimal': optimal}

# --- NEW SCORING SYSTEM ---

def calculate_performance_score(analysis):
    """
    Calculates a new score based on performance metrics that impact revenue.
    Total: 100 points.
    """
    score = 0
    
    # Page Speed (30 points) - Most important factor for user retention
    load_time = analysis['load_time']
    if load_time < 2.0:
        score += 30
    elif load_time < 3.0:
        score += 20
    elif load_time < 4.0:
        score += 10
    
    # Mobile Performance (25 points) - Crucial for over half of all traffic
    if analysis['mobile_friendly']:
        score += 25
        
    # Core SEO (25 points) - Foundational for Google ranking
    if analysis['title_tag']['optimal']:
        score += 10
    if analysis['meta_description']['optimal']:
        score += 8
    if analysis['h1_tag']['optimal']:
        score += 7
        
    # Security (10 points) - A direct SEO ranking factor
    if analysis['has_https']:
        score += 10
        
    # Conversion Elements (10 points) - Helps turn visitors into customers
    if analysis['has_contact']:
        score += 10
        
    return min(100, int(score))