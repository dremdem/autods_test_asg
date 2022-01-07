select a.name, m.year, count(m.id)
from actor a
left join actor_movie am on a.id = am.actor_id
left join movie m on m.id = am.movie_id
group by a.name, m.year
