from newspaper import Article
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
from rank import rank_biased_quotes
from model.generate_score import generate_scores
load_dotenv()


def extract_important_text(url):
    """
    Uses newspaper3k to download and parse an article from the given URL,
    returning the main article text which usually excludes extraneous content.
    """
    article = Article(url)
    article.download()
    article.parse()
    #print(article.text)
    return article.text

def extract_bias_score(text):
    return 0

def extract_information(text, url):
    """
    Calls the Gemini API using function calling to determine a political bias score
    from the provided article text. The function declaration 'extract_information' expects ai notes, quotes, and a serach query for similar articles
    """
    # Replace with your actual Gemini API key or set it as an environment variable.
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Define a function declaration for extracting the bias.
    extract_information_declaration = {
        "name": "extract_information",
        "description": (
            "Extracts a information from this article including ai notes, some quotes that may reflect bias and a search query for getting similar (unbiased) articles,  "
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ai_notes": {
                    "type": "string",
                    "description": "Give a brief description of the data set and potential bias that may be present"
                },
                "search_query":{
                    "type": "string",
                    "description": "Biased on the topics/events/ideas discussed in this article, please generate a search query that will return articles of similar type. For example, lets say this article is titled 'why trump tariffs are great', return a search query called trump tariffs/tariffs. Make sure to eliminate political bias in the search query but capture the relevant event/informatoin of the article."
                }

            },
            "required": ["ai_notes", "search_query"]
        }
    }

    # Set up the function calling tool and configuration.
    tools = types.Tool(function_declarations=[extract_information_declaration])
    config = types.GenerateContentConfig(tools=[tools])

    # Create a prompt instructing Gemini to determine the bias.
    prompt = (
        "Determine extract information from the article text. "
        "Return a function call to 'extract_information' with the parameter 'bias' set to an integer between -10 "
        "(extreme left) and 10 (extreme right). Only respond with the function call, nothing else.\n\n"
        f"Article Text: {text} Also return some notes about the article, some quotes in the article that may reflect bias, and a search query to pull similar articles on the same topic"
        "For the search query, ABSOLUTELY do not provide the opinion of the article, for example if the article critizies or supports a policy, only include the policy name in the search query."
        "You only need to include the idea/topic/policy discussed, not the authors opinon/interpretation of it."
    )

    #print(prompt)

    # Call Gemini using the generate_content method with the configuration.
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-001",
        contents=prompt,
        config=config
    )

    # Extract the function call from the first candidate's first part.
    candidate = response.candidates[0]
    function_call = candidate.content.parts[0].function_call

    # If a function call is returned and it matches our declaration, extract the bias.
    if function_call and function_call.name == "extract_information":
        bias = extract_bias_score(text)
        bias_quotes = rank_biased_quotes(text, n=10)
        bias_score = generate_scores(bias_quotes, url, use_local_model=True)
        ai_notes = function_call.args.get("ai_notes")
        search_query = function_call.args.get("search_query")
        search_results = get_search_results(search_query) if search_query else None
        scored_search_results = score_search_results(search_results)
        
        return bias, ai_notes, bias_quotes, search_query, scored_search_results, bias_score
    else:
        # If no valid function call is returned, default to a neutral bias.
        return 0

def get_search_results(query, n=5):
    params = {
        "q": query,
        "hl": "en",
        "gl": "us",
        "api_key": "1fa97dc33d9cb1985b6d9207fc2d739b80addd59136c86e24d5b4e0473a6ff98"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    urls = [result['link'] for result in results.get('organic_results', [])[:n]]
    return urls

def score_search_results(search_results):
    """
    Takes an array of URLs and returns an object with each URL having article metadata and score.
    
    Args:
        search_results (list): List of URLs to process
        
    Returns:
        dict: Dictionary with URLs as keys and article data + score as values
    """
    scored_results = {}
    
    for url in search_results:
        article_data = extract_article_metadata(url)
        score = extract_bias_score(article_data['text'])
        #bias_quotes = extract_bias_quotes(article_data['text'])
        
        scored_results[url] = {
            "score": score,
            "title": article_data['title'],
            "image_url": article_data['image_url'],
            "text_preview": article_data['text'][:150] + "..." if len(article_data['text']) > 150 else article_data['text']
        }
    
    return scored_results

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

def extract_article_metadata(url):
    """
    Extracts article text, title, and image URL with a focus on reliable image extraction
    similar to search engines.
    
    Args:
        url (str): The URL of the article
    
    Returns:
        dict: Dictionary containing text, title, and image_url
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Increase timeout from 10 to 20 seconds for slow sites
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract article text (your existing functionality)
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs])
        
        # Extract title (prioritize metadata)
        title = None
        meta_title = soup.find('meta', property='og:title') or soup.find('meta', name='twitter:title')
        if meta_title and meta_title.get('content'):
            title = meta_title['content']
        elif soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        elif soup.title:
            title = soup.title.text.strip()
        
        # Extract image URL (prioritize metadata - this is how Google does it)
        image_url = None
        
        # 1. Check Open Graph image (highest priority)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = urljoin(url, og_image['content'])
        
        # 2. Check Twitter Card image
        if not image_url:
            twitter_image = soup.find('meta', name='twitter:image')
            if twitter_image and twitter_image.get('content'):
                image_url = urljoin(url, twitter_image['content'])
        
        # 3. Check article:image
        if not image_url:
            article_image = soup.find('meta', property='article:image')
            if article_image and article_image.get('content'):
                image_url = urljoin(url, article_image['content'])
        
        # 4. Look for Schema.org JSON-LD data
        if not image_url:
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    import json
                    data = json.loads(script.string)
                    # Handle different schema structures
                    if isinstance(data, dict):
                        if 'image' in data:
                            image_src = data['image']
                            if isinstance(image_src, dict) and 'url' in image_src:
                                image_url = urljoin(url, image_src['url'])
                            elif isinstance(image_src, str):
                                image_url = urljoin(url, image_src)
                            break
                except:
                    continue
        
        # 5. Fall back to prominent images in the article
        if not image_url:
            # Look for large images at the top of the article
            main_content = soup.find('article') or soup.find('main') or soup
            for img in main_content.find_all('img', limit=5):  # Check only first 5 images
                if img.get('src') and not img['src'].endswith(('.gif', '.svg')):
                    # Skip tiny icons and decorative elements
                    if img.get('width') and img.get('height'):
                        try:
                            if int(img['width']) >= 300 or int(img['height']) >= 200:
                                image_url = urljoin(url, img['src'])
                                break
                        except ValueError:
                            # Width/height might be percentage or other format
                            if '%' not in img['width'] and '%' not in img['height']:
                                image_url = urljoin(url, img['src'])
                                break
                    # Check image file path for clues
                    elif 'header' in img.get('src', '').lower() or 'featured' in img.get('src', '').lower():
                        image_url = urljoin(url, img['src'])
                        break
        
        return {
            'text': text,
            'title': title or "Untitled Article",
            'image_url': image_url
        }
    
    except Exception as e:
        print(f"Error extracting data from {url}: {str(e)}")
        return {'text': '', 'title': f"Article at {url}", 'image_url': None}

