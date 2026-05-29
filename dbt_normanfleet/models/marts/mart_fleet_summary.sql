with tel as (
    select * from {{ ref('stg_telemetrie') }}
),
veh as (
    select * from {{ ref('stg_vehicules') }}
),
agg as (
    select
        t.vehicule_id,
        count(*)                                    as nb_jours_roulage,
        sum(t.km_jour)                              as km_total_periode,
        avg(t.km_jour)                              as km_jour_moyen,
        sum(t.est_actif)                            as jours_actifs,
        count(*) - sum(t.est_actif)                 as jours_immobilises,
        round(sum(t.est_actif) * 100.0 / count(*), 1) as taux_disponibilite_pct,
        avg(case when t.consommation_l100 > 0 then t.consommation_l100 end) as conso_moy_l100
    from tel t
    group by t.vehicule_id
)
select
    v.vehicule_id,
    v.immatriculation,
    v.marque,
    v.modele,
    v.motorisation,
    v.annee_mise_service,
    v.site_affectation,
    v.km_total_depart,
    a.km_total_periode,
    v.km_total_depart + a.km_total_periode  as km_compteur_actuel,
    a.nb_jours_roulage,
    a.jours_actifs,
    a.jours_immobilises,
    a.taux_disponibilite_pct,
    round(a.conso_moy_l100, 2)              as conso_moy_l100,
    round(a.km_jour_moyen, 1)               as km_jour_moyen
from veh v
left join agg a on v.vehicule_id = a.vehicule_id
