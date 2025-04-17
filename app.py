from flask import Flask, render_template, request, jsonify, send_from_directory
import json
from youtube_tag_generator import YouTubeTagGenerator
import os
from dotenv import load_dotenv
from datetime import datetime
from blog_feed import BlogFeed

app = Flask(__name__)

# Enhanced UTF-8 encoding configuration
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json;charset=utf-8'

# Custom JSON encoder to handle UTF-8
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

app.json_encoder = CustomJSONEncoder

# Load environment variables
load_dotenv()

# Initialize the generator with API key
tag_generator = YouTubeTagGenerator()

# Initialize blog feed
blog_feed = BlogFeed()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/generate')
def index():
    return render_template('index.html')

@app.route('/generator')
def generator_page():
    return render_template('index.html')

@app.route('/generate-tags', methods=['POST'])
def generate_tags():
    try:
        query = request.form.get('query', '').strip()
        if not query:
            print("No query provided")
            return jsonify({'error': 'No query provided'})
        
        print(f"\nProcessing query: {query}")
        tags = tag_generator.generate_tags(query)
        
        if not tags:
            print("No tags found")
            return jsonify({'error': 'No tags found for this query'})
        
        print(f"Returning {len(tags)} tags")
        return jsonify({'tags': tags})
    except Exception as e:
        print(f"Error in generate_tags route: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/favicon', 'favicon.ico')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        try:
            video_url = request.form.get('video_url')
            print(f"Received URL: {video_url}")
            
            if not video_url:
                return jsonify({'error': 'Please enter a YouTube URL'})
            
            # Extract video ID from URL
            video_id = extract_video_id(video_url)
            print(f"Extracted video ID: {video_id}")
            
            if not video_id:
                return jsonify({'error': 'Could not find video ID in URL. Please use a valid YouTube URL'})
            
            # Get video analysis
            analysis = tag_generator.analyze_video(video_id)
            print(f"Analysis result: {analysis}")
            
            if not analysis:
                return jsonify({'error': 'Could not analyze video. Please check the URL and try again'})
            
            # Validate required fields
            required_fields = ['title', 'description', 'thumbnail', 'viewCount', 'likeCount', 'commentCount', 'duration']
            missing_fields = [field for field in required_fields if field not in analysis]
            
            if missing_fields:
                print(f"Missing fields in analysis: {missing_fields}")
                return jsonify({'error': f'Incomplete video data. Missing: {", ".join(missing_fields)}'})
            
            return jsonify(analysis)
        except Exception as e:
            print(f"Error in analyze route: {e}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
    return render_template('analyze.html')

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    import re
    print(f"Extracting ID from URL: {url}")  # Debug print
    
    # Handle full YouTube URLs
    if "youtube.com/watch" in url:
        try:
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            return parse_qs(parsed_url.query)['v'][0]
        except Exception as e:
            print(f"Error parsing YouTube URL: {e}")
            return None
    
    # Handle shortened youtu.be URLs
    elif "youtu.be" in url:
        try:
            return url.split("/")[-1].split("?")[0]
        except Exception as e:
            print(f"Error parsing shortened URL: {e}")
            return None
            
    print("No video ID found in URL")
    return None

@app.route('/blog-posts')
def get_blog_posts():
    try:
        posts = blog_feed.get_posts(limit=6)
        return jsonify({'posts': posts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 