select s.simulation_day as Day,
    round(w.water_change_fraction * 100, 1) || '%' as WaterChange,
    s.tan_mass_mg as Tan,
    s.nitrite_mass_mg as Nitrite,
    s.nitrate_mass_mg as Nitrate
from daily_snapshot as s
join water_change_plan as w
on s.run_id = w.run_id and s.simulation_day = w.simulation_day
order by s.simulation_day;