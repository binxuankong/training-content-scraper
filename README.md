# Training Content Scraper
Scrape data literacy related training contents from various websites, and extract out the skills (both data literacy skills and skills from ontology) mentioned in the content.

## JMLR
- Content: Research paper
- Website: https://www.jmlr.org
- Scrape all content from website and add new papers into database.

## Medium
- Content: Article
- Website: https://www.medium.com
- Tags: data-science, machine-learning, data-engineering
- Check the date of the last scraped content in the database, and scrape for the remaining dates until 7 days from today. Get contents from each tag.

## Youtube
- Content: Video
- Website: https://www.youtube.com
- Queries: Data literacy skills
- For each skill in the data literacy skills, query the skill on Youtube for videos published in this month and scrape the contents.

## KDnuggets
- Content: Article
- Website: https://www.kdnuggets.com
- Scrape for tutorials/opinions related content from the website published in this month.
