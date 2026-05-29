with source as (
    select * from read_csv_auto('{{ env_var("NORMANFLEET_RAW") }}/fact_interventions.csv')
)
select
    intervention_id,
    vehicule_id,
    cast(date_intervention as date)     as date_intervention,
    type_intervention,
    libelle,
    technicien,
    cast(duree_heures as double)        as duree_heures,
    cast(cout_eur as integer)           as cout_eur,
    cast(km_compteur as integer)        as km_compteur,
    case when type_intervention = 'preventif' then 1 else 0 end as est_preventif
from source
