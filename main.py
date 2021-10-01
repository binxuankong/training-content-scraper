import pandas as pd
import datetime as dt
import time
from sqlalchemy import create_engine
from config.settings import settings
# from secrets import settings
from jmlr_scraper import jmlr_scraper
from medium_scraper import medium_scraper
from youtube_scraper import youtube_scraper
from queries import *
from data_skills import DATA_SKILLS


def main():
    engine = create_engine(settings['skills_db'])

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
        df_jmlr = jmlr_scraper(all_skills, engine)
        if df_jmlr is not None:
            df_jmlr.to_sql('ContentJMLR', engine, index=False, if_exists='append')
            print('Succesfully scraped contents from JMLR.')
        else:
            print('No new content from JMLR.')
    except Exception as e:
        print('Error in scraping contents from JMLR:', e)

    # Medium
    try:
        # Scrape content with 7 days delay
        date = dt.datetime.now() - dt.timedelta(days=7)
        df_med_ds = medium_scraper('data-science', date, all_skills)
        df_med_ml = medium_scraper('machine-learning', date, all_skills)
        df_med_de = medium_scraper('data-engineering', date, all_skills)
        df_med = df_med_ds.append(df_med_ml)
        df_med = df_med.append(df_med_de)
        df_med = df_med.drop_duplicates(subset=['id'])
        df_med = df_med.sort_values(by=['id'])
        df_med.to_sql('ContentMedium', engine, index=False, if_exists='append')
        print('Succesfully scraped contents from Medium.')
    except Exception as e:
        print('Error in scraping contents from Medium:', e)
    
    # Youtube
    # Scrape only at the start of the month
    if dt.datetime.today().day == 1:
        try:
            df_yt = pd.DataFrame()
            for skill in DATA_SKILLS:
                df_temp = youtube_scraper(skill, 'this_month', all_skills)
                df_yt = df_yt.append(df_temp)
                time.sleep(5)
            df_yt = df_yt.drop_duplicates(subset='id')
            df_yt = df_yt.sort_values(by=['published_year', 'published_month', 'id'])
            # Add to temp table to avoid id conflict
            df_yt.to_sql('ContentYoutubeTemp', engine, index=False, if_exists='replace')
            engine.execute(youtube_update_query)
            engine.execute(youtube_insert_query)
            print('Succesfully scraped contents from Youtube')
        except Exception as e:
            print('Error in scraping contents from Youtube:', e)

    engine.dispose()
    return


if __name__ == "__main__":
    main()
