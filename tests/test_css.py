import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web'))
from web_app import create_app

app = create_app()
with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['user_id'] = 1; sess['username'] = 'Admin'; sess['lang'] = 'en'
    r = c.get('/dashboard')
    html = r.data.decode('utf-8')
    body_start = html.find('<body>')
    body_end = html.find('</body>')
    print('=== BODY OPENING ===')
    print(html[body_start:body_start+500])
    print('\n=== NAVBAR ===')
    nav_start = html.find('<nav')
    nav_end = html.find('</nav>')
    print(html[nav_start:nav_end+6][:800])
