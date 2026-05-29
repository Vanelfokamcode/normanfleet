with source as (
    select * from read_csv_auto('{{ env_var("NORMANFLEET_RAW") }}/dim_vehicules.csv')
)
select
    vehicule_id,
    immatriculation,
    marque,
    modele,
    cast(ptac_tonnes as integer)        as ptac_tonnes,
    motorisation,
    cast(annee_mise_service as integer) as annee_mise_service,
    site_affectation,
    cast(km_total_depart as integer)    as km_total_depart,
    current_date - make_date(cast(annee_mise_service as integer), 1, 1) as age_jours
from source
