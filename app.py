from flask import Flask, request, redirect, render_template_string
import sqlite3
import string
import random
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS url_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            original_url TEXT NOT NULL, 
            short_url TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>URL Shortener</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
        .container { max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 2px 2px 12px #aaa; }
        input[type="text"] { width: 80%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; }
        input[type="submit"] { padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
        input[type="submit"]:hover { background-color: #218838; }
        .result { margin-top: 20px; padding: 15px; background-color: #e9ecef; border-radius: 4px; }
        a { color: #007bff; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Python URL Shortener</h2>
        <form method="POST" action="/">
            <label for="url">Enter a long URL to shorten:</label><br>
            <input type="text" id="url" name="url" placeholder="https://www.example.com" required>
            <br>
            <input type="submit" value="Shorten URL">
        </form>
        {% if short_url %}
            <div class="result">
                Success! Your shortened URL is:<br><br>
                <a href="{{ short_url }}" target="_blank">{{ short_url }}</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        original_url = request.form['url']
        
        if not original_url.startswith(('http://', 'https://')):
            original_url = 'http://' + original_url

        short_id = generate_short_id()
        
        conn = sqlite3.connect('urls.db')
        c = conn.cursor()
        c.execute('INSERT INTO url_mapping (original_url, short_url) VALUES (?, ?)', (original_url, short_id))
        conn.commit()
        conn.close()
        
        short_url = request.host_url + short_id

    return render_template_string(HTML_TEMPLATE, short_url=short_url)

@app.route('/<short_id>')
def redirect_url(short_id):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('SELECT original_url FROM url_mapping WHERE short_url = ?', (short_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return redirect(result[0])
    else:
        return "<h1>404 - URL not found</h1>", 404

if __name__ == '__main__':
    app.run(debug=True)