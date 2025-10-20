import os
import json
from flask import Flask, Response, request
from supabase import create_client, Client

app = Flask(__name__)

# Supabase setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route('/health')
def health_check():
    return 'OK'

@app.route('/albums')
def get_albums():
    page = int(request.args.get('page', 1))
    page_size = 20
    offset = (page - 1) * page_size
    response = supabase.table('albums').select("*").range(offset, offset + page_size - 1).execute()
    if response.data:
        return Response(json.dumps(response.data, ensure_ascii=False), mimetype='application/json')
    else:
        error_message = {"error": "No albums found or an error occurred."}
        return Response(json.dumps(error_message, ensure_ascii=False), mimetype='application/json', status=500)

@app.route('/albums/search')
def search_albums():
    keyword = request.args.get('keyword')
    if not keyword:
        return Response(json.dumps({"error": "Keyword not provided"}), mimetype='application/json', status=400)

    page = int(request.args.get('page', 1))
    page_size = 20
    offset = (page - 1) * page_size

    response = supabase.table('albums').select('*').or_(f'artist.ilike.%{keyword}%,title.ilike.%{keyword}%').range(offset, offset + page_size - 1).execute()

    if response.data:
        return Response(json.dumps(response.data, ensure_ascii=False), mimetype='application/json')
    else:
        error_message = {"error": "No albums found or an error occurred."}
        return Response(json.dumps(error_message, ensure_ascii=False), mimetype='application/json', status=500)

if __name__ == '__main__':
    app.run(debug=True)