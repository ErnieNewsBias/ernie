from flask import Flask, request, jsonify
from extract_text import extract_important_text, extract_score  # Import both functions

app = Flask(__name__)

# API endpoint to scrape, extract text, and calculate a bias score.
@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400
    try:
        # Extract important text from the provided URL
        text = extract_important_text(url)
        # Print the extracted text to the server console (not sent to the client)
        #print("Extracted Text:\n", text)
        # Pass the extracted text to the extract_score function
        bias, ai_notes, bias_quotes = extract_score(text)
        # Return only the bias score to the frontend
        return jsonify({'bias': bias, "ai_notes": ai_notes, "bias_quotes": bias_quotes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)