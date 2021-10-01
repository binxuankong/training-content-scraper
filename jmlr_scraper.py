import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from headers import headers_list
from skill_extraction import extract_skills, extract_ignore, extract_data_skills

def jmlr_scraper(skills, engine):
    base_url = 'https://jmlr.org'
    url = base_url + '/papers/v22/'
    page = requests.get(url, headers=random.choice(headers_list))
    if page.status_code != 200:
        return
    soup = BeautifulSoup(page.content, 'html.parser')
    dls = soup.findAll('dl')
    # Get existing papers in database
    df_ex = pd.read_sql_query('select cj.id, cj.title from "ContentJMLR" cj', engine)
    ex_papers = df_ex['title'].unique().tolist()
    papers = []
    # Iterate through each paper
    has_new = False
    for dl in dls:
        title = dl.find('dt').get_text()
        if title in ex_papers:
            continue
        paper = {}
        dd = dl.find('dd')
        paper['title'] = title
        paper['authors'] = dd.get_text().split(';')[0].strip()
        paper['journal_num'] = dd.get_text().split(';')[-1].split('\n')[0].split('(').strip()
        for a in dd.findAll('a'):
            if a.get_text() == '(Machine Learning Open Source Software Paper)':
                continue
            href = a['href']
            if 'http' not in href:
                href = base_url + href
            paper[a.get_text()] = href
        # Get abstract of paper and extract skills
        output = get_abstract_skills(paper, skills)
        if output is not None:
            paper['abstract'] = output[0]
            if len(output[1]) > 0:
                paper['skills'] = '; '.join(output[1])
                data_skills = extract_data_skills(output[1])
                if len(data_skills) > 0:
                    paper['data_skills'] = '; '.join(data_skills)
        papers.append(paper)
        has_new = True
    # Compile into dataframe if we have new papers
    if has_new:
        df = pd.DataFrame.from_dict(papers)
        df['id'] = df.index + max(df_ex['id']) + 1
        return df
    return None

def get_abstract_skills(paper, skills):
    page = requests.get(paper['abs'], headers=random.choice(headers_list))
    if page.status_code != 200:
        return None
    soup = BeautifulSoup(page.content, 'html.parser')
    abstract = soup.find('p', class_='abstract').get_text().strip('\n')
    all_skills = extract_skills(paper['title'] + ' ' + abstract, skills[0])
    keep_skills, _ = extract_ignore(all_skills, skills[1], skills[2])
    keep_skills.sort()
    return abstract, keep_skills
