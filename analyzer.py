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
            
            # New cannabis-specific metrics
            'cannabis_seo': check_cannabis_seo_keywords(soup, text_content),
            'cannabis_education': check_cannabis_education_content(text_content),
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
            'cannabis_seo': {'score': 0},
            'cannabis_education': {'score': 0},
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

# --- NEW CANNABIS-SPECIFIC ANALYSIS FUNCTIONS ---

def check_cannabis_seo_keywords(soup, text_content):
    """
    Analyzes cannabis-specific SEO keyword integration for better search visibility.
    Returns score out of 12 points.
    """
    cannabis_keywords = [
        # Strain types
        'indica', 'sativa', 'hybrid',
        # Product categories  
        'flower', 'edibles', 'concentrates', 'vapes', 'pre-rolls', 'prerolls',
        # Effects/benefits
        'thc', 'cbd', 'terpenes', 'cannabinoids',
        # Industry terms
        'dispensary', 'cannabis', 'marijuana', 'weed', 'buds'
    ]
    
    score = 0
    title = soup.find('title')
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    
    # Title contains cannabis keywords (6 points)
    if title and title.string and any(keyword in title.string.lower() for keyword in cannabis_keywords):
        score += 6
    
    # Meta description contains cannabis keywords (4 points)  
    if meta_desc and meta_desc.get('content') and any(keyword in meta_desc.get('content', '').lower() for keyword in cannabis_keywords):
        score += 4
        
    # Body content has good cannabis keyword density (2 points)
    keyword_count = sum(text_content.count(keyword) for keyword in cannabis_keywords)
    if keyword_count >= 5:  # At least 5 cannabis keyword mentions
        score += 2
    
    return {
        'score': score,
        'keywords_found': keyword_count,
        'has_title_keywords': title and title.string and any(keyword in title.string.lower() for keyword in cannabis_keywords),
        'has_meta_keywords': meta_desc and meta_desc.get('content') and any(keyword in meta_desc.get('content', '').lower() for keyword in cannabis_keywords)
    }

def check_cannabis_education_content(text_content):
    """
    Analyzes presence of cannabis education content that builds customer trust.
    Returns score out of 8 points.
    """
    education_indicators = [
        # Dosage guidance
        'dosage', 'dose', 'how much', 'start low', 'microdose', 'mg',
        # Effects information  
        'effects', 'experience', 'duration', 'onset time', 'feeling',
        # Product education
        'strain guide', 'product guide', 'consumption methods', 'how to use',
        # Safety education
        'responsible use', 'safety', 'first time', 'beginner', 'new to cannabis'
    ]
    
    education_count = sum(1 for indicator in education_indicators if indicator in text_content)
    
    # Educational content scoring
    if education_count >= 8:
        score = 8  # Excellent education content
    elif education_count >= 5:
        score = 6  # Good education content  
    elif education_count >= 3:
        score = 4  # Some education content
    elif education_count >= 1:
        score = 2  # Minimal education content
    else:
        score = 0  # No education content
    
    return {
        'score': score,
        'education_indicators_found': education_count,
        'has_dosage_info': any(term in text_content for term in ['dosage', 'dose', 'mg', 'start low']),
        'has_effects_info': any(term in text_content for term in ['effects', 'experience', 'duration', 'feeling']),
        'has_safety_info': any(term in text_content for term in ['responsible use', 'safety', 'first time', 'beginner'])
    }

# --- NEW SCORING SYSTEM ---

def calculate_performance_score(analysis):
    """
    Calculates a cannabis-focused score based on performance metrics that impact revenue.
    Total: 100 points (reweighted to include cannabis-specific factors).
    """
    score = 0
    
    # Page Speed (25 points) - Most important factor for user retention
    load_time = analysis['load_time']
    if load_time < 2.0:
        score += 25
    elif load_time < 3.0:
        score += 17
    elif load_time < 4.0:
        score += 8
    
    # Mobile Performance (20 points) - Crucial for over half of all traffic
    if analysis['mobile_friendly']:
        score += 20
        
    # Core SEO (20 points) - Foundational for Google ranking
    if analysis['title_tag']['optimal']:
        score += 8
    if analysis['meta_description']['optimal']:
        score += 7
    if analysis['h1_tag']['optimal']:
        score += 5
        
    # Security (8 points) - A direct SEO ranking factor
    if analysis['has_https']:
        score += 8
        
    # Conversion Elements (7 points) - Helps turn visitors into customers
    if analysis['has_contact']:
        score += 7
    
    # Cannabis SEO Keywords (12 points) - Cannabis-specific search visibility
    score += analysis['cannabis_seo']['score']
    
    # Cannabis Education Content (8 points) - Builds customer trust and reduces anxiety
    score += analysis['cannabis_education']['score']
        
    return min(100, int(score))