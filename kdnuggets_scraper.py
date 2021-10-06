import random
import requests
import pandas as pd
import json
import datetime as dt
from bs4 import BeautifulSoup
from headers import headers_list
from skill_extraction import extract_skills, extract_ignore, extract_data_skills

# type_: tutorials/opinions
def kdnuggets_scraper(type_, month, year):
    base_url = 'https://www.kdnuggets.com/{}/{:>02}/{}.html' #:>02 to add leading 0 to month
    url = base_url.format(year, month, type_)
    page = requests.get(url, headers=random.choice(headers_list))
    if page.status_code != 200:
        print(page, page.reason)
        return None
    soup = BeautifulSoup(page.content, 'html.parser')
    items = soup.find('ul', class_='three_ul test').find_all('li')
    post_list = []
    for item in items:
        title = get_title(item)
        if title is None:
            continue
        description = get_description(item)
        tags = get_tags(item)
        skills, data_skills = get_skills(title, description, tags)
        post_list.append({
            'id': get_id(item),
            'title': title,
            'author': get_author(item, title),
            'date': get_date(item),
            'url': get_url(item),
            'description': description,
            'type': type_,
            'tags': tags,
            'skills': skills,
            'data_skills': data_skills,
        })
    df = pd.DataFrame.from_dict(post_list)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='id')
    return df

def get_id(item):
    try:
        return item.find('a')['id']
    except:
        return None

def get_title(item):
    try:
        return item.find('b').text
    except:
        return None

def get_author(item, title):
    try:
        this_text = item.text.replace(title, '')
        author = this_text.split('by')[1].split('-')[0]
        return author.strip()
    except:
        return None

def get_date(item):
    try:
        date = item.find('font').text
        return date.replace('-', '').strip()
    except:
        return None

def get_url(item):
    try:
        return item.find('a')['href']
    except:
        return None

def get_description(item):
    try:
        return item.find('div').text.strip()
    except:
        return None

def get_tags(item):
    try:
        tags = item.find('p', class_='tags').text
        return tags.split(': ')[-1]
    except:
        return None

def get_skills(title, description, tags):
    context = title
    if description is not None:
        context = context + ' ' + description
    if tags is not None:
        context = context + ' ' + tags
    all_skills = extract_skills(context)
    keep_skills, _ = extract_ignore(all_skills)
    keep_skills.sort()
    if len(keep_skills) > 0:
        data_skills = extract_data_skills(keep_skills)
        if len(data_skills) > 0:
            return '; '.join(keep_skills), '; '.join(data_skills)
        return '; '.join(keep_skills), None
    return None, None
