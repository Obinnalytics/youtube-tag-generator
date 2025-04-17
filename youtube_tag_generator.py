import sys
import codecs
import unicodedata

# Set UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

class YouTubeTagGenerator:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YouTube API key not found")
        try:
            print("Initializing YouTube API...")
            self.youtube = build('youtube', 'v3', developerKey=api_key)
        except Exception as e:
            print(f"Error initializing YouTube API: {e}")
            raise

    def sanitize_text(self, text):
        """Sanitize text to handle special characters"""
        if not text:
            return ""
        # Normalize unicode characters
        text = unicodedata.normalize('NFKC', text)
        # Remove control characters
        text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")
        return text

    def sanitize_output(self, text):
        """Sanitize text for output, replacing special characters with standard ASCII"""
        if not text:
            return ""
        
        # Define character replacements
        replacements = {
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '—': '-',
            '–': '-',
            '…': '...',
            '•': '*',
            '©': '(c)',
            '®': '(r)',
            '™': '(tm)',
            '°': ' degrees',
            '×': 'x',
            '÷': '/',
            '≠': '!=',
            '≤': '<=',
            '≥': '>=',
        }
        
        # Replace special characters
        for special, normal in replacements.items():
            text = text.replace(special, normal)
        
        # Remove any remaining non-ASCII characters
        text = text.encode('ascii', 'ignore').decode('ascii')
        return text

    def get_video_category(self, query):
        """Determine the most likely video category based on keywords"""
        categories = {
            '1': ['music', 'song', 'audio', 'concert', 'band', 'singer'],
            '2': ['vlog', 'blog', 'lifestyle', 'daily', 'routine'],
            '10': ['gaming', 'game', 'gameplay', 'playthrough', 'walkthrough'],
            '15': ['pets', 'animals', 'wildlife', 'nature'],
            '17': ['sports', 'football', 'basketball', 'soccer', 'fitness'],
            '20': ['tutorial', 'how to', 'guide', 'tips', 'tricks'],
            '22': ['vlog', 'blog', 'people', 'life'],
            '23': ['comedy', 'funny', 'humor', 'entertainment'],
            '24': ['entertainment', 'show', 'performance'],
            '25': ['news', 'politics', 'current events'],
            '26': ['technology', 'tech', 'gadgets', 'review'],
            '27': ['education', 'learning', 'course', 'lecture'],
            '28': ['science', 'experiment', 'research'],
            '29': ['nonprofit', 'activism', 'charity']
        }
        
        query_lower = query.lower()
        for category_id, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category_id
        return '22'  # Default to People & Blogs if no match

    def calculate_title_relevance(self, title, query_words):
        """Calculate how relevant a title is to the search query"""
        title_words = set(word.lower() for word in title.split())
        matching_words = sum(1 for word in query_words if word in title_words)
        return matching_words / len(query_words) if query_words else 0

    def get_related_videos(self, query, max_results=50):
        try:
            query = self.sanitize_text(query)
            print(f"Searching for videos: {query}")
            
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='relevance'
            ).execute()
            
            if 'items' not in search_response:
                print("No items in search response")
                return []
            
            # Get video IDs
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get detailed video info
            videos_response = self.youtube.videos().list(
                part='statistics,snippet',
                id=','.join(video_ids)
            ).execute()
            
            if not videos_response.get('items'):
                return []
            
            return videos_response['items']
            
        except Exception as e:
            print(f"Error searching videos: {e}")
            return []

    def get_video_tags(self, video_id):
        try:
            video_id = self.sanitize_text(video_id)
            print(f"Getting tags for video: {video_id}")
            video_response = self.youtube.videos().list(
                part='snippet',
                id=video_id,
                fields='items(snippet(tags))'
            ).execute()

            if not video_response.get('items'):
                print(f"No items found for video {video_id}")
                return []

            tags = video_response['items'][0]['snippet'].get('tags', [])
            # Sanitize tags for output
            tags = [self.sanitize_output(tag) for tag in tags if tag]
            print(f"Found {len(tags)} tags for video {video_id}")
            return tags
        except Exception as e:
            print(f"Error getting video tags: {e}")
            return []

    def validate_tag(self, tag, query_words):
        """Validate tag quality based on multiple criteria"""
        tag_lower = tag.lower()
        
        # Length checks
        if len(tag) < 2 or len(tag) > 30:  # YouTube tag length limits
            return False, "length"
        
        # Check for spam patterns
        spam_patterns = ['subscribe', 'follow', 'check out', 'click here', 'watch more']
        if any(pattern in tag_lower for pattern in spam_patterns):
            return False, "spam"
        
        # Check for excessive punctuation
        punctuation_count = sum(1 for char in tag if char in '!?.,;:')
        if punctuation_count > 2:
            return False, "punctuation"
        
        # Check for keyword stuffing
        if tag_lower.count(' ') > 4:  # More than 5 words
            return False, "keyword_stuffing"
        
        return True, None

    def score_tag_quality(self, tag, query_words, title_words):
        """Score tag quality based on multiple factors"""
        tag_lower = tag.lower()
        score = 1.0
        
        # Relevance to query
        query_word_matches = sum(1 for word in query_words if word in tag_lower)
        score += query_word_matches * 0.5
        
        # Relevance to title
        title_word_matches = sum(1 for word in title_words if word in tag_lower)
        score += title_word_matches * 0.3
        
        # Length optimization (prefer tags between 10-20 chars)
        tag_length = len(tag)
        if 10 <= tag_length <= 20:
            score += 0.2
        
        # Prefer 2-3 word tags
        word_count = len(tag.split())
        if 2 <= word_count <= 3:
            score += 0.3
        
        return score

    def extract_keywords(self, text):
        """Extract meaningful keywords from text"""
        # Common words to filter out
        stop_words = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
                     'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 
                     'to', 'was', 'were', 'will', 'with'}
        
        # Split text and filter out stop words and short words
        words = text.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return set(keywords)

    def get_search_suggestions(self, query):
        """Get search suggestions from YouTube API"""
        try:
            # Get search suggestions using search.list
            suggestion_response = self.youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=10,
                relevanceLanguage='en',
                order='relevance'
            ).execute()
            
            suggestions = []
            if 'items' in suggestion_response:
                for item in suggestion_response['items']:
                    title = item['snippet']['title']
                    description = item['snippet']['description']
                    # Extract keywords from both title and description
                    suggestions.extend(self.extract_keywords(title))
                    suggestions.extend(self.extract_keywords(description))
            
            return set(suggestions)
        except Exception as e:
            print(f"Error getting search suggestions: {e}")
            return set()

    def analyze_tag_frequency(self, tags_list):
        """Analyze tag frequency and patterns across videos"""
        tag_stats = {}
        
        for tags in tags_list:
            for tag in tags:
                tag_lower = tag.lower()
                if tag_lower not in tag_stats:
                    tag_stats[tag_lower] = {
                        'original': tag,
                        'count': 0,
                        'videos': 0
                    }
                tag_stats[tag_lower]['count'] += 1
                tag_stats[tag_lower]['videos'] += 1
        
        return tag_stats

    def generate_tags(self, query):
        try:
            print(f"\nGenerating tags for query: {query}")
            
            # Get videos
            videos = self.get_related_videos(query)
            if not videos:
                print("No videos found")
                return None
            
            # Collect all tags with their frequency
            tag_stats = {}
            
            # Process tags from each video
            for video in videos:
                try:
                    video_id = video['id']
                    tags = self.get_video_tags(video_id)
                    
                    if tags:
                        # Count tag frequency
                        for tag in tags:
                            tag_lower = tag.lower()
                            if tag_lower not in tag_stats:
                                tag_stats[tag_lower] = {
                                    'original': tag,
                                    'count': 0,
                                    'views': 0
                                }
                            
                            tag_stats[tag_lower]['count'] += 1
                            tag_stats[tag_lower]['views'] += int(video['statistics'].get('viewCount', 0))
                
                except Exception as e:
                    print(f"Error processing video: {e}")
                    continue

            if not tag_stats:
                print("No valid tags found")
                return None

            # Sort tags by frequency and views
            sorted_tags = sorted(
                tag_stats.values(),
                key=lambda x: (x['count'], x['views']),
                reverse=True
            )

            # Get top 25 unique tags
            unique_tags = []
            seen = set()
            
            # First add tags containing the query
            query_words = set(query.lower().split())
            for tag_data in sorted_tags:
                if len(unique_tags) >= 25:
                    break
                    
                tag = tag_data['original']
                tag_lower = tag.lower()
                
                if tag_lower not in seen:
                    if any(word in tag_lower for word in query_words):
                        unique_tags.append(tag)
                        seen.add(tag_lower)
            
            # Then add remaining popular tags
            for tag_data in sorted_tags:
                if len(unique_tags) >= 25:
                    break
                    
                tag = tag_data['original']
                tag_lower = tag.lower()
                
                if tag_lower not in seen:
                    unique_tags.append(tag)
                    seen.add(tag_lower)

            print(f"Generated {len(unique_tags)} tags")
            return unique_tags[:25]

        except Exception as e:
            print(f"Error generating tags: {e}")
            return None

    def analyze_video(self, video_id):
        """Analyze a YouTube video and return detailed statistics"""
        try:
            # Get video details
            video_response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()

            if not video_response.get('items'):
                return None

            video = video_response['items'][0]
            snippet = video['snippet']
            statistics = video['statistics']
            
            # Format duration
            duration = video['contentDetails']['duration']
            duration_str = self._format_duration(duration)

            # Get tags and calculate tag stats
            tags = snippet.get('tags', [])
            tag_stats = {
                'total_tags': len(tags),
                'avg_tag_length': sum(len(tag) for tag in tags) / len(tags) if tags else 0,
                'tags_with_keywords': sum(1 for tag in tags if snippet['title'].lower() in tag.lower())
            }

            # Prepare analysis results
            analysis = {
                'title': snippet['title'],
                'description': snippet['description'],
                'publishedAt': snippet['publishedAt'],
                'duration': duration_str,
                'viewCount': statistics.get('viewCount', 0),
                'likeCount': statistics.get('likeCount', 0),
                'commentCount': statistics.get('commentCount', 0),
                'tags': tags,
                'tag_stats': tag_stats,
                'thumbnail': snippet['thumbnails']['high']['url']
            }

            return analysis

        except Exception as e:
            print(f"Error analyzing video: {e}")
            return None

    def _format_duration(self, duration):
        """Convert YouTube duration format to readable string"""
        import re
        import datetime

        # Remove 'PT' from duration
        duration = duration[2:]
        
        hours = 0
        minutes = 0
        seconds = 0

        # Extract hours, minutes, seconds
        time_dict = re.match(r'(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration).groups()
        
        if time_dict[0]:
            hours = int(time_dict[0])
        if time_dict[1]:
            minutes = int(time_dict[1])
        if time_dict[2]:
            seconds = int(time_dict[2])

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}" 