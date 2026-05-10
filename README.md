<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00BFFF,100:0047FF&height=220&section=header&text=VEEPN%20SMS%20API&fontSize=58&fontColor=ffffff&fontAlignY=38&desc=Free%20Temporary%20SMS%20Verification%20Service&descAlignY=60&descSize=18&animation=fadeIn" />

<br>

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=24&pause=1000&color=00BFFF&center=true&vCenter=true&width=900&lines=VEEPN+SMS+API+%F0%9F%93%B1;Get+Temporary+Phone+Numbers+Instantly+%E2%9C%85;Flask+%7C+Requests+%7C+REST+API+Powered+%F0%9F%94%A5;Free+SMS+Verification+for+Any+Service+%E2%9A%A1;Vercel+Ready+%7C+Multiple+Countries+%F0%9F%8C%8D" alt="Typing SVG" />

<br><br>

![Python](https://img.shields.io/badge/Python-3.x-0099ff?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-0066ff?style=for-the-badge&logo=flask&logoColor=white)
![REST API](https://img.shields.io/badge/REST-API-00BFFF?style=for-the-badge)
![Vercel](https://img.shields.io/badge/Vercel-Ready-000000?style=for-the-badge&logo=vercel&logoColor=white)
![SMS](https://img.shields.io/badge/Temporary-SMS-0047FF?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-00ccff?style=for-the-badge)

<br>

> **🌍 Free Temporary SMS Verification API - Get disposable phone numbers from 10+ countries instantly!**

</div>

---

<div align="center">

# 🌟 About VEEPN SMS API

</div>

**VEEPN SMS API** is a free, lightweight REST API that provides temporary phone numbers for SMS verification from multiple countries.

**Supported Countries:**
- 🇫🇷 France
- 🇩🇪 Germany  
- 🇮🇸 Iceland
- 🇮🇪 Ireland
- 🇮🇹 Italy
- 🇳🇱 Netherlands
- 🇵🇱 Poland
- 🇷🇺 Russia
- 🇪🇸 Spain
- 🇬🇧 United Kingdom

**Perfect for:**
- 📱 Account Verification
- 🔐 Privacy Protection
- 🧪 Testing SMS Services
- 🚫 Avoiding Spam
- 🌐 International Signups

---

<div align="center">

# ✨ Features

</div>

```diff
+ 🌍 10+ Countries Supported
+ 📱 Free Temporary Phone Numbers
+ 💬 Real-time SMS Retrieval
+ 🔍 Automatic Verification Code Extraction
+ 🎯 Service Detection (Apple, Google, Telegram, etc.)
+ ⚡ Lightweight & Fast
+ ☁️ Vercel Ready (Serverless)
+ 📱 Termux Compatible
+ 🔌 Simple REST API
+ 💰 100% Free
+ 🚫 No Registration Required
+ 🔄 Auto-refresh SMS
```

---

<div align="center">

🚀 API Usage Guide

</div>

Base URL: https://your-vercel-app.vercel.app (replace with your actual Vercel URL after deployment)

1. Get API Information & Available Endpoints

```bash
GET /
```

Example:

```bash
curl https://your-vercel-app.vercel.app/
```

Response:

```json
{
  "api": "Temporary SMS API",
  "version": "1.0.0",
  "endpoints": {
    "GET /": "Show this API usage documentation",
    "GET /numbers": "Get all available temporary numbers by country",
    "GET /numbers/{country}": "Get active number and SMS messages for a specific country",
    "POST /numbers/{country}/refresh": "Force refresh SMS messages for a country"
  },
  "supported_countries": [
    "france", "germany", "iceland", "ireland", "italy",
    "netherlands", "poland", "russia", "spain", "united-kingdom"
  ]
}
```

---

2. Get All Active Numbers (One Per Country)

```bash
GET /numbers
```

Example:

```bash
curl https://your-vercel-app.vercel.app/numbers
```

Response:

```json
{
  "total_countries": 10,
  "available_numbers": [
    {
      "country": "france",
      "country_name": "France",
      "number": "+336XXXXXXXX",
      "status": "available",
      "activated_at": "2026-05-11T10:30:00"
    }
  ],
  "usage": "Use /numbers/{country-name} to view SMS for that number"
}
```

---

3. Get Number + SMS for a Specific Country

```bash
GET /numbers/{country}
```

Supported country names:
france, germany, iceland, ireland, italy, netherlands, poland, russia, spain, united-kingdom

Example (France):

```bash
curl https://your-vercel-app.vercel.app/numbers/france
```

Response:

```json
{
  "country": "france",
  "country_name": "France",
  "active_number": "+336XXXXXXXX",
  "activated_at": "2026-05-11T10:30:00",
  "last_check": "2026-05-11T10:35:00",
  "total_sms": 2,
  "sms_messages": [
    {
      "text": "Your Apple verification code is 654321",
      "verification_codes": ["654321"],
      "service": "Apple",
      "time": "2026-05-11T10:32:00"
    },
    {
      "text": "Telegram code 123456",
      "verification_codes": ["123456"],
      "service": "Telegram",
      "time": "2026-05-11T10:33:00"
    }
  ]
}
```

---

4. Refresh SMS for a Country

```bash
POST /numbers/{country}/refresh
```

Example (Germany):

```bash
curl -X POST https://your-vercel-app.vercel.app/numbers/germany/refresh
```

Response:

```json
{
  "country": "germany",
  "active_number": "+4915XXXXXXXX",
  "last_check": "2026-05-11T10:40:00",
  "total_sms": 5,
  "sms_messages": [...]
}
```

---

📝 Quick Example: Extract Verification Code

Using Python:

```python
import requests

# Get France number and SMS
response = requests.get('https://your-vercel-app.vercel.app/numbers/france')
data = response.json()

# Extract first verification code
for sms in data['sms_messages']:
    if sms['verification_codes']:
        print(f"Service: {sms['service']}")
        print(f"Code: {sms['verification_codes'][0]}")
        break
```

Using cURL + jq (parse JSON):

```bash
curl -s https://your-vercel-app.vercel.app/numbers/iceland | jq '.sms_messages[].verification_codes[]'
```

---

🌍 Supported Countries & Codes

Country Key Example Number
France france +336XXXXXXXX
Germany germany +4915XXXXXXXX
Iceland iceland +354XXXXXX
Ireland ireland +35389XXXXX
Italy italy +39XXXXXXXX
Netherlands netherlands +316XXXXXXXX
Poland poland +48XXXXXXXX
Russia russia +79XXXXXXXX
Spain spain +346XXXXXXXX
United Kingdom united-kingdom +447XXXXXXXX

---

⚠️ Notes

· Each country maintains 1 active number at a time
· SMS messages automatically include extracted verification codes (4-8 digits)
· Service detection works for: Apple, Google, Amazon, Telegram, TikTok, Coinbase, Claude, NVIDIA, Samsung
· Messages are limited to last 20 (GET) or 10 (POST refresh)
· Numbers are temporary and may change over time

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00BFFF,100:0047FF&height=150&section=footer" />

Made with ❤️ for the developer community

⬆ Back to Top

</div>
