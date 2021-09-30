skills_query = """
select "Skill" from "Skill"
"""

redskills_query = """
select "Skill" from "IgnoreSkill" isk join "Skill" s on s."Id" = isk."Id"
"""

dupskills_query = """
select ask."Skill", s."Skill" as "Parent" from "AlternateSkill" ask join "Skill" s on s."Id" = ask."Id"
"""