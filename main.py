import pandas as pd
import datetime as dt
import time
import random
from sqlalchemy import create_engine
# from config.settings import settings
from secrets import settings
from jmlr_scraper import jmlr_scraper
from medium_scraper import medium_scraper
from youtube_scraper import youtube_scraper
from kdnuggets_scraper import kdnuggets_scraper
from queries import *
from data_skills import DATA_SKILLS


def main():
    engine = create_engine(settings['skills_db'])
    today = dt.datetime.today()

    # Get skills
    df_skills = pd.read_sql_query(skills_query, engine)
    skills = df_skills['Skill'].unique().tolist()
    df_redskills = pd.read_sql_query(redskills_query, engine)
    red_skills = df_redskills['Skill'].unique().tolist()
    df_dupskills = pd.read_sql_query(dupskills_query, engine)
    dup_skills = df_dupskills.set_index('Skill').to_dict()['Parent']
    skills.extend(list(dup_skills.keys()))
    all_skills = (skills, red_skills, dup_skills)

    # JMLR
    try:
        print('Scraping contents from JMLR...')
        df_jmlr = jmlr_scraper(all_skills, engine)
        if df_jmlr is not None:
            df_jmlr.to_sql('ContentJMLR', engine, index=False, if_exists='append')
            print('Succesfully scraped contents from JMLR!')
        else:
            print('No new content from JMLR.')
    except Exception as e:
        print('Error in scraping contents from JMLR:', e)

    # Medium
    try:
        print('Scraping contents from Medium...')
        # Get last scraped content date
        df_d = pd.read_sql_query(medium_date_query, engine)
        start_date = df_d['published_date'].item()
        # Get content with 7 days delay
        end_date = today - dt.timedelta(days=7)
        tags = ['data-science', 'machine-learning', 'data-engineering']
        df_med = pd.DataFrame()
        current_date = start_date
        for _ in range((end_date - start_date).days):
            current_date = current_date + dt.timedelta(days=1)
            print('Scraping Medium content from {}.'.format(current_date.strftime('%Y-%m-%d')))
            for tag in tags:
                df_temp = medium_scraper(tag, current_date, all_skills)
                df_med = df_med.append(df_temp)
                current_date = current_date + dt.timedelta(days=1)
                time.sleep(random.randint(1,3))
        df_med = df_med.drop_duplicates(subset=['id'])
        df_med = df_med.sort_values(by=['published_date', 'id'])
        df_med.to_sql('ContentMedium', engine, index=False, if_exists='append')
        print('Succesfully scraped contents from Medium!')
    except Exception as e:
        print('Error in scraping contents from Medium:', e)
    
    # Youtube
    try:
        print('Scraping contents from Youtube...')
        df_yt = pd.DataFrame()
        for skill in DATA_SKILLS:
            print('Scraping Youtube content for {}.'.format(skill))
            df_temp = youtube_scraper(skill, 'this_month', all_skills)
            df_yt = df_yt.append(df_temp)
            time.sleep(5)
        df_yt = df_yt.drop_duplicates(subset='id')
        df_yt = df_yt.sort_values(by=['published_year', 'published_month', 'id'])
        # Add to temp table to avoid id conflict
        df_yt.to_sql('ContentYoutubeTemp', engine, index=False, if_exists='replace')
        engine.execute(youtube_update_query)
        engine.execute(youtube_insert_query)
        print('Succesfully scraped contents from Youtube!')
    except Exception as e:
        print('Error in scraping contents from Youtube:', e)

    # KDnuggets
    try:
        print('Scraping contents from KDnuggets...')
        if today.month == 1:
            month = 12
            year = today.year - 1
        else:
            month = today.month - 1
            year = today.year
        df_kdn = kdnuggets_scraper('tutorials', month, year, all_skills)
        df_kdn = df_kdn.append(kdnuggets_scraper('opinions', month, year, all_skills))
        df_kdn = df_kdn.drop_duplicates(subset='id')
        df_kdn = df_kdn.sort_values(by=['date', 'id'])
        df_kdn.to_sql('ContentKDnuggets', engine, index=False, if_exists='append')
        print('Succesfully scraped contents from KDnuggets!')
    except Exception as e:
        print('Error in scraping contents from KDnuggets:', e)

    engine.dispose()
    return


if __name__ == "__main__":
    main()
