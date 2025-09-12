"""
Enhanced Cannabis Website Analyzer
Includes additional compliance checks based on real violations and micro-SaaS opportunities
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.parse import urljoin, urlparse
from typing import Dict, List

def analyze_cannabis_site_enhanced(url: str) -> Dict:
    """
    Enhanced cannabis website analysis with additional compliance checks
    Based on real Canadian cannabis violations and enforcement patterns
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
        
        # Enhanced compliance analysis
        analysis = {
            'url': url,
            'status_code': response.status_code,
            'load_time': load_time,
            
            # Basic compliance (existing)
            'has_age_gate': check_age_verification(text_content, soup),
            'has_warning': check_health_warnings(text_content),
            'has_license': check_license_display(text_content),
            'mobile_friendly': check_mobile_friendly(soup),
            'has_https': url.startswith('https://'),
            'has_contact': check_contact_info(text_content),
            
            # Enhanced compliance checks (new revenue opportunities)
            'provincial_compliance': check_provincial_compliance(text_content, url),
            'inter_provincial_warnings': check_inter_provincial_warnings(text_content),
            'quantity_limit_display': check_quantity_limits(text_content),
            'payment_compliance': check_payment_methods(text_content),
            'marketing_compliance': check_marketing_compliance(text_content, soup),
            'accessibility_compliance': check_accessibility(soup),
            'gdpr_privacy_compliance': check_privacy_compliance(text_content, soup),
            'social_media_compliance': check_social_media_links(soup),
            
            # Technical performance
            'page_size': len(response.content),
            'title_length': len(soup.title.string) if soup.title else 0,
            'meta_description': check_meta_description(soup),
            'structured_data': check_structured_data(soup),
        }
        
        # Calculate enhanced score with new compliance factors
        score = calculate_enhanced_score(analysis)
        analysis['score'] = score
        analysis['compliance_category'] = get_compliance_category(score)
        analysis['risk_level'] = get_risk_level(analysis)
        analysis['recommendations'] = get_enhanced_recommendations(analysis)
        
        return analysis
        
    except requests.RequestException as e:
        return get_error_response(url, str(e))

def check_provincial_compliance(text_content: str, url: str) -> Dict:
    """
    Check for provincial-specific compliance indicators
    Based on real violations: Cannabis Xpress $100K fine, provincial reporting gaps
    """
    province_indicators = {
        'ontario': ['ocs', 'ontario cannabis store', 'agco', 'lcbo'],
        'british_columbia': ['bccs', 'bc cannabis', 'bcldb'],
        'alberta': ['aglc', 'alberta gaming'],
        'quebec': ['sqdc', 'société québécoise'],
        'manitoba': ['manitoba liquor'],
        'saskatchewan': ['slga', 'saskatchewan liquor'],
        'nova_scotia': ['nslc', 'nova scotia liquor'],
        'new_brunswick': ['cannabis nb'],
        'pei': ['pei cannabis'],
        'newfoundland': ['canopy growth', 'tweed'],
        'yukon': ['yukon liquor'],
        'nwt': ['nwt liquor'],
        'nunavut': ['nunavut liquor']
    }
    
    detected_provinces = []
    for province, indicators in province_indicators.items():
        for indicator in indicators:
            if indicator in text_content or indicator in url.lower():
                detected_provinces.append(province)
                break
    
    # Check for specific provincial warnings
    provincial_warnings = [
        'authorized retailer', 'détaillant autorisé',
        'licensed by', 'licensed in', 'autorisé par',
        'provincial regulations', 'réglementations provinciales'
    ]
    
    has_provincial_warnings = any(warning in text_content for warning in provincial_warnings)
    
    return {
        'detected_provinces': detected_provinces,
        'has_provincial_warnings': has_provincial_warnings,
        'compliance_score': len(detected_provinces) + (2 if has_provincial_warnings else 0)
    }

def check_inter_provincial_warnings(text_content: str) -> Dict:
    """
    Check for inter-provincial sales compliance
    Validation: Montrose Cannabis suspended for inter-provincial violations
    """
    inter_provincial_indicators = [
        'shipping restrictions', 'livraison restreinte',
        'not available in', 'non disponible dans',
        'provincial restrictions', 'restrictions provinciales',
        'local delivery only', 'livraison locale seulement',
        'check local laws', 'vérifiez les lois locales',
        'province specific', 'spécifique à la province'
    ]
    
    warning_count = sum(1 for indicator in inter_provincial_indicators if indicator in text_content)
    
    return {
        'has_warnings': warning_count > 0,
        'warning_count': warning_count,
        'compliance_score': min(warning_count * 2, 10)  # Max 10 points
    }

def check_quantity_limits(text_content: str) -> Dict:
    """
    Check for quantity limit displays and warnings
    Based on retail compliance requirements
    """
    quantity_indicators = [
        'possession limit', 'limite de possession',
        'daily limit', 'limite quotidienne',
        'maximum', 'maximum per person',
        '30 gram', '30g', '30 gramme',
        'purchase limit', 'limite d\'achat',
        'legal limit', 'limite légale'
    ]
    
    limit_count = sum(1 for indicator in quantity_indicators if indicator in text_content)
    
    return {
        'has_limits': limit_count > 0,
        'limit_mentions': limit_count,
        'compliance_score': min(limit_count * 3, 15)  # Max 15 points
    }

def check_payment_methods(text_content: str) -> Dict:
    """
    Check for compliant payment method displays
    Cannabis payment compliance is critical for regulatory adherence
    """
    payment_methods = [
        'cash only', 'comptant seulement',
        'debit', 'interac', 'visa debit',
        'credit card', 'carte de crédit',
        'e-transfer', 'virement électronique',
        'payment upon delivery', 'paiement à la livraison'
    ]
    
    payment_count = sum(1 for method in payment_methods if method in text_content)
    
    # Check for prohibited payment warnings
    prohibited_warnings = [
        'no credit cards', 'pas de cartes de crédit',
        'cash or debit only', 'comptant ou débit seulement'
    ]
    
    has_prohibited_warnings = any(warning in text_content for warning in prohibited_warnings)
    
    return {
        'payment_methods_listed': payment_count,
        'has_prohibited_warnings': has_prohibited_warnings,
        'compliance_score': payment_count * 2 + (5 if has_prohibited_warnings else 0)
    }

def check_marketing_compliance(text_content: str, soup: BeautifulSoup) -> Dict:
    """
    Check for marketing compliance issues
    Validation: Ghost Drops $250K AMP for marketing violations
    """
    prohibited_marketing = [
        'lifestyle', 'glamorize', 'glamouriser',
        'party', 'fête', 'celebration',
        'appealing to youth', 'attrayant pour les jeunes',
        'cartoon', 'mascot', 'mascotte',
        'celebrity endorsement', 'endorsement de célébrité'
    ]
    
    prohibited_count = sum(1 for term in prohibited_marketing if term in text_content)
    
    # Check for compliant educational language
    educational_terms = [
        'educational', 'éducatif',
        'medical information', 'information médicale',
        'responsible use', 'usage responsable',
        'health effects', 'effets sur la santé',
        'research', 'recherche'
    ]
    
    educational_count = sum(1 for term in educational_terms if term in text_content)
    
    # Check images for compliance (basic check)
    images = soup.find_all('img')
    image_alt_compliance = sum(1 for img in images if img.get('alt') and 'cannabis' not in img.get('alt', '').lower())
    
    return {
        'prohibited_marketing_count': prohibited_count,
        'educational_content_count': educational_count,
        'compliant_images': image_alt_compliance,
        'compliance_score': max(0, (educational_count * 3) - (prohibited_count * 5))
    }

def check_accessibility(soup: BeautifulSoup) -> Dict:
    """
    Check for accessibility compliance (WCAG guidelines)
    Required for government compliance and human rights legislation
    """
    accessibility_features = {
        'alt_text': len([img for img in soup.find_all('img') if img.get('alt')]),
        'aria_labels': len(soup.find_all(attrs={'aria-label': True})),
        'heading_structure': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
        'form_labels': len([label for label in soup.find_all('label') if label.get('for')]),
        'skip_links': len(soup.find_all('a', href=re.compile(r'#.*')))
    }
    
    total_score = sum(min(value, 10) for value in accessibility_features.values()) / 5
    
    return {
        'features': accessibility_features,
        'compliance_score': int(total_score)
    }

def check_privacy_compliance(text_content: str, soup: BeautifulSoup) -> Dict:
    """
    Check for privacy policy and GDPR compliance
    Critical for cannabis businesses handling customer data
    """
    privacy_indicators = [
        'privacy policy', 'politique de confidentialité',
        'data protection', 'protection des données',
        'gdpr', 'pipeda', 'personal information',
        'cookie policy', 'politique de cookies',
        'consent', 'consentement'
    ]
    
    privacy_count = sum(1 for indicator in privacy_indicators if indicator in text_content)
    
    # Check for privacy policy link
    privacy_links = soup.find_all('a', href=re.compile(r'privacy|confidentialité', re.I))
    
    return {
        'privacy_mentions': privacy_count,
        'has_privacy_links': len(privacy_links) > 0,
        'compliance_score': privacy_count * 2 + (len(privacy_links) * 3)
    }

def check_social_media_links(soup: BeautifulSoup) -> Dict:
    """
    Check social media presence and compliance
    Important for cannabis businesses navigating platform restrictions
    """
    social_platforms = {
        'instagram': ['instagram.com', 'ig.com'],
        'facebook': ['facebook.com', 'fb.com'],
        'twitter': ['twitter.com', 'x.com'],
        'linkedin': ['linkedin.com'],
        'youtube': ['youtube.com', 'youtu.be'],
        'tiktok': ['tiktok.com']
    }
    
    detected_platforms = []
    all_links = soup.find_all('a', href=True)
    
    for platform, domains in social_platforms.items():
        for link in all_links:
            if any(domain in link['href'] for domain in domains):
                detected_platforms.append(platform)
                break
    
    return {
        'platforms': detected_platforms,
        'platform_count': len(detected_platforms),
        'compliance_score': len(detected_platforms) * 2  # More platforms = better reach
    }

def check_meta_description(soup: BeautifulSoup) -> Dict:
    """Check for SEO meta description"""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        content = meta_desc['content']
        return {
            'has_description': True,
            'length': len(content),
            'optimal': 150 <= len(content) <= 160,
            'content': content[:100] + '...' if len(content) > 100 else content
        }
    return {'has_description': False, 'length': 0, 'optimal': False}

def check_structured_data(soup: BeautifulSoup) -> Dict:
    """Check for structured data (JSON-LD, microdata)"""
    json_ld = soup.find_all('script', type='application/ld+json')
    microdata = soup.find_all(attrs={'itemscope': True})
    
    return {
        'json_ld_count': len(json_ld),
        'microdata_count': len(microdata),
        'has_structured_data': len(json_ld) > 0 or len(microdata) > 0
    }

def calculate_enhanced_score(analysis: Dict) -> int:
    """
    Enhanced scoring algorithm including new compliance factors
    Total possible: 100 points
    """
    score = 0
    
    # Core compliance (60 points total)
    if analysis['has_https']: score += 10
    if analysis['has_age_gate']: score += 20  # Most critical
    if analysis['has_warning']: score += 15
    if analysis['has_license']: score += 15
    
    # Performance & UX (15 points total)
    if analysis['mobile_friendly']: score += 5
    if analysis['load_time'] < 3: score += 5
    elif analysis['load_time'] < 5: score += 3
    if analysis['has_contact']: score += 5
    
    # Enhanced compliance (25 points total)
    score += min(analysis['provincial_compliance']['compliance_score'], 5)
    score += min(analysis['inter_provincial_warnings']['compliance_score'], 5)
    score += min(analysis['quantity_limit_display']['compliance_score'], 5)
    score += min(analysis['marketing_compliance']['compliance_score'], 5)
    score += min(analysis['accessibility_compliance']['compliance_score'], 5)
    
    # Bonus points for exceptional compliance
    if analysis['gdpr_privacy_compliance']['compliance_score'] > 5:
        score += 3
    if analysis['social_media_compliance']['platform_count'] >= 3:
        score += 2
    
    return min(100, max(0, score))

def get_compliance_category(score: int) -> str:
    """Categorize compliance level"""
    if score >= 90: return "Excellent"
    elif score >= 80: return "Good" 
    elif score >= 70: return "Fair"
    elif score >= 60: return "Poor"
    else: return "Critical"

def get_risk_level(analysis: Dict) -> str:
    """Assess regulatory risk level"""
    critical_missing = []
    if not analysis['has_age_gate']: critical_missing.append('age_gate')
    if not analysis['has_warning']: critical_missing.append('health_warnings')
    if not analysis['has_license']: critical_missing.append('license_display')
    
    if len(critical_missing) >= 2: return "High Risk"
    elif len(critical_missing) == 1: return "Medium Risk"
    elif analysis['score'] < 70: return "Low Risk"
    else: return "Compliant"

def get_enhanced_recommendations(analysis: Dict) -> List[str]:
    """Generate detailed recommendations for compliance improvements"""
    recommendations = []
    
    # Critical compliance issues
    if not analysis['has_age_gate']:
        recommendations.append("🚨 CRITICAL: Implement age verification gate - legally required for all cannabis websites")
    
    if not analysis['has_warning']:
        recommendations.append("⚠️ CRITICAL: Add Health Canada health warnings - required by federal law")
    
    if not analysis['has_license']:
        recommendations.append("📋 HIGH: Display license information - proves legal authorization to operate")
    
    # Provincial compliance
    if analysis['provincial_compliance']['compliance_score'] < 3:
        recommendations.append("🏛️ Add provincial compliance indicators - show local authorization")
    
    # Inter-provincial warnings
    if not analysis['inter_provincial_warnings']['has_warnings']:
        recommendations.append("🌍 Add shipping/delivery restriction warnings - prevent inter-provincial violations")
    
    # Marketing compliance
    if analysis['marketing_compliance']['compliance_score'] < 5:
        recommendations.append("📢 Review marketing content - ensure educational focus, avoid lifestyle messaging")
    
    # Technical improvements
    if not analysis['has_https']:
        recommendations.append("🔒 Enable HTTPS - required for secure transactions and trust")
    
    if analysis['load_time'] > 3:
        recommendations.append(f"⚡ Improve page speed - currently {analysis['load_time']:.1f}s, aim for <3s")
    
    # Accessibility
    if analysis['accessibility_compliance']['compliance_score'] < 15:
        recommendations.append("♿ Improve accessibility - add alt text, ARIA labels, proper heading structure")
    
    # Privacy compliance
    if analysis['gdpr_privacy_compliance']['compliance_score'] < 5:
        recommendations.append("🔐 Add privacy policy and cookie consent - required for customer data protection")
    
    return recommendations

def get_error_response(url: str, error: str) -> Dict:
    """Return error response structure"""
    return {
        'url': url,
        'status_code': 0,
        'load_time': 0,
        'has_age_gate': False,
        'has_warning': False,
        'has_license': False,
        'mobile_friendly': False,
        'has_https': url.startswith('https://'),
        'has_contact': False,
        'provincial_compliance': {'compliance_score': 0},
        'inter_provincial_warnings': {'compliance_score': 0},
        'quantity_limit_display': {'compliance_score': 0},
        'payment_compliance': {'compliance_score': 0},
        'marketing_compliance': {'compliance_score': 0},
        'accessibility_compliance': {'compliance_score': 0},
        'gdpr_privacy_compliance': {'compliance_score': 0},
        'social_media_compliance': {'compliance_score': 0},
        'score': 15,
        'compliance_category': 'Critical',
        'risk_level': 'High Risk',
        'error': error,
        'recommendations': ['🚨 Website unreachable - check URL and server status']
    }

# Import existing functions from analyzer.py
def check_age_verification(text_content, soup):
    """Check for age verification - the most important cannabis compliance item"""
    age_indicators = [
        '19+', '18+', '21+',  # Age indicators
        'age verification', 'age gate', 'verify age',
        'must be 19', 'must be 18', 'must be 21',
        'are you 19', 'are you 18', 'are you 21',
        'confirm age', 'legal age',
        'adult use', 'adults only'
    ]
    
    # Check text content
    for indicator in age_indicators:
        if indicator in text_content:
            return True
    
    # Check for age-related form inputs or buttons
    age_inputs = soup.find_all(['input', 'button'], string=re.compile(r'age|19|18|21', re.I))
    if age_inputs:
        return True
        
    # Check for modal or popup indicators
    modal_classes = soup.find_all(attrs={'class': re.compile(r'age|modal|popup|gate', re.I)})
    if modal_classes:
        return True
        
    return False

def check_health_warnings(text_content):
    """Check for Health Canada warnings and other health-related disclaimers"""
    health_warnings = [
        'health canada', 'santé canada',
        'health warning', 'avertissement',
        'may cause drowsiness', 'peut causer',
        'keep away from children', 'tenir hors de portée',
        'do not operate', 'ne pas conduire',
        'cannabis products', 'produits cannabis',
        'this product has not been analyzed',
        'ce produit n\'a pas été analysé',
        'for medical use only', 'usage médical seulement',
        'warning:', 'attention:', 'avertissement:'
    ]
    
    for warning in health_warnings:
        if warning in text_content:
            return True
            
    return False

def check_license_display(text_content):
    """Check if cannabis license information is displayed"""
    license_indicators = [
        'license', 'licence', 'permit',
        'health canada license', 'licence santé canada',
        'cultivation license', 'processing license',
        'retail license', 'licence de vente',
        'authorized dealer', 'détaillant autorisé',
        'licensed producer', 'producteur autorisé',
        'micro-cultivator', 'micro-cultivation',
        'lp#', 'licence #', 'permit #'
    ]
    
    for indicator in license_indicators:
        if indicator in text_content:
            return True
            
    # Look for license number patterns (common formats)
    license_patterns = [
        r'lic[a-z]*\s*#?\s*\d+',  # License #123
        r'permit\s*#?\s*\d+',      # Permit #456
        r'[a-z]{2,4}-\d{3,6}',     # LP-12345 format
    ]
    
    for pattern in license_patterns:
        if re.search(pattern, text_content):
            return True
            
    return False

def check_mobile_friendly(soup):
    """Check for mobile optimization"""
    # Look for viewport meta tag
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport and 'width=device-width' in str(viewport):
        return True
        
    # Look for responsive CSS classes
    responsive_classes = soup.find_all(attrs={'class': re.compile(r'responsive|mobile|col-', re.I)})
    if responsive_classes:
        return True
        
    return False

def check_contact_info(text_content):
    """Check if contact information is available"""
    contact_indicators = [
        'contact', 'phone', 'email', 'address',
        'call us', 'reach us', 'get in touch',
        '@', 'mailto:', 'tel:',
        'customer service', 'support'
    ]
    
    for indicator in contact_indicators:
        if indicator in text_content:
            return True
            
    return False

if __name__ == "__main__":
    # Test with enhanced analyzer
    test_url = "https://ocs.ca"
    result = analyze_cannabis_site_enhanced(test_url)
    print(f"Enhanced Analysis for {test_url}:")
    print(f"Score: {result['score']}/100 ({result['compliance_category']})")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendations: {len(result['recommendations'])} items")
    for rec in result['recommendations'][:3]:
        try:
            print(f"  - {rec}")
        except UnicodeEncodeError:
            # Handle Unicode encoding issues
            safe_rec = rec.encode('ascii', 'ignore').decode('ascii')
            print(f"  - {safe_rec}")