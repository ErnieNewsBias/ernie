from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS
from extract_text import extract_article_metadata, extract_information  # Import both functions
import os
from concurrent.futures import ThreadPoolExecutor
from process import process_url
import threading
import time

app = Flask(__name__)

# Configure CORS to allow requests from multiple origins
CORS(app, resources={r"/scrape": {"origins": [
    "http://localhost:3000"
    "http://localhost:3001", 
    "https://ernienews-1031077341247.us-central1.run.app"
]}}) 

# API endpoint to scrape, extract text, and calculate a bias score.
@app.route('/scrape', methods=['GET'])
def scrape():
    thread_name = threading.current_thread().name
    print(f"[THREAD:{thread_name}] scrape: Received request for URL: {request.args.get('url', 'None')}")
    
    url = request.args.get('url')
    if not url:
        print(f"[THREAD:{thread_name}] scrape: Missing URL parameter")
        return jsonify({'error': 'URL parameter is required'}), 400
    
    try:
        print(f"[THREAD:{thread_name}] scrape: Processing URL: {url}")
        start_time = time.time()
        
        # Process URL using the multithreaded function
        ai_notes, similar_articles, bias_score, search_query = process_url(url)
        
        print(f"[THREAD:{thread_name}] scrape: URL processed in {time.time() - start_time:.2f} seconds")
        print(f"[THREAD:{thread_name}] scrape: Getting article metadata")
        
        # Extract article metadata for the response
        article_metadata = extract_article_metadata(url)
        
        # Calculate overall bias
        overall_bias = sum(bias_score.values()) / len(bias_score) if bias_score else 0
        print(f"[THREAD:{thread_name}] scrape: Overall bias score: {overall_bias}")
        
        # Prepare response
        print(f"[THREAD:{thread_name}] scrape: Preparing JSON response")
        response = jsonify({
            'original_article': {
                'url': url,
                'title': article_metadata['title'],
                'image_url': article_metadata['image_url'],
                'text_preview': article_metadata['text'][:150] + "..." if len(article_metadata['text']) > 150 else article_metadata['text']
            },
            'analysis': {
                'bias': overall_bias,
                'ai_notes': ai_notes,
                'bias_quotes': list(bias_score.keys()) if bias_score else [],
                'bias_score': bias_score,
                'search_query': search_query if search_query else ""
            },
            'similar_articles': similar_articles
        })
        
        print(f"[THREAD:{thread_name}] scrape: Request completed successfully in {time.time() - start_time:.2f} seconds")
        return response
        
    except Exception as e:
        print(f"[THREAD:{thread_name}] [ERROR] scrape: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Cloud Run sets this environment variable
    port = int(os.environ.get('PORT', 8080))
    # Must listen on 0.0.0.0 for Cloud Run
    app.run(host='0.0.0.0', port=port, debug=False)