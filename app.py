import requests
import re
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    'Accept-Encoding': "gzip, deflate, br, zstd",
    'sec-ch-ua-platform': "\"Android\"",
    'sec-ch-ua': "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    'accept-language': "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
}

COUNTRIES = {
    'united-kingdom': {'code': '44', 'prefix': '447', 'name': 'United Kingdom'},
    'uk': {'code': '44', 'prefix': '447', 'name': 'United Kingdom'},
    'ireland': {'code': '353', 'prefix': '35389', 'name': 'Ireland'},
    'iceland': {'code': '354', 'prefix': '354', 'name': 'Iceland'},
    'france': {'code': '33', 'prefix': '336', 'name': 'France'},
    'germany': {'code': '49', 'prefix': '4915', 'name': 'Germany'},
    'spain': {'code': '34', 'prefix': '346', 'name': 'Spain'},
    'italy': {'code': '39', 'prefix': '39', 'name': 'Italy'},
    'netherlands': {'code': '31', 'prefix': '316', 'name': 'Netherlands'},
    'poland': {'code': '48', 'prefix': '48', 'name': 'Poland'},
    'russia': {'code': '7', 'prefix': '79', 'name': 'Russia'},
    'morocco': {'code': '212', 'prefix': '2126', 'name': 'Morocco'},
}

# المنصات المطلوبة فقط
PLATFORMS = {
    'telegram': ['Telegram', 'telegram', 'TG'],
    'whatsapp': ['WhatsApp', 'whatsapp', 'WA'],
    'tiktok': ['TikTok', 'tiktok'],
}

ACTIVE_NUMBERS = {}

def detect_platform(text):
    for platform, keywords in PLATFORMS.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                return platform
    return "Unknown"

def extract_codes(text):
    codes = []
    matches = re.findall(r'\b(\d{4,8})\b', text)
    for m in matches:
        if m not in codes:
            codes.append(m)
    return codes

class TempSMSAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.base_url = "https://veepn.com/online-sms"

    def get_first_number(self, country_key):
        url = f"{self.base_url}/countries/{country_key}/"
        try:
            resp = self.session.get(url).json()
            for num in resp:
                if not num.get('is_archive', False):
                    return {
                        'number': num.get('number'),
                        'full_number': num.get('full_number') or num.get('code'),
                        'country_code': COUNTRIES[country_key]['code']
                    }, None
            return None, f"No numbers for {country_key}"
        except Exception as e:
            return None, str(e)

    def get_sms(self, country_key, number):
        url = f"{self.base_url}/countries/{country_key}/{number}/"
        try:
            resp = self.session.get(url, params={'page': '1', 'count': '50'}).json()
            items = resp if isinstance(resp, list) else resp.get('data', [])
            msgs = []
            for m in items:
                text = m.get('text', '')
                codes = extract_codes(text)
                platform = detect_platform(text)
                if platform in ['telegram', 'whatsapp', 'tiktok']:
                    msgs.append({
                        'id': m.get('id'),
                        'text': text,
                        'codes': codes,
                        'platform': platform,
                        'time': m.get('created_at', '')
                    })
            return msgs, None
        except Exception as e:
            return None, str(e)

    def get_or_create(self, country_key):
        if country_key not in COUNTRIES:
            return None, f"Country '{country_key}' not found"
        if country_key in ACTIVE_NUMBERS:
            return ACTIVE_NUMBERS[country_key], None
        info, err = self.get_first_number(country_key)
        if err:
            return None, err
        ACTIVE_NUMBERS[country_key] = {
            'country': country_key,
            'name': COUNTRIES[country_key]['name'],
            'number': info['full_number'],
            'activated_at': datetime.now().isoformat(),
        }
        return ACTIVE_NUMBERS[country_key], None

sms_api = TempSMSAPI()

@app.route('/')
def home():
    return jsonify({
        'api': 'SMS API - Telegram/WhatsApp/TikTok',
        'countries': list(COUNTRIES.keys()),
        'endpoints': {
            'GET /numbers/{country}': 'رسائل الدولة',
            'GET /numbers/{country}/telegram': 'تيليجرام فقط',
            'GET /numbers/{country}/whatsapp': 'واتساب فقط',
            'GET /numbers/{country}/tiktok': 'تيك توك فقط',
        }
    })

@app.route('/numbers/<country>')
def get_country(country):
    country_key = country.lower()
    if country_key == 'uk':
        country_key = 'united-kingdom'
    if country_key not in COUNTRIES:
        return jsonify({'error': 'Country not found', 'available': list(COUNTRIES.keys())}), 404
    
    info, err = sms_api.get_or_create(country_key)
    if err:
        return jsonify({'error': err}), 404
    
    msgs, _ = sms_api.get_sms(country_key, info['number'])
    return jsonify({
        'country': country_key,
        'name': info['name'],
        'number': info['number'],
        'total': len(msgs) if msgs else 0,
        'messages': msgs[:20] if msgs else []
    })

@app.route('/numbers/<country>/telegram')
def telegram_only(country):
    country_key = country.lower()
    if country_key == 'uk':
        country_key = 'united-kingdom'
    if country_key not in COUNTRIES:
        return jsonify({'error': 'Country not found'}), 404
    
    info, err = sms_api.get_or_create(country_key)
    if err:
        return jsonify({'error': err}), 404
    
    msgs, _ = sms_api.get_sms(country_key, info['number'])
    tg = [m for m in msgs if m['platform'] == 'telegram'] if msgs else []
    return jsonify({
        'country': country_key,
        'number': info['number'],
        'platform': 'Telegram',
        'total': len(tg),
        'messages': tg[:10]
    })

@app.route('/numbers/<country>/whatsapp')
def whatsapp_only(country):
    country_key = country.lower()
    if country_key == 'uk':
        country_key = 'united-kingdom'
    if country_key not in COUNTRIES:
        return jsonify({'error': 'Country not found'}), 404
    
    info, err = sms_api.get_or_create(country_key)
    if err:
        return jsonify({'error': err}), 404
    
    msgs, _ = sms_api.get_sms(country_key, info['number'])
    wa = [m for m in msgs if m['platform'] == 'whatsapp'] if msgs else []
    return jsonify({
        'country': country_key,
        'number': info['number'],
        'platform': 'WhatsApp',
        'total': len(wa),
        'messages': wa[:10]
    })

@app.route('/numbers/<country>/tiktok')
def tiktok_only(country):
    country_key = country.lower()
    if country_key == 'uk':
        country_key = 'united-kingdom'
    if country_key not in COUNTRIES:
        return jsonify({'error': 'Country not found'}), 404
    
    info, err = sms_api.get_or_create(country_key)
    if err:
        return jsonify({'error': err}), 404
    
    msgs, _ = sms_api.get_sms(country_key, info['number'])
    tt = [m for m in msgs if m['platform'] == 'tiktok'] if msgs else []
    return jsonify({
        'country': country_key,
        'number': info['number'],
        'platform': 'TikTok',
        'total': len(tt),
        'messages': tt[:10]
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
