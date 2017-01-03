import os
import json
import datetime
import requests
from flask import Flask
from flask import abort, render_template
from flask import jsonify


app = Flask(__name__)

@app.route('/')
def index():
    date = datetime.datetime.today().date()-datetime.timedelta(days=1)
    date = date.strftime("%Y%m%d")
    return render_template('index.html', date=date)

@app.route('/<date>')
def date_json(date):
    try:
        date = datetime.datetime.strptime(date, '%Y%m%d').strftime('%Y%m%d')
    except:
        return jsonify({})
    json_file = 'media/%s.json'%(date)
    if not os.path.exists(json_file):
        json_data = fetch_json(date, 'daily', 1)
        if json_data is not None:
            with open(json_file, 'w') as f:
                json.dump(json_data, f)
        else:
            return jsonify({})
    else:
        with open(json_file, 'r') as f:
            json_data = json.load(f)
    return jsonify(json_data)


def fetch_json(date, mode, page):
    """
        Fetch json data at a specific date with mode and page
    """
    URL_PATTERN = 'http://www.pixiv.net/ranking.php?content=illust&format=json&date={0}&mode={1}&p={2}'
    url = URL_PATTERN.format(date, mode, page)
    res = requests.get(url)
    if res.status_code != 200:
        return None
    else:
        json_data = json.loads(res.content)
        _ = {'contents': [], 'mode': json_data['mode'], \
             'date': json_data['date'], 'next': json_data['prev_date']}
        for item in json_data['contents']:
            _['contents'].append({'id': item['illust_id'], 'url': item['url']})
        json_data = _
        return json_data if len(json_data['contents']) > 0 else None


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
