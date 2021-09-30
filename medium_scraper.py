import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from headers import headers_list
from skill_extraction import extract_skills, extract_ignore, extract_data_skills

def medium_scraper(tag, date, skills):
    base_url = 'https://medium.com/tag/{}/archive/'
    url = base_url.format(tag) + date.strftime('%Y/%m/%d')
    page = requests.get(url, headers=random.choice(headers_list))
    soup = BeautifulSoup(page.content, 'html.parser')
    # Pulls each card from the feed. Each card is a story or comment
    cards = soup.find_all('div', class_='streamItem streamItem--postPreview js-streamItem')
    card_list = []
    for card in cards:
        title = get_title(card)
        subtitle = get_subtitle(card)
        claps = get_claps(card)
        if title is None or is_comment(card) or claps is None:
            continue
        if claps < 100:
            continue
        this_skills, data_skills = get_skills(title, subtitle, skills)
        card_list.append({
            'id': get_id(card),
            'title': title,
            'subtitle': subtitle,
            'author': get_author(card),
            'publication': get_publication(card),
            'published_date': date,
            'read_time_mins': get_read_time(card),
            'claps': claps,
            'url': get_url(card),
            'skills': this_skills,
            'data_skills': data_skills,
        })
    df = pd.DataFrame.from_dict(card_list)
    df['published_date'] = pd.to_datetime(df['published_date'])
    return df

def get_id(card):
    id_ = card.find('div', class_='postArticle postArticle--short js-postArticle js-trackPostPresentation js-trackPostScrolls')
    if id_ is not None:
        return id_['data-post-id']
    return id_

def get_title(card):
    # Different combination of classes possible for titles
    combinations = [('h3', 'graf graf--h3 graf-after--figure graf--title'),
                    ('h3', 'graf graf--h3 graf-after--figure graf--trailing graf--title'),
                    ('h4', 'graf graf--h4 graf--leading'),
                    ('h3', 'graf graf--h3 graf--leading graf--title'),
                    ('p', 'graf graf--p graf--leading'),
                    ('h3', 'graf graf--h3 graf--startsWithDoubleQuote graf--leading graf--title'),
                    ('h3', 'graf graf--h3 graf--startsWithDoubleQuote graf-after--figure graf--trailing graf--title')]
    title = None
    for combi in combinations:
        title = card.find(combi[0], class_=combi[1])
        if title is not None:
            return title.text
    return title

def get_subtitle(card):
    # Different combination of classes possible for subtitles
    combinations = [('h4', 'graf graf--h4 graf-after--h3 graf--subtitle'),
                    ('h4', 'graf graf--h4 graf-after--h3 graf--trailing graf--subtitle'),
                    ('strong', 'markup--strong markup--p-strong'),
                    ('h4', 'graf graf--p graf-after--h3 graf--trailing'),
                    ('p', 'graf graf--p graf-after--h3 graf--trailing'),
                    ('blockquote', 'graf graf--pullquote graf-after--figure graf--trailing'),
                    ('p', 'graf graf--p graf-after--figure'),
                    ('blockquote', 'graf graf--blockquote graf-after--h3 graf--trailing'),
                    ('p', 'graf graf--p graf-after--figure graf--trailing'),
                    ('em', 'markup--em markup--p-em'),
                    ('p', 'graf graf--p graf-after--p graf--trailing')]
    subtitle = None
    for combi in combinations:
        subtitle = card.find(combi[0], class_=combi[1])
        if subtitle is not None:
            return subtitle.text
    return subtitle

def get_author(card):
    author = card.find('a', class_='ds-link ds-link--styleSubtle link link--darken link--accent u-accentColor--textNormal u-accentColor--textDarken')
    if author is not None:
        return author.text
    return author

def get_publication(card):
    pub = card.find('a', class_='ds-link ds-link--styleSubtle link--darken link--accent u-accentColor--textNormal')
    if pub is not None:
        return pub.text
    return pub

def get_read_time(card):
    time = card.find('span', class_='readingTime')
    if time is not None:
        time = time['title']
        return time.replace(' min read', '')
    return time

def get_claps(card):
    claps = card.find('button', class_='button button--chromeless u-baseColor--buttonNormal js-multirecommendCountButton u-disablePointerEvents')
    if claps is not None:
        claps = claps.text
        if 'K' in claps:
            try:
                return int(float(claps.replace('K', '')) * 1000)
            except:
                return None
        else:
            try:
                return int(claps)
            except:
                return None
    return claps

def is_comment(card):
    # Check if card is a story or comment
    comment = card.find('div', class_='u-fontSize14 u-marginTop10 u-marginBottom20 u-padding14 u-xs-padding12 u-borderRadius3 u-borderCardBackground u-borderLighterHover u-boxShadow1px4pxCardBorder')
    return comment is not None

def get_url(card):
    url = card.find('a', class_='')
    if url is not None:
        return url['href'].split('?')[0]
    return url

def get_skills(title, subtitle, skills):
    context = title
    if subtitle is not None:
        context = context + ' ' + subtitle
    all_skills = extract_skills(context, skills[0])
    keep_skills, _ = extract_ignore(all_skills, skills[1], skills[2])
    keep_skills.sort()
    if len(keep_skills) > 0:
        data_skills = extract_data_skills(keep_skills)
        if len(data_skills) > 0:
            return '; '.join(keep_skills), '; '.join(data_skills)
        return '; '.join(keep_skills), None
    return None, None
