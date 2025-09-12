from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from analyzer import analyze_cannabis_site
import csv
from datetime import datetime

app = FastAPI(title="Canvrio Cannabis Website Performance Analyzer", version="2.0.0")

# Simple CSV logging for leads
def log_lead(email, url, score):
    with open('leads.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), email, url, score])

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cannabis Website Performance Analyzer - Canvrio</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            line-height: 1.6;
            color: #1a202c;
            background: #ffffff;
        }
        
        h1, h2, h3 {
            font-family: 'Segoe UI', 'Roboto', 'Arial Black', sans-serif;
            letter-spacing: 1px;
            font-weight: 700;
        }
        
        :root {
            --canvrio-navy: #0C1B2A;
            --canvrio-green: #1F8A6A;
            --canvrio-accent: #14B8A6;
            --canvrio-light: #F4F6F8;
            --gray-100: #f7fafc;
            --gray-200: #e2e8f0;
            --gray-500: #718096;
            --gray-600: #4a5568;
            --gray-900: #1a202c;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem 0;
            background: linear-gradient(135deg, var(--canvrio-navy) 0%, var(--canvrio-green) 100%);
            color: white;
            border-radius: 16px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .analyzer-form {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            border: 2px solid var(--gray-200);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            font-weight: 600;
            color: var(--canvrio-navy);
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }
        
        input[type="url"], input[type="email"] {
            width: 100%;
            padding: 1rem;
            border: 2px solid var(--gray-200);
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        input[type="url"]:focus, input[type="email"]:focus {
            outline: none;
            border-color: var(--canvrio-accent);
            box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.1);
        }
        
        .analyze-btn {
            width: 100%;
            background: linear-gradient(135deg, var(--canvrio-accent) 0%, var(--canvrio-green) 100%);
            color: white;
            border: none;
            padding: 1.25rem;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 212, 170, 0.3);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 3rem;
        }
        
        .feature {
            background: var(--gray-100);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--gray-200);
        }
        
        .feature h3 {
            color: var(--canvrio-navy);
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        
        .feature p {
            color: var(--gray-600);
            font-size: 0.95rem;
        }
        
        .powered-by {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            color: var(--gray-500);
            font-size: 0.9rem;
        }
        
        /* Mobile Responsive Styles */
        @media (max-width: 768px) {
            .container {
                padding: 1rem 0.5rem;
            }
            
            .header {
                margin-bottom: 2rem;
                padding: 1.5rem 1rem;
            }
            
            .header h1 {
                font-size: 1.8rem;
                line-height: 1.2;
            }
            
            .header p {
                font-size: 1rem;
                margin-top: 0.5rem;
            }
            
            .analyzer-form {
                padding: 1.5rem 1rem;
                margin: 0 0.5rem;
            }
            
            .form-group {
                margin-bottom: 1.25rem;
            }
            
            label {
                font-size: 0.95rem;
                margin-bottom: 0.4rem;
            }
            
            input[type="url"], input[type="email"] {
                padding: 0.875rem;
                font-size: 1rem;
                border-radius: 6px;
            }
            
            .analyze-btn {
                padding: 1rem;
                font-size: 1rem;
                margin-top: 0.5rem;
            }
            
            .features {
                grid-template-columns: 1fr;
                gap: 1rem;
                margin-top: 2rem;
            }
            
            .feature {
                padding: 1.25rem 1rem;
            }
            
            .feature h3 {
                font-size: 1rem;
            }
            
            .feature p {
                font-size: 0.9rem;
            }
        }
        
        @media (max-width: 480px) {
            .header h1 {
                font-size: 1.5rem;
                letter-spacing: 1px;
            }
            
            .header p {
                font-size: 0.95rem;
            }
            
            .analyzer-form {
                padding: 1.25rem 0.75rem;
                margin: 0 0.25rem;
            }
            
            input[type="url"], input[type="email"] {
                padding: 0.75rem;
                font-size: 0.95rem;
            }
            
            .analyze-btn {
                padding: 0.875rem;
                font-size: 0.95rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="height: 80px; overflow: hidden; display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                <img src="canvrio-logo.png" alt="Canvrio" style="height: 250px; width: auto;">
            </div>
            <h1>Cannabis Website Performance Analyzer</h1>
            <p>Find Out How Your Website Speed & SEO Rank Against Competitors</p>
        </div>
        
        <form class="analyzer-form" method="post" action="/analyze">
            <div class="form-group">
                <label for="url">Cannabis Website URL</label>
                <input type="url" id="url" name="url" placeholder="https://your-dispensary.com" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email for Your Report</label>
                <input type="email" id="email" name="email" placeholder="owner@dispensary.com" required>
            </div>
            
            <button type="submit" class="analyze-btn">Analyze Performance</button>
        </form>
        
        <div class="features">
            <div class="feature">
                <h3>Real-World Speed Test</h3>
                <p>We test your site's loading speed just like a real customer would, showing you exactly why visitors might be leaving.</p>
            </div>
            <div class="feature">
                <h3>Competitive Benchmarking</h3>
                <p>See how your performance stacks up against other cannabis websites in your market.</p>
            </div>
            <div class="feature">
                <h3>Actionable SEO Insights</h3>
                <p>Get a simple, clear report on the technical SEO factors that help you rank higher on Google.</p>
            </div>
        </div>
        
        <div class="powered-by">
            Powered by <strong>Canvrio</strong> | Cannabis Industry Intelligence
        </div>
    </div>
</body>
</html>
    """

@app.post("/analyze", response_class=HTMLResponse)
def analyze(url: str = Form(...), email: str = Form(...)):
    # Analyze the website using the updated performance analyzer
    result = analyze_cannabis_site(url)
    
    # Log the lead with the new performance score
    log_lead(email, url, result.get('score', 0))
    
    # Dynamically build the HTML for our new performance metrics grid
    metrics_html = ""
    
    # Metric 1: Page Load Speed
    metrics_html += f"""
    <div class="result-item">
        <h3>Page Load Speed</h3>
        <span class="status {'pass' if result['load_time'] < 3 else 'fail'}">
            {result.get('load_time', 0):.1f}s
        </span>
        <p>Measures the time it takes for your page to become visible to a user.</p>
    </div>
    """
    
    # Metric 2: Mobile Performance
    metrics_html += f"""
    <div class="result-item">
        <h3>Mobile Performance</h3>
        <span class="status {'pass' if result.get('mobile_friendly') else 'fail'}">
            {'✓ OPTIMIZED' if result.get('mobile_friendly') else '✗ NEEDS WORK'}
        </span>
        <p>Checks for a mobile-friendly design, crucial for the 60% of users on phones.</p>
    </div>
    """
    
    # Metric 3: SEO Security (HTTPS)
    metrics_html += f"""
    <div class="result-item">
        <h3>SEO Security (HTTPS)</h3>
        <span class="status {'pass' if result.get('has_https') else 'fail'}">
            {'✓ SECURE' if result.get('has_https') else '✗ INSECURE'}
        </span>
        <p>A secure site is a requirement for ranking high on Google.</p>
    </div>
    """

    # Metric 4: Conversion: Contact Info
    metrics_html += f"""
    <div class="result-item">
        <h3>Conversion: Contact Info</h3>
        <span class="status {'pass' if result.get('has_contact') else 'fail'}">
            {'✓ VISIBLE' if result.get('has_contact') else '✗ HIDDEN'}
        </span>
        <p>Measures if customers can easily find ways to contact you.</p>
    </div>
    """
    
    # Metric 5: SEO: Title Tag
    title_info = result.get('title_tag', {'optimal': False, 'text': 'Missing'})
    metrics_html += f"""
    <div class="result-item">
        <h3>SEO: Title Tag</h3>
        <span class="status {'pass' if title_info.get('optimal') else 'fail'}">
            {'✓ OPTIMAL' if title_info.get('optimal') else '✗ NEEDS IMPROVEMENT'}
        </span>
        <p>A well-written title tag is critical for search engine ranking.</p>
    </div>
    """
    
    # Metric 6: SEO: Meta Description
    meta_info = result.get('meta_description', {'optimal': False, 'text': 'Missing'})
    metrics_html += f"""
    <div class="result-item">
        <h3>SEO: Meta Description</h3>
        <span class="status {'pass' if meta_info.get('optimal') else 'fail'}">
            {'✓ OPTIMAL' if meta_info.get('optimal') else '✗ MISSING'}
        </span>
        <p>This text appears in Google search results and encourages clicks.</p>
    </div>
    """
    
    # Metric 7: SEO: Main Heading (H1)
    h1_info = result.get('h1_tag', {'optimal': False, 'count': 0})
    metrics_html += f"""
    <div class="result-item">
        <h3>SEO: Main Heading (H1)</h3>
        <span class="status {'pass' if h1_info.get('optimal') else 'fail'}">
            {'✓ OPTIMAL' if h1_info.get('optimal') else '✗ NEEDS FIX'}
        </span>
        <p>A single, clear H1 heading tells Google what your page is about.</p>
    </div>
    """

    # Return the final results page
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Report - Canvrio</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            line-height: 1.6;
            color: #1a202c;
            background: #ffffff;
        }}
        
        h1, h2, h3 {{
            font-family: 'Segoe UI', 'Roboto', 'Arial Black', sans-serif;
            letter-spacing: 1px;
            font-weight: 700;
        }}
        
        :root {{
            --canvrio-navy: #0C1B2A;
            --canvrio-green: #1F8A6A;
            --canvrio-accent: #14B8A6;
            --canvrio-light: #F4F6F8;
            --gray-100: #f7fafc;
            --gray-200: #e2e8f0;
            --gray-500: #718096;
            --gray-600: #4a5568;
            --gray-900: #1a202c;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, var(--canvrio-navy) 0%, var(--canvrio-green) 100%);
            color: white;
            border-radius: 16px;
        }}
        
        .score-card {{
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            border: 3px solid var(--canvrio-accent);
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .score {{
            font-size: 4rem;
            font-weight: 900;
            color: var(--canvrio-accent);
            margin: 1rem 0;
        }}
        
        .grade {{
            font-size: 1.5rem;
            color: var(--canvrio-navy);
            font-weight: 600;
        }}
        
        .results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        
        .result-item {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--canvrio-accent);
        }}
        
        .result-item h3 {{
            color: var(--canvrio-navy);
            margin-bottom: 0.5rem;
        }}
        
        .status {{
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
        }}
        
        .status.pass {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status.fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .cta-section {{
            background: var(--canvrio-light);
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin: 3rem 0;
        }}
        
        .cta-btn {{
            background: linear-gradient(135deg, var(--canvrio-accent) 0%, var(--canvrio-green) 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 1rem 0.5rem;
            transition: transform 0.2s ease;
        }}
        
        .cta-btn:hover {{
            transform: translateY(-2px);
        }}
        
        .back-btn {{
            background: var(--gray-500);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            text-decoration: none;
            display: inline-block;
            margin-top: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Performance Report</h1>
            <p>Results for: {url}</p>
        </div>
        
        <div class="score-card">
            <div class="score">{result.get('score', 0)}</div>
            <div class="grade">Grade: {'A' if result.get('score', 0) >= 90 else 'B' if result.get('score', 0) >= 80 else 'C' if result.get('score', 0) >= 70 else 'D'}</div>
            <p>Overall Website Performance Score</p>
        </div>
        
        <div class="results-grid">
            {metrics_html}
        </div>
        
        <div class="cta-section">
            <h2>Is Your Website Fast Enough to Compete?</h2>
            <p>Slow websites lose 40% of their visitors before the page even loads. Our analysis identifies the key performance issues that could be costing you customers and provides actionable steps to improve your revenue.</p>
            
            <div style="background: rgba(255,255,255,0.9); padding: 1rem; border-radius: 8px; margin: 1rem 0; font-size: 0.9rem; color: var(--canvrio-navy);">
                <strong>💰 Performance Note:</strong> A 1-second delay in page load time can lead to a 7% reduction in conversions. We show you where to find those seconds.
            </div>
            
            <a href="mailto:hello@canvrio.com?subject=Website Performance Report Follow-up for {url}&body=Hi! I just analyzed {url} and got a performance score of {result.get('score', 0)}/100. I'd like to discuss how to improve my website's speed and SEO to increase sales." class="cta-btn">
                Book a Free Consultation
            </a>
            
            <a href="/" class="back-btn">Analyze Another Site</a>
        </div>
    </div>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)