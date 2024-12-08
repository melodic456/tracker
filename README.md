# Email and Link Tracking System

This Flask application provides functionality for:
1. URL shortening with click tracking
2. Email open tracking
3. Analytics for both link clicks and email opens

## Features

- Create shortened URLs with click tracking
- Track email opens using invisible pixels
- View statistics for link clicks and email opens
- Simple web interface for link creation and stats

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

## Usage

### URL Shortening
1. Visit the homepage
2. Enter a URL to shorten
3. Use the generated short URL in your communications

### Email Open Tracking
To track email opens, add this HTML to your email:
```html
<img src="http://your-domain/track/open/[EMAIL_ID].png" alt="" style="display:none">
```
Replace [EMAIL_ID] with a unique identifier for the email.

### View Statistics
Visit the homepage to see click statistics for all shortened URLs.