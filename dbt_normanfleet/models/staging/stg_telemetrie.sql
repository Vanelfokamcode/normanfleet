with source as (
    select * from read_csv_auto('{{ env_var("NORMANFLEET_RAW") }}/fact_telemetrie.csv')
)
select
    telemetrie_id,
    vehicule_id,
    cast(date as date)                      as date_jour,
    cast(km_jour as integer)                as km_jour,
    cast(km_cumul as integer)               as km_cumul,
    cast(consommation_L100 as double)       as consommation_l100,
    statut,
    case when statut = 'actif' then 1 else 0 end as est_actif
from source
