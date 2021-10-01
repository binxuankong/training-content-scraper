skills_query = """
select "Skill" from "Skill"
"""

redskills_query = """
select "Skill" from "IgnoreSkill" isk join "Skill" s on s."Id" = isk."Id"
"""

dupskills_query = """
select ask."Skill", s."Skill" as "Parent" from "AlternateSkill" ask join "Skill" s on s."Id" = ask."Id"
"""

youtube_update_query = """
update "ContentYoutube" cy
set title = cyt.title, view_count = cyt.view_count, description = cyt.description, skills = cyt.skills, data_skills = cyt.data_skills
from "ContentYoutubeTemp" cyt
where cy.id = cyt.id
"""

youtube_insert_query = """
insert into "ContentYoutube"
(id, title, channel, published_year, published_month, length, view_count, url, description, skills, data_skills)
select
cyt.id, cyt.title, cyt.channel, cyt.published_year, cyt.published_month, cyt.length, cyt.view_count, cyt.url,
cyt.description, cyt.skills, cyt.data_skills
from "ContentYoutubeTemp" cyt
on conflict (id) do nothing
"""
