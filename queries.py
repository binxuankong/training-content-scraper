get_inactive_users = """
select fname, user_id from user_details where last_login_date IS NOT NULL AND last_login_date < NOW() - INTERVAL '4 days'
"""

get_inactive_users_keycloak = """
select 
distinct on 
(ee.user_id) ee.user_id, to_timestamp(ee.event_time/1000), ue.email 
from event_entity as ee 
inner join user_entity ue 
on ee.user_id = ue.id 
WHERE 
to_timestamp(ee.event_time/1000) < NOW() - INTERVAL '30 days' 
AND type='LOGIN' 
AND ue.email IS NOT NULL 
AND ee.user_id IS NOT NULL 
order by ee.user_id, ee.id ASC
"""