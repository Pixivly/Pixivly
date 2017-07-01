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
        return jsonify({'contents': [], 'next': '19990101'})
    json_file = 'media/%s.json'%(date)
    if not os.path.exists(json_file):
        json_data = fetch_json(date, 'daily', 1)
        if json_data is not None:
            with open(json_file, 'w') as f:
                json.dump(json_data, f)
        else:
            p_date = datetime.datetime.strptime(date, '%Y%m%d') - datetime.timedelta(days=1)
            p_date = p_date.strftime('%Y%m%d')
            return jsonify({'contents': [], 'next': p_date})
    else:
        with open(json_file, 'r') as f:
            json_data = json.load(f)
    return jsonify(json_data)


def fetch_json(date, mode, page):
    """
        Fetch json data at a specific date with mode and page
    """
    URL_PATTERN = 'https://www.pixiv.net/ranking.php?content=illust&format=json&date={0}&mode={1}&p={2}'
    url = URL_PATTERN.format(date, mode, page)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
            'Host': 'www.pixiv.net',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        res = requests.get(url, headers=headers, timeout=3)
    except requests.exceptions.Timeout as e:
        return None
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
