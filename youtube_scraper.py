import random
import requests
import pandas as pd
import json
import datetime as dt
from bs4 import BeautifulSoup
from headers import headers_list
from skill_extraction import extract_skills, extract_ignore, extract_data_skills

def get_youtube_videos(skill, filter_time, skills):
    base_url = 'https://www.youtube.com'
    # Dictionary for filtering search query
    sp_dict = {'this_year': 'EgQIBRAB', 'this_month': 'EgQIBBAB', 'this_week': 'EgQIAxAB', 'today': 'EgQIAhAB'}
    if filter_time not in sp_dict.keys():
        return None
    url = base_url + '/results'
    query = 'learn ' + skill
    params = {'search_query': query.replace(' ', '+')}
    # Default is no filter
    if filter_time is not None:
        params['sp'] = sp_dict[filter_time]
    page = requests.get(url, params=params, headers=random.choice(headers_list))
    if page.status_code != 200:
        print(page, page.reason)
        return None
    soup = BeautifulSoup(page.content, 'html.parser')
    json_text = str(soup.find_all('script')).split('var ytInitialData = ')[-1].split(';</script>')[0]
    res = json.loads(json_text)
    res = res['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
    video_list = []
    # Iterate through each video
    for contents in res:
        # Get only those with video
        if 'itemSectionRenderer' not in contents:
            continue
        contents = contents['itemSectionRenderer']['contents']
        for content in contents:
            # Ignore ads
            if 'videoRenderer' not in content:
                continue
            content = content['videoRenderer']
            title = get_text(content, 'title')
            if title is None:
                continue
            description = get_description(content)
            this_skills, data_skills = get_skills(title, description, skills)
            published_year, published_month = get_published_date(content)
            video_list.append({
                'id': content['videoId'],
                'title': title,
                'channel_id': get_channel_id(content),
                'channel': get_text(content, 'ownerText'),
                'published_year': published_year,
                'published_month': published_month,
                'length': get_length(content),
                'view_count': get_view_count(content),
                'url': get_url(content, base_url),
                'description': description,
                'skills': this_skills,
                'data_skills': data_skills
            })
    df = pd.DataFrame.from_dict(video_list)
    # df['length'] = pd.to_timedelta(df['length'])
    return df
    
def get_channel_id(content):
    try:
        return content['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId']
    except:
        return None

def get_text(content, info):
    try:
        return ' '.join(t['text'] for t in content[info]['runs'])
    except:
        return None

def get_length(content):
    try:
        length = content['lengthText']['simpleText']
        length = length.split(':')
        if len(length) == 1:
            length.insert(0, '00')
        if len(length) == 2:
            length.insert(0, '00')
        return ':'.join(length)
    except:
        return None

def get_published_date(content):
    try:
        published_time = content['publishedTimeText']['simpleText']
        val = [int(s) for s in published_time.split() if s.isdigit()][0]
        current = dt.datetime.now()
        if 'year' in published_time:
            published = current - dt.timedelta(days=365.25*val)
        elif 'month' in published_time:
            published = current - dt.timedelta(days=30.436875*val)
        elif 'week' in published_time:
            published = current - dt.timedelta(weeks=val)
        elif 'day' in published_time:
            published = current - dt.timedelta(days=val)
        elif 'hour' in published_time:
            published = current - dt.timedelta(hours=val)
        elif 'minute' in published_time:
            published = current - dt.timedelta(minutes=val)
        elif 'second' in published_time:
            published = current - dt.timedelta(seconds=val)
        return published.year, published.month
    except:
        return None, None

def get_view_count(content):
    try:
        view_count = content['viewCountText']['simpleText']
        view_count = view_count.split(' views')[0].replace(',', '')
        return int(view_count)
    except:
        return None

def get_url(content, base_url):
    try:
        url = content['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
        return base_url + url
    except:
        return None

def get_description(content):
    try:
        description = ' '.join([t['text'] for t in content['detailedMetadataSnippets'][0]['snippetText']['runs']])
        return description
    except:
        return None

def get_skills(title, description, skills):
    context = title
    if description is not None:
        context = context + ' ' + description
    all_skills = extract_skills(context, skills[0])
    # Ignore the Video skill as it is not relevant for Youtube
    if 'Video' in all_skills:
        all_skills.remove('Video')
    keep_skills, _ = extract_ignore(all_skills, skills[1], skills[2])
    keep_skills.sort()
    if len(keep_skills) > 0:
        data_skills = extract_data_skills(keep_skills)
        if len(data_skills) > 0:
            return '; '.join(keep_skills), '; '.join(data_skills)
        return '; '.join(keep_skills), None
    return None, None
