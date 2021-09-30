import pandas as pd
import datetime as dt
from sqlalchemy import create_engine
# from config.settings import settings
from secrets import settings
from jmlr_scraper import jmlr_scraper
from medium_scraper import medium_scraper
from queries import *


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
    # df_jmlr = jmlr_scraper(skills)

    # Medium
    try:
        date = dt.datetime(2021, 9, 23)
        df_med_ds = medium_scraper('data-science', date, all_skills)
        df_med_ml = medium_scraper('machine-learning', date, all_skills)
        df_med = df_med_ds.append(df_med_ml)
        df_med = df_med.drop_duplicates(subset=['id'])
        df_med = df_med.sort_values(by=['id'])
        df_med.to_sql('ContentMedium', engine, index=False, if_exists='append')
        print('Succesfully scraped contents from Medium.')
    except Exception as e:
        print('Error in scraping contents from Medium:', e)

    engine.dispose()
    return


if __name__ == "__main__":
    main()
