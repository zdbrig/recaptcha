from flask import Flask, render_template, request, jsonify
import random
import base64
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
page_loads = defaultdict(list)

@app.route('/')
def home():
    client_ip = request.remote_addr
    current_time = datetime.now()
    page_loads[client_ip] = [t for t in page_loads[client_ip] if current_time - t < timedelta(minutes=5)]
    page_loads[client_ip].append(current_time)
    show_captcha = len(page_loads[client_ip]) >= 3
    return render_template('index.html', show_captcha=show_captcha)

@app.route('/subscribe')
def index():
    client_ip = request.remote_addr
    current_time = datetime.now()
    page_loads[client_ip] = [t for t in page_loads[client_ip] if current_time - t < timedelta(minutes=5)]
    page_loads[client_ip].append(current_time)
    show_captcha = len(page_loads[client_ip]) >= 3
    return render_template('index.html', show_captcha=show_captcha)

@app.route('/get-captcha', methods=['GET'])
def get_captcha():
    text = str(random.randint(1000, 9999))
    app.captcha_text = text
    img = Image.new('RGB', (100, 40), color='white')
    d = ImageDraw.Draw(img)
    for i in range(50):
        x = random.randint(0, 100)
        y = random.randint(0, 40)
        d.point((x, y), fill='black')
    d.text((30, 10), text, fill='black')
    buffered = io.BytesIO()
    img.save(buffered, format='PNG')
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return jsonify({'image': img_str})

@app.route('/verify-subscription', methods=['POST'])
def verify_subscription():
    client_ip = request.remote_addr
    show_captcha = len(page_loads[client_ip]) >= 3
    
    if show_captcha:
        captcha_response = request.form.get('captcha')
        if captcha_response != app.captcha_text:
            return jsonify({'message': 'Please enter the correct captcha'}), 400
    
    return jsonify({'message': 'Subscription successful!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
