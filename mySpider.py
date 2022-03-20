import os
import re
import sys
from bs4 import BeautifulSoup
import json
import time
import random
import requests
from hashlib import md5
from pyquery import PyQuery as pq
user_name = 'shirley.zxq'
url_base = 'https://www.instagram.com/'
uri = 'https://www.instagram.com/graphql/query/?query_hash=a5164aed103f24b03e7b7747a2d94e3c&variables=%7B%22id%22%3A%22{user_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D'
BASE_URL = 'https://www.instagram.com/accounts/login/'
LOGIN_URL = BASE_URL + 'ajax/'
headers_list = [
        "Mozilla/5.0 (Windows NT 5.1; rv:41.0) Gecko/20100101"\
        " Firefox/41.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2)"\
        " AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2"\
        " Safari/601.3.9",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0)"\
        " Gecko/20100101 Firefox/15.0.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"\
        " (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"\
        " Edge/12.246"
        ]

USERNAME = 'ooldprince'
PASSWD = 'caonima'
USER_AGENT = headers_list[random.randrange(0, 4)]

# first visit to get cookie
session = requests.Session()
session.headers = {'user-agent': USER_AGENT}
session.headers.update({'Referer': BASE_URL})
req = session.get(BASE_URL)
soup = BeautifulSoup(req.content, 'html.parser')
body = soup.find('body')
pattern = re.compile('window._sharedData')
script = body.find("script", text=pattern)
script = script.get_text().replace('window._sharedData = ', '')[:-1]
data = json.loads(script)
#print(data['config']['csrf_token'])

# login!
login_data = {'username': 'ooldprince', 'password': 'caonima', 'queryParams': {}}
session.headers.update({'X-CSRFToken': data['config']['csrf_token']})
login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
#print(login.text)
#print(login.cookies['csrftoken'])
cookies = login.cookies
session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})

#get urls
urls = []
url = url_base + user_name + '/'
response = session.get(url)
html = response.text
user_id = re.findall('"profilePage_([0-9]+)"', html, re.S)[0]
#print(user_id)
doc = pq(html)
items = doc('script[type="text/javascript"]').items()
cnt = 0
for item in items:
    if item.text().strip().startswith('window._sharedData'):
        js_data = json.loads(item.text()[21:-1], encoding='utf-8')
        edges = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
        page_info = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]['page_info']
        cursor = page_info['end_cursor']
        flag = page_info['has_next_page']
        for edge in edges:
            if edge['node']['display_url']:
                display_url = edge['node']['display_url']
                print(display_url)
                urls.append(display_url)
while flag and cnt < 7:
    url = uri.format(user_id=user_id, cursor=cursor)
    print(url)
    response = session.get(url)
    print(response)
    js_data = response.json()
    #print(js_data)
    infos = js_data['data']['user']['edge_owner_to_timeline_media']['edges']
    cursor = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
    flag = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
    for info in infos:
        if info['node']['is_video']:
            video_url = info['node']['video_url']
            if video_url:
                print(video_url)
                urls.append(video_url)
        else:
            if info['node']['display_url']:
                display_url = info['node']['display_url']
                print(display_url)
                urls.append(display_url)
    print(cursor, flag)
    cnt += 1
    time.sleep(4 + float(random.randint(1, 800))/200)
# start download!
dirpath = r'/Users/lwz/Desktop/Instagram/{0}'.format(user_name)
if not os.path.exists(dirpath):
    os.mkdir(dirpath)
for i in range(len(urls)):
    print('\ndownloading{0}： '.format(i) + urls[i], ' remaining{0}'.format(len(urls)-i-1))
    try:
        response = session.get(urls[i])
        content = response.content
        file_path = r'/Users/lwz/Desktop/Instagram/{0}/{1}.{2}'.format(user_name, md5(content).hexdigest(), urls[i][-43:-40])
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:
                print('{0}ok： '.format(i) + urls[i])
                f.write(content)
                f.close()
        else:
            print('{0} has been downloaded'.format(i))
    except Exception as e:
        print(e)
        print('download error')
