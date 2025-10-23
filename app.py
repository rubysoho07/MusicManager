import os
import json
from flask import Flask, Response, request
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

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


@app.route('/slash-command/albums/search', methods=['POST'])
def slash_search_albums():
    keyword = request.form.get('text')

    if not keyword:
        return Response("Keyword not provided", status=400)

    response = supabase.table('albums').select('*').or_(f'artist.ilike.%{keyword}%,title.ilike.%{keyword}%').execute()

    if response.data:
        results = []
        for album in response.data:
            results.append(f"{album['artist']} / {album['title']} / {album['media']}")
        
        response_text = '\n'.join(results)
    else:
        response_text = "No albums found."

    slack_response = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":cd: *검색 결과*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": response_text
                }
            }
        ]
    }
    return Response(json.dumps(slack_response, ensure_ascii=False), mimetype='application/json')


@app.route('/add-album', methods=['GET', 'POST'])
def add_album():
    if request.method == 'POST':
        artist = request.form.get('artist')
        title = request.form.get('title')
        media = request.form.get('media')

        if not all([artist, title, media]):
            return Response(json.dumps({"error": "All fields are required"}), mimetype='application/json', status=400)

        response = supabase.table('albums').insert({
            "artist": artist,
            "title": title,
            "media": media
        }).execute()

        if response.data:
            return Response(json.dumps(response.data, ensure_ascii=False), mimetype='application/json')
        else:
            error_message = {"error": "Failed to add album."}
            return Response(json.dumps(error_message, ensure_ascii=False), mimetype='application/json', status=500)
    else:
        return """
            <form method="post">
                <label for="artist">Artist:</label><br>
                <input type="text" id="artist" name="artist"><br>
                <label for="title">Title:</label><br>
                <input type="text" id="title" name="title"><br>
                <label for="media">Media:</label><br>
                <select id="media" name="media">
                    <option value="Tape">Tape</option>
                    <option value="CD" selected>CD</option>
                </select><br><br>
                <input type="submit" value="Submit">
            </form>
        """

@app.route('/slash-command/albums/add', methods=['POST'])
def slash_add_album_button():
    domain = os.environ.get('DOMAIN')
    slack_response = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":cd: *앨범을 추가하려면 아래 버튼을 클릭하세요*"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "앨범 추가"
                        },
                        "url": f'https://{domain}/add-album'
                    }
                ]
            }
        ]
    }
    return Response(json.dumps(slack_response, ensure_ascii=False), mimetype='application/json')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)