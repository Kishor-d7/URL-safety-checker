from flask import Flask, request, render_template, jsonify
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import webtech

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check_url', methods=['POST'])
def check_url():
    url = request.form.get('url')
    piracy_warning = detect_piracy(url)
    fake_warning = detect_fake_url(url)
    technologies = get_technologies(url)
    return jsonify({'piracy_warning': piracy_warning, 'fake_warning': fake_warning, 'technologies': technologies})

def detect_piracy(url):
    piracy_keywords = ["piracy", "torrent", "free movies", "anime streaming", "crack", "warez", "hianime", "aniwatch", "9anime"]
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return "Warning: This URL returned a non-200 status code."

        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text().lower()

        for keyword in piracy_keywords:
            if keyword in text_content:
                return "Warning: This URL is associated with piracy and may be risky!"

        return "This URL does not appear to be associated with piracy."
    except requests.RequestException:
        return "Warning: Could not access the URL. It may be unsafe."

def detect_fake_url(url):
    parsed_url = urlparse(url)

    if not parsed_url.scheme:
        return "Invalid URL format. Please include the scheme (http or https)."

    if parsed_url.scheme != 'https':
        return "Warning: This URL is not using HTTPS, which may be less secure."

    fake_keywords = ["fake", "phishing", "scam", "fraud", "malicious"]
    for keyword in fake_keywords:
        if keyword in url.lower():
            return "Warning: This URL may be fake or malicious!"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return "Warning: This URL returned a non-200 status code."

        if 'content-type' in response.headers and 'text/html' not in response.headers['content-type'].lower():
            return "Warning: This URL does not appear to be an HTML page."

        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        for script in scripts:
            if script.get('src') and any(kw in script.get('src').lower() for kw in ['ad', 'track', 'virus']):
                return "Warning: This URL contains scripts from potentially malicious sources."

        return "This URL seems safe."
    except requests.RequestException:
        return "Warning: Could not access the URL. It may be unsafe."

def get_technologies(url):
    try:
        webtech_analyzer = webtech.WebTech(timeout=10)
        result = webtech_analyzer.start_from_url(url)
        
        technologies = [tech['name'] for tech in result['tech']]
        return technologies if technologies else ["No specific technologies detected."]
    except Exception as e:
        return [str(e)]

if __name__ == '__main__':
    app.run(debug=True)
