from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS
from extract_text import extract_article_metadata, extract_information  # Import both functions

app = Flask(__name__)
CORS(app, resources={r"/scrape": {"origins": ["http://localhost:3001", "https://ernienews-1031077341247.us-central1.run.app"]}}) # Enable CORS for multiple origins

# API endpoint to scrape, extract text, and calculate a bias score.
@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400
    try:
        # Extract metadata from the provided URL
        article_metadata = extract_article_metadata(url)
        
        # Check if we actually got article text
        if not article_metadata['text'].strip():
            return jsonify({'error': 'Could not extract text from the provided URL'}), 422
        
        # Pass the extracted text to the extract_information function
        bias, ai_notes, bias_quotes, search_query, scored_search_results = extract_information(article_metadata['text'])
        
        # Return all data to the frontend
        return jsonify({
            'original_article': {
                'url': url,
                'title': article_metadata['title'],
                'image_url': article_metadata['image_url'],
                'text_preview': article_metadata['text'][:150] + "..." if len(article_metadata['text']) > 150 else article_metadata['text']
            },
            'analysis': {
                'bias': bias,
                'ai_notes': ai_notes,
                'bias_quotes': bias_quotes,
                'search_query': search_query
            },
            'similar_articles': scored_search_results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Ensure it runs on port 5000