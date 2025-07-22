from flask import Flask, request, send_file
from flask_cors import CORS
from io import BytesIO, TextIOWrapper
import csv
import asyncio
from scraper import scrape_emails_from_url

app = Flask(__name__)
CORS(app, origins="*") 

@app.route('/api/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return {'error': 'URL manquante'}, 400

        emails = asyncio.run(scrape_emails_from_url(url))

        # ✅ Convertir le CSV texte en fichier binaire avec BytesIO
        mem = BytesIO()
        writer = csv.writer(TextIOWrapper(mem, encoding='utf-8', newline=''))
        writer.writerow(['Email'])
        for email in emails:
            writer.writerow([email])
        mem.seek(0)

        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name='emails.csv'
        )

    except Exception as e:
        print(f"[ERREUR FLASK] {e}")
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
