with source as (
    select * from read_csv_auto('{{ env_var("NORMANFLEET_RAW") }}/dim_chauffeurs.csv')
)
select
    chauffeur_id,
    nom,
    prenom,
    nom || ' ' || prenom           as nom_complet,
    cast(permis_ce as boolean)     as permis_ce,
    cast(anciennete_ans as integer) as anciennete_ans,
    site
from source
