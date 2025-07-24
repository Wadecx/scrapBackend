from flask import Flask, request, send_file
from flask_cors import CORS
from io import BytesIO, StringIO
import csv
import asyncio
from scraper import scrape_emails_from_url

app = Flask(__name__)

# ✅ Fix CORS pour que ça fonctionne en prod (Render + Vercel)
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:3000",
    "https://scrap-frontend-phi.vercel.app"
]}})

@app.route('/api/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return {'error': 'URL manquante'}, 400

        emails = asyncio.run(scrape_emails_from_url(url))

        # ✅ On écrit d'abord dans un StringIO (texte)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Email'])
        for email in emails:
            writer.writerow([email])

        # ✅ Puis on convertit proprement en BytesIO (binaire)
        mem = BytesIO(output.getvalue().encode('utf-8'))
        output.close()
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
    # Pour le mode local
    app.run(host='0.0.0.0', port=5000, debug=True)
