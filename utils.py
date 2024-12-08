import random
import string
from io import BytesIO
import re

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_client_info(request):
    user_agent = request.user_agent.string
    device_type = detect_device_type(user_agent)
    
    return {
        'ip_address': request.remote_addr,
        'user_agent': user_agent,
        'device_type': device_type,
        'referrer': request.referrer
    }

def detect_device_type(user_agent):
    user_agent = user_agent.lower()
    if any(device in user_agent for device in ['iphone', 'ipad', 'android', 'mobile']):
        return 'mobile'
    elif 'tablet' in user_agent:
        return 'tablet'
    else:
        return 'desktop'

def create_tracking_pixel():
    pixel = BytesIO()
    pixel.write(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')
    pixel.seek(0)
    return pixel