from flask import Flask, jsonify, request
import requests
import re
from datetime import datetime

app = Flask(__name__)

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    'Accept-Encoding': "gzip, deflate, br, zstd",
    'sec-ch-ua-platform': "\"Android\"",
    'save-data': "on",
    'sec-ch-ua': "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    'sec-ch-ua-mobile': "?0",
    'sec-fetch-site': "same-origin",
    'sec-fetch-mode': "cors",
    'sec-fetch-dest': "empty",
    'accept-language': "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    'priority': "u=1, i"
}

COUNTRIES = {
    'united-kingdom': {'code': '44', 'prefix': '447', 'name': 'United Kingdom', 'display': 'United Kingdom'},
    'uk': {'code': '44', 'prefix': '447', 'name': 'United Kingdom', 'display': 'United Kingdom'},
    'ireland': {'code': '353', 'prefix': '35389', 'name': 'Ireland', 'display': 'Ireland'},
    'iceland': {'code': '354', 'prefix': '354', 'name': 'Iceland', 'display': 'Iceland'},
    'france': {'code': '33', 'prefix': '336', 'name': 'France', 'display': 'France'},
    'germany': {'code': '49', 'prefix': '4915', 'name': 'Germany', 'display': 'Germany'},
    'spain': {'code': '34', 'prefix': '346', 'name': 'Spain', 'display': 'Spain'},
    'italy': {'code': '39', 'prefix': '39', 'name': 'Italy', 'display': 'Italy'},
    'netherlands': {'code': '31', 'prefix': '316', 'name': 'Netherlands', 'display': 'Netherlands'},
    'poland': {'code': '48', 'prefix': '48', 'name': 'Poland', 'display': 'Poland'},
    'russia': {'code': '7', 'prefix': '79', 'name': 'Russia', 'display': 'Russia'},
}

ACTIVE_NUMBERS = {}

class TempSMSAPI:
    def __init__(self):
        self.base_url = "https://veepn.com/online-sms"
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def get_first_available_number(self, country_key):
        url = f"{self.base_url}/countries/{country_key}/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            numbers = response.json()
            
            for num in numbers:
                if not num.get('is_archive', False):
                    return {
                        'number': num.get('number'),
                        'full_number': num.get('full_number') or num.get('code'),
                        'country_code': COUNTRIES[country_key]['code']
                    }, None
            
            return None, f"No active numbers found for {country_key}"
        except Exception as e:
            return None, str(e)
    
    def get_sms_for_number(self, country_key, number):
        url = f"{self.base_url}/countries/{country_key}/{number}/"
        params = {'page': '1', 'count': '50'}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for msg in data.get('data', []):
                codes = re.findall(r'\b(\d{4,8})\b', msg.get('text', ''))
                msg['verification_codes'] = codes if codes else []
                
                service_match = re.search(r'(Apple|Google|Amazon|Telegram|TikTok|Coinbase|Claude|NVIDIA|Samsung)', msg.get('text', ''), re.IGNORECASE)
                msg['service'] = service_match.group(1) if service_match else 'Unknown'
            
            return data, None
        except Exception as e:
            return None, str(e)
    
    def get_or_create_active_number(self, country_key):
        if country_key not in COUNTRIES:
            return None, f"Country '{country_key}' not found"
        
        if country_key in ACTIVE_NUMBERS:
            return ACTIVE_NUMBERS[country_key], None
        
        number_info, error = self.get_first_available_number(country_key)
        if error:
            return None, error
        
        ACTIVE_NUMBERS[country_key] = {
            'country': country_key,
            'country_name': COUNTRIES[country_key]['name'],
            'number': number_info['full_number'],
            'activated_at': datetime.now().isoformat(),
            'last_check': None
        }
        
        return ACTIVE_NUMBERS[country_key], None

sms_api = TempSMSAPI()

@app.route('/', methods=['GET'])
def api_usage():
    """Show API documentation and usage"""
    return jsonify({
        'api': 'Temporary SMS API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': {
                'description': 'Show this API usage documentation',
                'example': 'GET /'
            },
            'GET /numbers': {
                'description': 'Get all available temporary numbers by country',
                'example': 'GET /numbers'
            },
            'GET /numbers/{country}': {
                'description': 'Get active number and SMS messages for a specific country',
                'parameters': {
                    'country': 'Country name (france, germany, iceland, ireland, italy, spain, netherlands, poland, russia, united-kingdom)'
                },
                'example': 'GET /numbers/france'
            },
            'POST /numbers/{country}/refresh': {
                'description': 'Force refresh SMS messages for a country',
                'parameters': {
                    'country': 'Country name'
                },
                'example': 'POST /numbers/france/refresh'
            }
        },
        'supported_countries': [
            {'name': 'France', 'key': 'france'},
            {'name': 'Germany', 'key': 'germany'},
            {'name': 'Iceland', 'key': 'iceland'},
            {'name': 'Ireland', 'key': 'ireland'},
            {'name': 'Italy', 'key': 'italy'},
            {'name': 'Netherlands', 'key': 'netherlands'},
            {'name': 'Poland', 'key': 'poland'},
            {'name': 'Russia', 'key': 'russia'},
            {'name': 'Spain', 'key': 'spain'},
            {'name': 'United Kingdom', 'key': 'united-kingdom'}
        ],
        'curl_examples': {
            'Get all numbers': 'curl https://your-app.vercel.app/numbers',
            'Get France numbers': 'curl https://your-app.vercel.app/numbers/france',
            'Refresh France SMS': 'curl -X POST https://your-app.vercel.app/numbers/france/refresh'
        },
        'notes': [
            'Each country has one active number at a time',
            'SMS messages include extracted verification codes',
            'Service detection for common platforms (Apple, Google, Telegram, etc.)'
        ]
    })

@app.route('/numbers', methods=['GET'])
def show_all_numbers():
    all_numbers = []
    
    for country_key in COUNTRIES.keys():
        if country_key == 'uk':
            continue
            
        active_num, error = sms_api.get_or_create_active_number(country_key)
        
        if active_num:
            all_numbers.append({
                'country': country_key,
                'country_name': COUNTRIES[country_key]['name'],
                'number': active_num['number'],
                'status': 'available',
                'activated_at': active_num['activated_at']
            })
    
    return jsonify({
        'total_countries': len(all_numbers),
        'available_numbers': all_numbers,
        'usage': 'Use /numbers/{country-name} to view SMS for that number'
    })

@app.route('/numbers/<country>', methods=['GET'])
def show_country_number_and_sms(country):
    country_key = country.lower()
    
    if country_key == 'uk':
        country_key = 'united-kingdom'
    
    if country_key not in COUNTRIES:
        return jsonify({
            'error': f"Country '{country}' not found",
            'available_countries': [c for c in COUNTRIES.keys() if c != 'uk']
        }), 404
    
    active_num, error = sms_api.get_or_create_active_number(country_key)
    
    if error:
        return jsonify({'error': error}), 404
    
    sms_data, sms_error = sms_api.get_sms_for_number(country_key, active_num['number'])
    
    if sms_error:
        return jsonify({
            'country': country_key,
            'country_name': COUNTRIES[country_key]['name'],
            'active_number': active_num['number'],
            'error': sms_error
        }), 404
    
    messages = sms_data.get('data', [])
    
    ACTIVE_NUMBERS[country_key]['last_check'] = datetime.now().isoformat()
    
    return jsonify({
        'country': country_key,
        'country_name': COUNTRIES[country_key]['name'],
        'active_number': active_num['number'],
        'activated_at': active_num['activated_at'],
        'last_check': ACTIVE_NUMBERS[country_key]['last_check'],
        'total_sms': len(messages),
        'sms_messages': messages[:20]
    })

@app.route('/numbers/<country>/refresh', methods=['POST'])
def refresh_country_sms(country):
    country_key = country.lower()
    
    if country_key == 'uk':
        country_key = 'united-kingdom'
    
    if country_key not in COUNTRIES:
        return jsonify({'error': 'Country not found'}), 404
    
    if country_key not in ACTIVE_NUMBERS:
        return jsonify({'error': 'No active number for this country yet. Use GET first.'}), 404
    
    sms_data, error = sms_api.get_sms_for_number(country_key, ACTIVE_NUMBERS[country_key]['number'])
    
    if error:
        return jsonify({'error': error}), 404
    
    ACTIVE_NUMBERS[country_key]['last_check'] = datetime.now().isoformat()
    
    return jsonify({
        'country': country_key,
        'active_number': ACTIVE_NUMBERS[country_key]['number'],
        'last_check': ACTIVE_NUMBERS[country_key]['last_check'],
        'total_sms': len(sms_data.get('data', [])),
        'sms_messages': sms_data.get('data', [])[:10]
    })

# For Vercel
app = app

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)