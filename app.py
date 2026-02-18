from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
import re
import html
import requests
from dotenv import load_dotenv
from functools import wraps
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
except ImportError:
    # Fallback if flask-limiter is not installed
    Limiter = None
    get_remote_address = lambda: '127.0.0.1'

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(32).hex())
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Rate Limiting
if Limiter:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
else:
    # Fallback decorator if flask-limiter is not installed
    def limiter_limit(limit_str):
        def decorator(f):
            return f
        return decorator
    limiter = type('Limiter', (), {'limit': lambda self, limit_str: limiter_limit(limit_str)})()

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Security Headers
@app.after_request
def after_request(response):
    """Add security headers and cache control"""
    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https: http:; "
        "connect-src 'self' https://api.aladhan.com http://api.aladhan.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    response.headers["Content-Security-Policy"] = csp
    
    # Cache control for static files
    if request.endpoint == 'static':
        response.headers["Cache-Control"] = "public, max-age=3600"
    else:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    
    return response

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'ramadan_app'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def call_ai_image_api(prompt):
    """
    Placeholder function for AI image generation.
    
    This function should be replaced with your actual AI image generation API integration.
    
    Args:
        prompt (str): Text prompt describing the character styling
        
    Returns:
        str: URL of the generated image (placeholder for now)
    """
    # TODO: Integrate your AI image generation API here
    # For now, return a placeholder URL
    return "https://via.placeholder.com/512x512/9C6644/EDE0D4?text=AI+Image+Generation+Not+Configured"
    # except Exception as e:
    #     print(f"Hugging Face API Error: {e}")
    #     return "https://via.placeholder.com/512x512/9C6644/EDE0D4?text=Error+Generating+Image"
    
    # ============================================
    # Dummy response (للاختبار فقط) - معطل الآن
    # ============================================
    # هذا السطر معطل لأن Replicate مفعّل أعلاه
    # return "https://via.placeholder.com/512x512/9C6644/EDE0D4?text=Generated+Image"

@app.route('/favicon.ico')
def favicon():
    """Handle favicon request to prevent 404 errors"""
    from flask import send_from_directory, abort
    import os
    favicon_path = os.path.join(app.static_folder, 'favicon.ico')
    if os.path.exists(favicon_path):
        return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    else:
        # Return 204 No Content if favicon doesn't exist to prevent 404 errors
        return '', 204

@app.route('/loading')
def loading():
    """Loading page with video animation - redirects to main page after 3 seconds"""
    return render_template('loading.html')

@app.route('/')
def index():
    """Redirect to loading page (first time) or home page (if already seen)"""
    from flask import redirect, url_for
    # Always redirect to loading - JavaScript will handle showing it only once
    return redirect(url_for('loading'))

@app.route('/home')
def home():
    """Render the main page and fetch recent generations for gallery"""
    # Check if user should see loading (via JavaScript)
    connection = get_db_connection()
    recent_generations = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            # Optimized query - only fetch valid images
            query = """
                SELECT id, prompt, image_url, created_at 
                FROM generations 
                WHERE image_url IS NOT NULL AND image_url != '' AND image_url NOT LIKE 'http://%' AND image_url NOT LIKE 'https://%'
                ORDER BY created_at DESC 
                LIMIT 12
            """
            cursor.execute(query)
            recent_generations = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Error fetching generations: {e}")
        finally:
            try:
                if connection and connection.is_connected():
                    connection.close()
            except:
                pass
    
    return render_template('index.html', recent_generations=recent_generations)

def sanitize_input(text, max_length=1000):
    """Sanitize user input to prevent XSS and SQL Injection"""
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Escape HTML
    text = html.escape(text)
    
    return text.strip()

def validate_prompt(prompt):
    """Validate prompt input"""
    if not prompt or len(prompt.strip()) == 0:
        return False, "الرجاء إدخال نص الوصف"
    
    if len(prompt) > 1000:
        return False, "النص طويل جداً (الحد الأقصى 1000 حرف)"
    
    # Check for SQL injection patterns
    sql_patterns = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)',
        r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
        r'(\'|\"|;|--|\/\*|\*\/)',
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False, "النص المدخل غير صالح"
    
    return True, None

@app.route('/generate', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limiting: 10 requests per minute
def generate():
    """Handle image generation request"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'لم يتم استلام البيانات'
            }), 400
            
        prompt = data.get('prompt', '').strip()
        
        # Validate prompt
        is_valid, error_msg = validate_prompt(prompt)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Sanitize prompt
        prompt = sanitize_input(prompt, max_length=1000)
        
            # Call AI image generation API
        print(f"Generating image for prompt: {prompt}")
        try:
            image_url = call_ai_image_api(prompt)
            print(f"Generated image URL: {image_url}")
            
            # التأكد من أن URL صحيح (يقبل المسارات المحلية والمسارات الخارجية)
            if not image_url:
                raise ValueError("لم يتم إرجاع URL للصورة")
            
            # تنظيف المسار من الـ double slashes
            image_url = image_url.replace('//', '/')
                
        except Exception as api_error:
            print(f"API Error: {api_error}")
            error_message = str(api_error)
            
            # معالجة Rate Limit بشكل خاص
            if "تم تجاوز الحد" in error_message or "rate limit" in error_message.lower():
                return jsonify({
                    'success': False,
                    'error': error_message,
                    'error_type': 'rate_limit'
                }), 429
            else:
                return jsonify({
                    'success': False,
                    'error': error_message,
                    'error_type': 'api_error'
                }), 500
        
        # Save to database
        connection = get_db_connection()
        if not connection:
            # حتى لو قاعدة البيانات فشلت، نرجع الصورة
            return jsonify({
                'success': True,
                'image_url': image_url,
                'generation_id': None,
                'prompt': prompt,
                'warning': 'تم توليد الصورة لكن فشل حفظها في قاعدة البيانات'
            })
        
        try:
            cursor = connection.cursor()
            # Use parameterized query to prevent SQL Injection
            insert_query = """
                INSERT INTO generations (prompt, image_url) 
                VALUES (%s, %s)
            """
            # Ensure image_url is safe
            safe_image_url = sanitize_input(image_url, max_length=500)
            cursor.execute(insert_query, (prompt, safe_image_url))
            connection.commit()
            generation_id = cursor.lastrowid
            cursor.close()
            
            return jsonify({
                'success': True,
                'image_url': image_url,
                'generation_id': generation_id,
                'prompt': prompt
            })
        except Error as e:
            print(f"Error saving to database: {e}")
            # حتى لو قاعدة البيانات فشلت، نرجع الصورة
            return jsonify({
                'success': True,
                'image_url': image_url,
                'generation_id': None,
                'prompt': prompt,
                'warning': 'تم توليد الصورة لكن فشل حفظها في قاعدة البيانات'
            })
        finally:
            try:
                if connection and connection.is_connected():
                    connection.close()
            except:
                pass
            
    except Exception as e:
        print(f"Error in generate route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'حدث خطأ غير متوقع: {str(e)}'
        }), 500

def convert_to_12_hour(time_24h):
    """Convert 24-hour time format to 12-hour format with AM/PM"""
    if not time_24h or time_24h == '--:--':
        return '--:--'
    
    try:
        # Parse time (HH:MM)
        parts = time_24h.split(':')
        if len(parts) != 2:
            return time_24h
        
        hour = int(parts[0])
        minute = parts[1]
        
        # Convert to 12-hour format
        if hour == 0:
            return f"12:{minute} ص"
        elif hour < 12:
            return f"{hour}:{minute} ص"
        elif hour == 12:
            return f"12:{minute} م"
        else:
            return f"{hour - 12}:{minute} م"
    except:
        return time_24h

@app.route('/api/iftar-times', methods=['GET'])
@limiter.limit("30 per minute")  # Rate limiting: 30 requests per minute
def get_iftar_times():
    """Get Iftar times (Maghrib prayer) for all Arab countries from today until end of Ramadan"""
    from datetime import timedelta
    import calendar
    
    try:
        # Calculate Ramadan dates for current year
        today = datetime.now()
        current_year = today.year
        
        # Ramadan 2025: March 1 - March 30 (adjust based on actual Islamic calendar)
        # Ramadan 2026: February 18 - March 19
        # We'll calculate based on year
        ramadan_dates = {
            2025: {'start': (3, 1), 'end': (3, 30)},
            2026: {'start': (2, 18), 'end': (3, 19)},
            2027: {'start': (2, 7), 'end': (3, 8)},
            2024: {'start': (3, 11), 'end': (4, 9)}
        }
        
        # Get Ramadan dates for current year, default to 2025 if not found
        if current_year in ramadan_dates:
            ramadan_info = ramadan_dates[current_year]
            ramadan_start = datetime(current_year, ramadan_info['start'][0], ramadan_info['start'][1])
            ramadan_end = datetime(current_year, ramadan_info['end'][0], ramadan_info['end'][1])
        else:
            # Default to March 1-30 for unknown years
            ramadan_start = datetime(current_year, 3, 1)
            ramadan_end = datetime(current_year, 3, 30)
        
        # If today is before Ramadan, use Ramadan start
        if today.date() < ramadan_start.date():
            start_date = ramadan_start
        else:
            start_date = today
        
        # If today is after Ramadan, use Ramadan end
        if today.date() > ramadan_end.date():
            end_date = ramadan_end
        else:
            end_date = ramadan_end
        
        # Arab countries with their coordinates (latitude, longitude)
        arab_countries = {
            'مصر': {'lat': 30.0444, 'lng': 31.2357, 'city': 'Cairo'},
            'السعودية': {'lat': 24.7136, 'lng': 46.6753, 'city': 'Riyadh'},
            'الإمارات': {'lat': 24.4539, 'lng': 54.3773, 'city': 'Abu Dhabi'},
            'الكويت': {'lat': 29.3759, 'lng': 47.9774, 'city': 'Kuwait City'},
            'قطر': {'lat': 25.2854, 'lng': 51.5310, 'city': 'Doha'},
            'البحرين': {'lat': 26.0667, 'lng': 50.5577, 'city': 'Manama'},
            'عمان': {'lat': 23.5859, 'lng': 58.4059, 'city': 'Muscat'},
            'اليمن': {'lat': 15.3694, 'lng': 44.1910, 'city': 'Sanaa'},
            'الأردن': {'lat': 31.9539, 'lng': 35.9106, 'city': 'Amman'},
            'لبنان': {'lat': 33.8938, 'lng': 35.5018, 'city': 'Beirut'},
            'سوريا': {'lat': 33.5138, 'lng': 36.2765, 'city': 'Damascus'},
            'العراق': {'lat': 33.3152, 'lng': 44.3661, 'city': 'Baghdad'},
            'فلسطين': {'lat': 31.9522, 'lng': 35.2332, 'city': 'Jerusalem'},
            'السودان': {'lat': 15.5007, 'lng': 32.5599, 'city': 'Khartoum'},
            'ليبيا': {'lat': 32.8872, 'lng': 13.1913, 'city': 'Tripoli'},
            'تونس': {'lat': 36.8065, 'lng': 10.1815, 'city': 'Tunis'},
            'الجزائر': {'lat': 36.7538, 'lng': 3.0588, 'city': 'Algiers'},
            'المغرب': {'lat': 33.9716, 'lng': -6.8498, 'city': 'Rabat'},
            'موريتانيا': {'lat': 18.0735, 'lng': -15.9582, 'city': 'Nouakchott'},
            'جيبوتي': {'lat': 11.8251, 'lng': 42.5903, 'city': 'Djibouti'},
            'الصومال': {'lat': 2.0469, 'lng': 45.3182, 'city': 'Mogadishu'},
            'جزر القمر': {'lat': -11.6455, 'lng': 43.3333, 'city': 'Moroni'}
        }
        
        iftar_times = {}
        current_date = start_date
        
        # Generate dates from start to end
        dates = []
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        # Get prayer times for each country and date
        # Limit dates to 7 days for faster loading
        max_days = 7
        dates_to_fetch = dates[:max_days] if len(dates) > max_days else dates
        
        # Select most important countries for faster loading
        important_countries = {
            'مصر': arab_countries['مصر'],
            'السعودية': arab_countries['السعودية'],
            'الإمارات': arab_countries['الإمارات'],
            'الكويت': arab_countries['الكويت'],
            'قطر': arab_countries['قطر'],
            'البحرين': arab_countries['البحرين'],
            'عمان': arab_countries['عمان'],
            'الأردن': arab_countries['الأردن'],
            'لبنان': arab_countries['لبنان'],
            'سوريا': arab_countries['سوريا'],
            'العراق': arab_countries['العراق'],
            'فلسطين': arab_countries['فلسطين'],
            'السودان': arab_countries['السودان'],
            'ليبيا': arab_countries['ليبيا'],
            'تونس': arab_countries['تونس'],
            'الجزائر': arab_countries['الجزائر'],
            'المغرب': arab_countries['المغرب']
        }
        
        import concurrent.futures
        
        def get_prayer_times_for_country(country_name, coords, dates_list):
            """Get prayer times for a country - use individual requests for reliability"""
            country_times = {}
            
            if not dates_list:
                return (country_name, country_times)
            
            # Use individual requests for each date (more reliable)
            for date_str in dates_list:
                try:
                    url = f"http://api.aladhan.com/v1/timings/{date_str}"
                    params = {
                        'latitude': coords['lat'],
                        'longitude': coords['lng'],
                        'method': 4,  # Umm al-Qura, Makkah
                        'school': 0   # Shafi
                    }
                    
                    response = requests.get(url, params=params, timeout=4)
                    if response.status_code == 200:
                        data = response.json()
                        if 'data' in data and 'timings' in data['data']:
                            maghrib_time = data['data']['timings'].get('Maghrib', '--:--')
                            if maghrib_time and maghrib_time != '--:--' and maghrib_time != '':
                                # Format time (remove +00:00 if present)
                                maghrib_time = maghrib_time.split(' ')[0].split('+')[0].strip()
                                # Convert to 12-hour format
                                if maghrib_time and ':' in maghrib_time:
                                    maghrib_time_12h = convert_to_12_hour(maghrib_time)
                                    country_times[date_str] = maghrib_time_12h
                                else:
                                    country_times[date_str] = '--:--'
                            else:
                                country_times[date_str] = '--:--'
                        else:
                            country_times[date_str] = '--:--'
                    else:
                        country_times[date_str] = '--:--'
                except requests.exceptions.Timeout:
                    country_times[date_str] = '--:--'
                except Exception as e:
                    print(f"Error for {country_name} on {date_str}: {str(e)[:50]}")
                    country_times[date_str] = '--:--'
            
            return (country_name, country_times)
        
        # Use thread pool with more workers for faster parallel requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            futures = []
            for country_name, coords in important_countries.items():
                future = executor.submit(get_prayer_times_for_country, country_name, coords, dates_to_fetch)
                futures.append(future)
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    country_name, country_times = future.result()
                    if country_name and country_times:
                        iftar_times[country_name] = {
                            'times': country_times,
                            'city': important_countries[country_name]['city']
                        }
                except Exception as e:
                    pass  # Skip failed countries
        
        # Ensure all countries have entries (even if empty)
        for country_name in important_countries.keys():
            if country_name not in iftar_times:
                iftar_times[country_name] = {
                    'times': {},
                    'city': important_countries[country_name]['city']
                }
            # Fill missing dates
            for date_str in dates_to_fetch:
                if date_str not in iftar_times[country_name]['times']:
                    iftar_times[country_name]['times'][date_str] = '--:--'
        
        # Check if we have any data
        if not iftar_times:
            return jsonify({
                'success': False,
                'error': 'لم يتم الحصول على أي مواعيد'
            }), 500
        
        # Debug: Check if we have times
        total_times = sum(len(country_data.get('times', {})) for country_data in iftar_times.values())
        print(f"Total times collected: {total_times} for {len(iftar_times)} countries")
        
        # Return only the dates we fetched
        return jsonify({
            'success': True,
            'dates': dates_to_fetch,
            'countries': iftar_times,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_days': len(dates_to_fetch)
        })
        
    except Exception as e:
        print(f"Error in get_iftar_times: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
