from flask import Flask, request, redirect, render_template, jsonify, send_file, session, url_for
from datetime import datetime
import os
from dotenv import load_dotenv
from database import db
from models import Link, Click, EmailOpen, EmailCampaign
from utils import generate_short_code, get_client_info, create_tracking_pixel
from auth import login_required, check_credentials

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///email_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if check_credentials(username, password):
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/api/create-link', methods=['POST'])
@login_required
def create_link():
    data = request.get_json()
    original_url = data.get('url')
    campaign_id = data.get('campaign_id')
    recipient = data.get('recipient')
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    while True:
        short_code = generate_short_code()
        if not Link.query.filter_by(short_code=short_code).first():
            break
    
    link = Link(
        original_url=original_url,
        short_code=short_code,
        campaign_id=campaign_id,
        recipient=recipient
    )
    db.session.add(link)
    db.session.commit()
    
    return jsonify({
        'short_url': f'/r/{short_code}',
        'original_url': original_url
    })

@app.route('/r/<short_code>')
def redirect_link(short_code):
    link = Link.query.filter_by(short_code=short_code).first_or_404()
    
    client_info = get_client_info(request)
    click = Click(
        link=link,
        recipient=link.recipient,
        ip_address=client_info['ip_address'],
        user_agent=client_info['user_agent'],
        device_type=client_info['device_type'],
        referrer=client_info['referrer']
    )
    db.session.add(click)
    db.session.commit()
    
    return redirect(link.original_url)

@app.route('/api/create-campaign', methods=['POST'])
@login_required
def create_campaign():
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Campaign name is required'}), 400
    
    campaign_id = generate_short_code(8)
    campaign = EmailCampaign(campaign_id=campaign_id, name=name)
    db.session.add(campaign)
    db.session.commit()
    
    return jsonify({
        'campaign_id': campaign_id,
        'name': name
    })

@app.route('/track/open/<campaign_id>/<email_id>.png')
def track_email_open(campaign_id, email_id):
    recipient = request.args.get('recipient', 'unknown')
    client_info = get_client_info(request)
    
    existing_open = EmailOpen.query.filter_by(
        email_id=email_id,
        campaign_id=campaign_id,
        recipient=recipient
    ).first()
    
    if existing_open:
        existing_open.open_count += 1
        existing_open.timestamp = datetime.utcnow()
    else:
        email_open = EmailOpen(
            email_id=email_id,
            campaign_id=campaign_id,
            recipient=recipient,
            ip_address=client_info['ip_address'],
            user_agent=client_info['user_agent'],
            device_type=client_info['device_type']
        )
        db.session.add(email_open)
    
    db.session.commit()
    return send_file(create_tracking_pixel(), mimetype='image/gif')

@app.route('/api/stats')
@login_required
def get_stats():
    links = Link.query.all()
    campaigns = EmailCampaign.query.all()
    email_opens = EmailOpen.query.all()
    
    link_details = []
    for link in links:
        clicks_data = []
        for click in link.clicks:
            clicks_data.append({
                'recipient': click.recipient,
                'timestamp': click.timestamp.isoformat(),
                'device_type': click.device_type,
                'referrer': click.referrer
            })
        
        link_details.append({
            'original_url': link.original_url,
            'short_code': link.short_code,
            'campaign_id': link.campaign_id,
            'recipient': link.recipient,
            'total_clicks': len(link.clicks),
            'clicks': clicks_data,
            'created_at': link.created_at.isoformat()
        })
    
    campaign_details = []
    for campaign in campaigns:
        opens_data = []
        campaign_opens = [o for o in email_opens if o.campaign_id == campaign.campaign_id]
        
        for email_open in campaign_opens:
            opens_data.append({
                'recipient': email_open.recipient,
                'timestamp': email_open.timestamp.isoformat(),
                'device_type': email_open.device_type,
                'open_count': email_open.open_count
            })
        
        campaign_details.append({
            'campaign_id': campaign.campaign_id,
            'name': campaign.name,
            'total_opens': len(campaign_opens),
            'unique_recipients': len(set(o.recipient for o in campaign_opens)),
            'opens': opens_data,
            'created_at': campaign.created_at.isoformat()
        })
    
    return jsonify({
        'links': link_details,
        'campaigns': campaign_details
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
