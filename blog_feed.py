import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import re

class BlogFeed:
    def __init__(self, rss_url="https://blog.simpleseotags.io/feed/"):
        self.rss_url = rss_url
        self.cache = {}
        self.cache_time = 0
        self.cache_duration = 1800  # 30 minutes in seconds
        self.default_limit = 6  # Changed from 5 to 6

    def get_posts(self, limit=6):
        """Get latest blog posts from RSS feed with caching"""
        current_time = time.time()
        
        # Return cached posts if they're still fresh
        if self.cache and (current_time - self.cache_time) < self.cache_duration:
            return self.cache[:limit]
            
        try:
            response = requests.get(self.rss_url)
            response.raise_for_status()  # Raise exception for bad status codes
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Find all items/entries (works for both RSS and Atom feeds)
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            posts = []
            for item in items[:6]:
                # Extract post data (handle both RSS and Atom formats)
                title = self._get_text(item, './/title')
                link = self._get_text(item, './/link')
                description = self._get_text(item, './/description') or self._get_text(item, './/content')
                pub_date = self._get_text(item, './/pubDate') or self._get_text(item, './/published')
                author = self._get_text(item, './/author') or self._get_text(item, './/creator') or 'SimpleSEOTags'
                
                # Extract image from content
                image = self._extract_image(description)
                
                # Parse date
                try:
                    date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                except:
                    try:
                        date_obj = datetime.strptime(pub_date, '%Y-%m-%dT%H:%M:%SZ')
                    except:
                        date_obj = datetime.now()
                
                post = {
                    'title': title,
                    'link': link,
                    'description': self._clean_html(description),
                    'date': date_obj.isoformat(),
                    'author': author,
                    'image': image
                }
                posts.append(post)
            
            # Update cache with exactly 6 posts
            self.cache = posts[:6]
            self.cache_time = current_time
            
            return posts[:6]
            
        except Exception as e:
            print(f"Error fetching blog feed: {e}")
            return []

    def _get_text(self, element, xpath):
        """Safely extract text from XML element"""
        try:
            found = element.find(xpath)
            return found.text if found is not None else ''
        except:
            return ''

    def _clean_html(self, text):
        """Remove HTML tags from text"""
        if not text:
            return ''
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    def _extract_image(self, html_content):
        """Extract the first image from HTML content"""
        try:
            if html_content:
                img_match = re.search(r'<img[^>]+src="([^">]+)"', html_content)
                if img_match:
                    return img_match.group(1)
        except Exception as e:
            print(f"Error extracting image: {e}")
        return None 