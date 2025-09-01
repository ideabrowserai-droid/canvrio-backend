import feedparser
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from pydantic import BaseModel, field_validator
import uvicorn
from datetime import datetime, timedelta
import sqlite3
import os
import re
import traceback
import logging
import json
import sys
import asyncio
from typing import Optional, List, Dict
import anthropic
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Content Aggregation - Clean single class approach
import requests
from bs4 import BeautifulSoup
import feedparser
import time
import hashlib
from ddgs import DDGS

# Load environment variables from .env file if it exists
load_dotenv()

# Simple lifespan manager for basic initialization:
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle
    """
    # Startup
    logger.info("Starting up Canvrio backend...")
    # Initialize databases
    init_database()
    init_content_database()
    logger.info("Databases initialized")
    yield  # Server runs here
    # Shutdown
    logger.info("Shutting down Canvrio backend...")

# Create FastAPI app:
app = FastAPI(title="Canvrio API", version="2.4.1", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security setup for curator authentication
security = HTTPBasic()

def get_curator_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify curator credentials"""
    correct_username = secrets.compare_digest(credentials.username, "canvrio")
    correct_password = secrets.compare_digest(credentials.password, "canntech420")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Mount static files for logos and assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIDebugger:
    """AI-powered debugging assistant for Canvrio FastAPI application"""
    def __init__(self):
        self.client = None
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.log_file = 'claude_debug.log'
        self.model = 'claude-3-haiku-20240307'
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("AI Debugger initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
        else:
            logger.warning("ANTHROPIC_API_KEY not set - AI debugging disabled")

    def sanitize_request_data(self, request_data: dict) -> dict:
        """Remove sensitive information from request data"""
        sensitive_keys = ['password', 'token', 'api_key', 'secret', 'authorization']
        sanitized = {}
        for key, value in request_data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        return sanitized

    async def analyze_error(self, 
                          error: Exception, 
                          endpoint: str, 
                          request: Optional[Request] = None,
                          request_data: Optional[dict] = None) -> str:
        """Analyze error using Claude and return debugging insights"""
        if not self.client:
            return "AI debugging unavailable - ANTHROPIC_API_KEY not configured"
        try:
            error_traceback = traceback.format_exc()
            context = {
                'endpoint': endpoint,
                'timestamp': datetime.now().isoformat(),
                'error_type': type(error).__name__,
                'error_message': str(error)
            }
            prompt = self._create_debug_prompt(error_traceback, context)
            message = self.client.messages.create(
                model=self.model, max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            analysis = message.content[0].text if message.content else "No analysis received"
            self._log_analysis(context, error_traceback, analysis)
            return analysis
        except Exception as debug_error:
            error_msg = f"AI debugging failed: {debug_error}"
            logger.error(error_msg)
            return error_msg

    def _create_debug_prompt(self, traceback_str: str, context: dict) -> str:
        return f"You are an expert debugger... Error Details: {context.get('endpoint')} ... Full Traceback: {traceback_str}"

    def _log_analysis(self, context: dict, traceback_str: str, analysis: str):
        pass

ai_debugger = AIDebugger()

# --- Pydantic Models ---
class NewsletterSubscription(BaseModel):
    email: str
    consent_marketing: bool
    consent_privacy: bool
    age_verified: bool
    data_processing_consent: bool

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v

class BulkUpdateRequest(BaseModel):
    content_ids: List[int]

# --- Database Initialization ---
def init_database():
    """Initialize SQLite database for newsletter subscriptions"""
    if not os.path.exists('newsletter.db'):
        conn = sqlite3.connect('newsletter.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                consent_marketing BOOLEAN NOT NULL,
                consent_privacy BOOLEAN NOT NULL,
                age_verified BOOLEAN NOT NULL,
                data_processing_consent BOOLEAN NOT NULL,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

def init_content_database():
    """Initialize SQLite database for aggregated content with enhanced schema"""
    db_path = 'content.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable WAL mode
    cursor.execute('PRAGMA journal_mode=WAL;')
    
    # Update existing schema to match sophisticated version
    try:
        cursor.execute('ALTER TABLE content_feeds ADD COLUMN engagement_metrics JSON')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE content_feeds ADD COLUMN content_hash VARCHAR(255) UNIQUE')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE content_feeds MODIFY COLUMN category TEXT NOT NULL')
    except sqlite3.OperationalError:
        pass  # SQLite doesn't support MODIFY, but that's ok
    
    conn.commit()
    conn.close()

# --- Clean Content Aggregator - Single Class Approach ---
class ContentAggregator:
    """Clean, single-purpose content aggregator for cannabis industry intelligence"""
    
    def __init__(self):
        self.db_path = 'content.db'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        self.business_keywords = [
            'pricing', 'wholesale', 'retail', 'dispensary', 'license', 'compliance', 'earnings', 
            'strategy', 'operations', 'regulations', 'health canada', 'provincial', 'ocs', 
            'revenue', 'profit', 'market share', 'acquisition', 'licensing'
        ]
        
        self.exclude_keywords = [
            'personal', 'lifestyle', 'strain review', 'product review', 'taste',
            'flavor', 'high', 'stoned', 'blazed', 'consumption', 'smoking'
        ]
        
        logger.info("Content Aggregator initialized with enhanced features.")
    
    def calculate_business_relevance(self, title: str, content: str, source: str) -> float:
        """Calculate business relevance score for content"""
        text = f"{title} {content}".lower()
        score = 2.0
        
        # Add points for business keywords
        score += min(sum(1 for keyword in self.business_keywords if keyword in text) * 0.8, 5.0)
        
        # Subtract points for excluded keywords
        score -= sum(1 for keyword in self.exclude_keywords if keyword in text) * 0.3
        
        # Source authority scoring
        source_lower = source.lower()
        if any(target in source_lower for target in ['mjbizdaily', 'stratcann', 'cannabis business times', 'new cannabis ventures']):
            score += 3.0
        elif 'health canada' in source_lower:
            score += 2.5
        elif source_lower.startswith('r/'):
            score += 1.0
        else:
            score += 0.5
        
        # Content quality bonuses
        if len(content or '') > 50:
            score += 1.0
        if any(indicator in text for indicator in ['analysis', 'report', 'update', 'strategy']):
            score += 1.0
        if any(keyword in text for keyword in ['cannabis', 'marijuana', 'thc', 'cbd', 'dispensary']):
            score += 1.5
        
        return max(0.0, min(score, 10.0))
    
    def should_include_content(self, title: str, content: str, source: str) -> bool:
        """Determine if content should be included based on relevance"""
        score = self.calculate_business_relevance(title, content, source)
        if 'health canada' in source.lower():
            return score >= 1.5
        # Lowered threshold to capture more news articles
        return score >= 1.0
    
    def get_content_hash(self, title: str, content: str) -> str:
        """Generate unique hash for content deduplication"""
        text = f"{title}{content}"
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def categorize_content(self, title: str, content: str, source: str) -> str:
        """Categorize content based on keywords and source"""
        text = f"{title} {content}".lower()
        
        if any(k in text for k in ['pricing', 'wholesale', 'retail price']):
            return 'Pricing Intelligence'
        if any(k in text for k in ['regulation', 'compliance', 'license', 'health canada']):
            return 'Regulatory'
        if any(k in text for k in ['earnings', 'cannara', 'canopy', 'sndl', 'tilray']):
            return 'Public Company'
        if any(k in text for k in ['operations', 'store', 'dispensary']):
            return 'Retail Operations'
        if source.startswith('r/'):
            return 'Community'
        
        return 'Industry Commentary'
    
    def fetch_rss_feeds(self) -> List[Dict]:
        """Fetch content from RSS feeds"""
        content = []
        rss_feeds = [
            {'url': 'https://stratcann.ca/feed', 'source': 'StratCann'},
            {'url': 'https://mjbizdaily.com/feed/', 'source': 'MJBizDaily'},
            {'url': 'https://www.newcannabisventures.com/feed/', 'source': 'New Cannabis Ventures'},
            {'url': 'https://www.cannabisbusinesstimes.com/rss/', 'source': 'Cannabis Business Times'},
        ]
        
        for feed_info in rss_feeds:
            try:
                feed = feedparser.parse(feed_info['url'])
                for entry in feed.entries[:5]:
                    published_dt = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_dt = datetime(*entry.published_parsed[:6])
                    
                    # Skip content older than 7 days to allow content aging for Canvrio's Picks
                    if published_dt < (datetime.now() - timedelta(days=7)):
                        continue
                    
                    title = re.sub(r'^[^a-zA-Z0-9@]+', '', entry.title).strip()
                    summary = BeautifulSoup(getattr(entry, 'summary', ''), 'html.parser').get_text(strip=True)[:400]
                    
                    content.append({
                        'title': title,
                        'content': summary,
                        'source': feed_info['source'],
                        'url': entry.link,
                        'published_date': published_dt
                    })
            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_info['source']}: {e}")
        
        return content
    
    def fetch_reddit_content(self) -> List[Dict]:
        """Fetch content from Reddit (simplified approach)"""
        content = []
        headers = {'User-Agent': 'Canvrio/1.0'}
        subreddits = ['canadients', 'TheOCS', 'CanadianCannabisLPs']
        
        for sub in subreddits:
            try:
                url = f'https://www.reddit.com/r/{sub}/hot.json?limit=10'
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                for post_data in response.json()['data']['children']:
                    post = post_data['data']
                    if post.get('created_utc', 0) > (time.time() - 86400):
                        content.append({
                            'title': post.get('title', ''),
                            'content': post.get('selftext', '')[:400],
                            'source': f'r/{sub}',
                            'url': f"https://reddit.com{post.get('permalink', '')}",
                            'published_date': datetime.fromtimestamp(post.get('created_utc'))
                        })
            except Exception as e:
                logger.error(f"Error fetching from r/{sub}: {e}")
        
        return content
    
    def fetch_health_canada_content(self) -> List[Dict]:
        """Fetch Health Canada regulatory updates"""
        content = []
        try:
            url = "https://www.canada.ca/en/health-canada/services/drugs-medication/cannabis/industry-licensees-applicants/licensed-cultivators-processors-sellers.html"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            content.append({
                'title': 'Health Canada Licensed Producers Database Updated',
                'content': 'Current listing of all federally licensed cannabis cultivators, processors, and sellers in Canada.',
                'source': 'Health Canada',
                'url': url,
                'published_date': datetime.now()
            })
        except Exception as e:
            logger.error(f"Error fetching Health Canada content: {e}")
        
        return content
    
    def fetch_duckduckgo_content(self) -> List[Dict]:
        """Fetch content using DuckDuckGo search for cannabis business news"""
        content = []
        
        # Cannabis business search terms
        search_queries = [
            "canadian cannabis news",
            "canada cannabis news", 
            "international cannabis news",
            "cannabis rescheduling",
            "cannabis business canada",
            "marijuana retail canada news",
            "canadian cannabis regulations",
            "cannabis earnings canada"
        ]
        
        try:
            with DDGS() as ddgs:
                for query in search_queries:
                    try:
                        # Search news from the past 7 days
                        results = ddgs.news(
                            query,  # First positional argument
                            region='ca-en',  # Canada English
                            safesearch='off',
                            timelimit='w',  # Past week
                            max_results=5  # Increased from 3 to 5 per query
                        )
                        
                        for result in results:
                            # Parse date - DuckDuckGo returns date in various formats
                            published_dt = datetime.now()
                            if result.get('date'):
                                try:
                                    # Try to parse the date string
                                    from dateutil import parser
                                    parsed_dt = parser.parse(result['date'])
                                    # Convert to naive datetime if it's timezone-aware
                                    if parsed_dt.tzinfo is not None:
                                        published_dt = parsed_dt.replace(tzinfo=None)
                                    else:
                                        published_dt = parsed_dt
                                except:
                                    # If parsing fails, use current time
                                    published_dt = datetime.now()
                            
                            # Skip content older than 7 days (both as naive datetimes)
                            if published_dt < (datetime.now() - timedelta(days=7)):
                                continue
                            
                            content.append({
                                'title': result.get('title', 'No title'),
                                'content': result.get('body', '')[:400],  # Limit content length
                                'source': result.get('source', 'Unknown Source'),
                                'url': result.get('url', ''),
                                'published_date': published_dt
                            })
                            
                        # Add delay between queries to be respectful
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Error searching DuckDuckGo for '{query}': {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error initializing DuckDuckGo search: {e}")
        
        logger.info(f"DuckDuckGo search completed. Found {len(content)} results.")
        return content
    
    def store_content(self, content_list: List[Dict]):
        """Store content in database with business relevance filtering"""
        if not content_list:
            return
        
        conn = sqlite3.connect(self.db_path)
        # Enable WAL mode for concurrency
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()
        stored_count = 0
        
        for item in content_list:
            try:
                if not self.should_include_content(item['title'], item.get('content', ''), item['source']):
                    continue
                
                content_hash = self.get_content_hash(item['title'], item.get('content', ''))
                relevance_score = self.calculate_business_relevance(item['title'], item.get('content', ''), item['source'])
                category = self.categorize_content(item['title'], item.get('content', ''), item['source'])
                
                cursor.execute('''
                    INSERT INTO content_feeds (title, content, source, category, url, published_date, content_hash, engagement_metrics, compliance_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['title'], item.get('content', ''), item['source'], category,
                    item['url'], item['published_date'], content_hash,
                    json.dumps({'business_relevance_score': relevance_score}), 'pending'
                ))
                
                if cursor.rowcount > 0:
                    stored_count += 1
                    
            except sqlite3.IntegrityError:
                pass  # Duplicate content
            except Exception as e:
                logger.error(f"Error storing content item: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"Content storing complete: {stored_count} new items stored.")
    
    def run_aggregation(self):
        """Run complete content aggregation from all sources"""
        logger.info("Starting content aggregation...")
        all_content = []
        
        # Fetch from all sources with error handling
        try:
            all_content.extend(self.fetch_health_canada_content())
        except Exception as e:
            logger.error(f"Failed to fetch from Health Canada: {e}")
            
        try:
            all_content.extend(self.fetch_reddit_content())
        except Exception as e:
            logger.error(f"Failed to fetch from Reddit: {e}")
            
        try:
            all_content.extend(self.fetch_rss_feeds())
        except Exception as e:
            logger.error(f"Failed to fetch from RSS Feeds: {e}")
            
        try:
            all_content.extend(self.fetch_duckduckgo_content())
        except Exception as e:
            logger.error(f"Failed to fetch from DuckDuckGo: {e}")
        
        self.store_content(all_content)
        logger.info(f"Aggregation finished. Total items fetched: {len(all_content)}")
        return len(all_content)
    
    def get_latest_content(self, limit: int = 20, approved_only: bool = True) -> List[Dict]:
        """Get latest content with improved sorting for user experience"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if approved_only:
            # CRITICAL FIX: Sort by approval_timestamp DESC for recently approved content,
            # then by published_date DESC for older approved content
            query = '''
                SELECT id, title, content, source, category, url, published_date, created_at, approval_timestamp
                FROM content_feeds 
                WHERE is_active = 1 AND compliance_status = 'approved'
                ORDER BY 
                    CASE 
                        WHEN approval_timestamp IS NOT NULL THEN approval_timestamp 
                        ELSE published_date 
                    END DESC 
                LIMIT ?
            '''
            params = (limit,)
        else:
            cutoff_time = datetime.now() - timedelta(hours=48)
            query = '''
                SELECT id, title, content, source, category, url, published_date, created_at, approval_timestamp
                FROM content_feeds 
                WHERE is_active = 1 AND published_date > ?
                ORDER BY published_date DESC 
                LIMIT ?
            '''
            params = (cutoff_time, limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_pending_content(self, hours: int = 48, limit: int = 50) -> List[Dict]:
        """Get pending content for curator with relevance scores"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cursor.execute('''
            SELECT id, title, content, source, category, url, published_date, created_at, 
                   compliance_status, engagement_metrics, priority
            FROM content_feeds 
            WHERE is_active = 1 AND published_date > ? AND compliance_status = 'pending'
            ORDER BY priority ASC, published_date DESC 
            LIMIT ?
        ''', (cutoff_time, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        content = []
        for row in rows:
            metrics = json.loads(row['engagement_metrics']) if row['engagement_metrics'] else {}
            content_dict = dict(row)
            content_dict['relevance_score'] = metrics.get('business_relevance_score', 0)
            content.append(content_dict)
        
        return content

aggregator = ContentAggregator()

# --- Static Pages & Health Check ---
@app.get("/")
async def serve_website(): return FileResponse("index.html")

@app.get("/about")
async def serve_about(): return FileResponse("about.html")

@app.get("/contact")
async def serve_contact(): return FileResponse("contact.html")

@app.get("/market-analysis")
async def serve_market_analysis(): return FileResponse("market-analysis.html")

@app.get("/website-intelligence")
async def serve_website_intelligence(): return FileResponse("website-intelligence.html")

@app.get("/health")
async def health_check(): return {"status": "healthy"}

@app.get("/intelligence-hub")
async def serve_intelligence_hub(): return FileResponse("intelligence-hub.html")

@app.get("/compliance-analysis")
async def serve_compliance_analysis(): return FileResponse("compliance-analysis.html")

@app.get("/pricing-analysis")
async def serve_pricing_analysis(): return FileResponse("pricing-analysis.html")

@app.get("/international-expansion")
async def serve_international_expansion(): return FileResponse("international-expansion.html")

# Catch-all route for HTML files
@app.get("/{filename}.html")
async def serve_html_files(filename: str):
    """Serve HTML files from the root directory"""
    import os
    file_path = f"{filename}.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

# --- Curator Interface Endpoint ---
@app.get("/curator")
async def serve_curator_interface(username: str = Depends(get_curator_credentials)):
    """Serves the integrated content curation HTML page (password protected)."""
    return FileResponse("curator.html")

# --- Blog Admin Interface Endpoint ---
@app.get("/blog-admin")
async def serve_blog_admin_interface():
    """Serves the CannTech blog administration HTML page."""
    return FileResponse("blog-admin.html")

# --- Newsletter API Endpoints ---
@app.post("/api/newsletter/subscribe")
async def subscribe_newsletter(subscription: NewsletterSubscription, request: Request):
    try:
        conn = sqlite3.connect('newsletter.db')
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM subscriptions WHERE email = ?", (subscription.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already subscribed")
        cursor.execute(
            'INSERT INTO subscriptions (email, consent_marketing, consent_privacy, age_verified, data_processing_consent) VALUES (?, ?, ?, ?, ?)',
            (subscription.email, True, True, True, True)
        )
        conn.commit()
        conn.close()
        return {"success": True, "message": "Successfully subscribed to newsletter!"}
    except Exception as e:
        logger.error(f"Subscription error: {e}")
        raise HTTPException(status_code=500, detail="Subscription failed.")

# --- Content & Curation API Endpoints ---
@app.post("/api/content/refresh")
async def refresh_content(background_tasks: BackgroundTasks, request: Request):
    """Triggers a background task to fetch new content from RSS feeds."""
    try:
        body = await request.json()
        reset_priorities = body.get('reset_priorities', False)
        logger.info(f"Reset priorities request: {reset_priorities}")
    except Exception as e:
        reset_priorities = False
        logger.info(f"No JSON body, defaulting to refresh: {e}")
        
    if reset_priorities:
        logger.info("Executing priority reset...")
        try:
            conn = sqlite3.connect(aggregator.db_path)
            conn.execute('PRAGMA journal_mode=WAL;')
            cursor = conn.cursor()
            cursor.execute("UPDATE content_feeds SET priority = 3")
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return {"success": True, "message": f"Reset {affected_rows} items to Normal priority."}
        except Exception as e:
            logger.error(f"Error resetting priorities: {e}")
            raise HTTPException(status_code=500, detail="Failed to reset priorities.")
    
    background_tasks.add_task(aggregator.run_aggregation)
    return {"success": True, "message": "Content refresh initiated in the background."}

@app.get("/api/content/latest")
async def get_latest_content_api(request: Request, limit: int = 20):
    """Get latest intelligence - approved content sorted by published_date (not approval time)"""
    try:
        conn = sqlite3.connect(aggregator.db_path)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all approved content from last 48 hours with custom priority sorting
        cursor.execute('''
            SELECT id, title, content, source, category, url, published_date, created_at, approval_timestamp, priority
            FROM content_feeds 
            WHERE is_active = 1 AND compliance_status = 'approved'
            AND datetime(published_date) >= datetime('now', '-48 hours')
            ORDER BY 
                CASE priority
                    WHEN 1 THEN 1  -- Breaking first
                    WHEN 2 THEN 2  -- High second
                    WHEN 3 THEN 3  -- Normal third (will be sorted alphabetically in Python)
                    WHEN 4 THEN 4  -- Low fourth
                    WHEN 5 THEN 5  -- Archive last
                    ELSE 3         -- Default to Normal
                END,
                CASE WHEN priority = 3 THEN title ELSE published_date END DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        content = [dict(row) for row in rows]
        return {"success": True, "content": content, "count": len(content)}
    except Exception as e:
        logger.error(f"Error getting latest content: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch latest content.")

@app.get("/api/content/pending")
async def get_pending_content(limit: int = 100):
    """Gets all content with a 'pending' status for the curator, including older content for better filtering."""
    try:
        conn = sqlite3.connect(aggregator.db_path)
        # Enable WAL mode for every connection
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get pending content from last 7 days instead of just recent content
        cutoff_time = datetime.now() - timedelta(days=7)
        cursor.execute("""
            SELECT * FROM content_feeds 
            WHERE compliance_status = 'pending' 
            AND (published_date > ? OR published_date IS NULL)
            ORDER BY created_at DESC 
            LIMIT ?
        """, (cutoff_time, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return {"success": True, "content": [dict(row) for row in rows]}
    except Exception as e:
        logger.error(f"Error getting pending content: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch pending content.")

@app.get("/api/content/banner-preview")
async def get_banner_preview():
    """Get the top 5 items that will appear in the banner (for curator visibility)"""
    try:
        content = aggregator.get_latest_content(limit=5, approved_only=True)
        return {"success": True, "banner_content": content}
    except Exception as e:
        logger.error(f"Error getting banner preview: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch banner preview.")

@app.get("/api/content/canvrio-picks")
async def get_canvrio_picks(limit: int = 5):
    """Get Canvrio's Picks - recently approved content sorted by approval_timestamp"""
    try:
        conn = sqlite3.connect(aggregator.db_path)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get content published more than 48 hours ago (Canvrio's Picks) with custom priority sorting
        cursor.execute('''
            SELECT id, title, content, source, category, url, published_date, created_at, approval_timestamp, priority
            FROM content_feeds 
            WHERE is_active = 1 AND compliance_status = 'approved' 
            AND approval_timestamp IS NOT NULL
            AND datetime(published_date) < datetime('now', '-48 hours')
            ORDER BY 
                CASE priority
                    WHEN 1 THEN 1  -- Breaking first
                    WHEN 2 THEN 2  -- High second
                    WHEN 3 THEN 3  -- Normal third (alphabetical)
                    WHEN 4 THEN 4  -- Low fourth
                    WHEN 5 THEN 5  -- Archive last
                    ELSE 3         -- Default to Normal
                END,
                CASE WHEN priority = 3 THEN title ELSE approval_timestamp END DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        content = [dict(row) for row in rows]
        return {"success": True, "content": content, "count": len(content)}
    except Exception as e:
        logger.error(f"Error getting Canvrio's picks: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch Canvrio's picks.")

# BULK ROUTES FIRST (more specific routes must come before generic {content_id} routes)
@app.post("/api/content/bulk/approve")
async def bulk_approve_content(payload: BulkUpdateRequest):
    """Approves a list of content items in bulk."""
    if not payload.content_ids:
        raise HTTPException(status_code=400, detail="No content IDs provided.")
    try:
        conn = sqlite3.connect(aggregator.db_path)
        # Enable WAL mode for every connection
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()
        placeholders = ', '.join('?' for _ in payload.content_ids)
        # CRITICAL FIX: Set approval_timestamp for bulk approvals  
        query = f"UPDATE content_feeds SET compliance_status = 'approved', approval_timestamp = CURRENT_TIMESTAMP WHERE id IN ({placeholders})"
        cursor.execute(query, payload.content_ids)
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Approved {cursor.rowcount} items."}
    except Exception as e:
        logger.error(f"Error in bulk approve: {e}")
        raise HTTPException(status_code=500, detail="Bulk approve failed.")

@app.post("/api/content/bulk/reject")
async def bulk_reject_content(payload: BulkUpdateRequest):
    """Rejects a list of content items in bulk."""
    if not payload.content_ids:
        raise HTTPException(status_code=400, detail="No content IDs provided.")
    try:
        conn = sqlite3.connect(aggregator.db_path)
        # Enable WAL mode for every connection
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()
        placeholders = ', '.join('?' for _ in payload.content_ids)
        query = f"UPDATE content_feeds SET compliance_status = 'rejected' WHERE id IN ({placeholders})"
        cursor.execute(query, payload.content_ids)
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Rejected {cursor.rowcount} items."}
    except Exception as e:
        logger.error(f"Error in bulk reject: {e}")
        raise HTTPException(status_code=500, detail="Bulk reject failed.")

@app.post("/api/content/bulk/reuse")
async def bulk_reuse_content(payload: BulkUpdateRequest):
    """Moves a list of approved content items back to pending."""
    if not payload.content_ids:
        raise HTTPException(status_code=400, detail="No content IDs provided.")
    try:
        conn = sqlite3.connect(aggregator.db_path)
        # Enable WAL mode for every connection
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()
        placeholders = ', '.join('?' for _ in payload.content_ids)
        query = f"UPDATE content_feeds SET compliance_status = 'pending', approval_timestamp = NULL WHERE id IN ({placeholders})"
        cursor.execute(query, payload.content_ids)
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Returned {cursor.rowcount} items to pending."}
    except Exception as e:
        logger.error(f"Error in bulk reuse: {e}")
        raise HTTPException(status_code=500, detail="Bulk reuse failed.")


# SINGLE CONTENT ROUTES (generic {content_id} routes come after specific routes)
@app.post("/api/content/{content_id}/approve")
async def approve_content(content_id: int):
    """Approves a single piece of content."""
    try:
        conn = sqlite3.connect(aggregator.db_path)
        # Enable WAL mode for every connection
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()
        # CRITICAL FIX: Set approval_timestamp when approving content
        cursor.execute("UPDATE content_feeds SET compliance_status = 'approved', approval_timestamp = CURRENT_TIMESTAMP WHERE id = ?", (content_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        conn.close()
        return {"success": True, "message": f"Content ID {content_id} approved."}
    except Exception as e:
        logger.error(f"Error approving content {content_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve content {content_id}.")

@app.post("/api/content/{content_id}/reject")
async def reject_content(content_id: int):
    """Rejects a single piece of content."""
    try:
        conn = sqlite3.connect(aggregator.db_path)
        # Enable WAL mode for every connection
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()
        cursor.execute("UPDATE content_feeds SET compliance_status = 'rejected' WHERE id = ?", (content_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        conn.close()
        return {"success": True, "message": f"Content ID {content_id} rejected."}
    except Exception as e:
        logger.error(f"Error rejecting content {content_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject content {content_id}.")

class PriorityRequest(BaseModel):
    priority: int

@app.post("/api/content/{content_id}/priority")
async def set_content_priority(content_id: int, priority_request: PriorityRequest):
    """Sets the priority for a specific content item (1=Breaking, 2=High, 3=Normal, 4=Low, 5=Archive)."""
    priority = priority_request.priority
    
    # Special case: content_id=0 and priority=3 means bulk reset all to Normal
    if content_id == 0 and priority == 3:
        try:
            conn = sqlite3.connect(aggregator.db_path)
            conn.execute('PRAGMA journal_mode=WAL;')
            cursor = conn.cursor()
            cursor.execute("UPDATE content_feeds SET priority = 3")
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return {"success": True, "message": f"Reset {affected_rows} items to Normal priority."}
        except Exception as e:
            logger.error(f"Error resetting priorities: {e}")
            raise HTTPException(status_code=500, detail="Failed to reset priorities.")
    
    if priority not in [1, 2, 3, 4, 5]:
        raise HTTPException(status_code=400, detail="Priority must be 1 (Breaking), 2 (High), 3 (Normal), 4 (Low), or 5 (Archive)")
    try:
        conn = sqlite3.connect(aggregator.db_path)
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()
        cursor.execute("UPDATE content_feeds SET priority = ? WHERE id = ?", (priority, content_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        conn.close()
        priority_names = {1: "Breaking", 2: "High", 3: "Normal", 4: "Low", 5: "Archive"}
        return {"success": True, "message": f"Content ID {content_id} priority set to {priority_names[priority]}."}
    except Exception as e:
        logger.error(f"Error setting priority for content {content_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set priority for content {content_id}.")

@app.get("/api/content/approved")
async def get_approved_content(limit: int = 100):
    """Gets all approved content for curator management."""
    try:
        conn = sqlite3.connect(aggregator.db_path)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, content, source, category, url, published_date, created_at, 
                   compliance_status, engagement_metrics, priority, approval_timestamp
            FROM content_feeds 
            WHERE is_active = 1 AND compliance_status = 'approved'
            ORDER BY priority ASC, approval_timestamp DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        content = []
        for row in rows:
            metrics = json.loads(row['engagement_metrics']) if row['engagement_metrics'] else {}
            content_dict = dict(row)
            content_dict['relevance_score'] = metrics.get('business_relevance_score', 0)
            content.append(content_dict)
            
        return {"success": True, "content": content}
    except Exception as e:
        logger.error(f"Error getting approved content: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch approved content.")

@app.post("/api/content/{content_id}/unapprove")
async def unapprove_content(content_id: int):
    """Moves approved content back to pending status."""
    try:
        conn = sqlite3.connect(aggregator.db_path)
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()
        cursor.execute("UPDATE content_feeds SET compliance_status = 'pending', approval_timestamp = NULL WHERE id = ?", (content_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        conn.close()
        return {"success": True, "message": f"Content ID {content_id} returned to pending."}
    except Exception as e:
        logger.error(f"Error unapproving content {content_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unapprove content {content_id}.")

@app.post("/api/content/{content_id}/reuse")
async def reuse_content(content_id: int):
    """Moves approved content back to pending, keeping original timestamp."""
    try:
        conn = sqlite3.connect(aggregator.db_path)
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()
        cursor.execute("UPDATE content_feeds SET compliance_status = 'pending', approval_timestamp = NULL WHERE id = ?", (content_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        conn.close()
        return {"success": True, "message": f"Content ID {content_id} returned to pending."}
    except Exception as e:
        logger.error(f"Error returning content {content_id} to pending: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to return content {content_id} to pending.")


# --- Main Execution ---
if __name__ == "__main__":
    # Production configuration for Render deployment
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "simple_main:app", 
        host="0.0.0.0",  # Changed for production
        port=port,       # Dynamic port for Render
        reload=False,    # Disabled for production
        log_level="info"
    )