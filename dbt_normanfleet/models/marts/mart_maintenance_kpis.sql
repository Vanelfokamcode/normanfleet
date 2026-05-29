with inter as (
    select * from {{ ref('stg_interventions') }}
),
veh as (
    select vehicule_id, immatriculation, marque, site_affectation from {{ ref('stg_vehicules') }}
),
agg as (
    select
        vehicule_id,
        count(*)                                            as nb_interventions_total,
        sum(est_preventif)                                  as nb_preventif,
        count(*) - sum(est_preventif)                       as nb_curatif,
        round(sum(est_preventif) * 100.0 / count(*), 1)    as ratio_preventif_pct,
        sum(cout_eur)                                       as cout_total_eur,
        round(avg(cout_eur), 0)                             as cout_moyen_eur,
        max(km_compteur)                                    as km_derniere_intervention,
        max(date_intervention)                              as date_derniere_intervention,
        sum(duree_heures)                                   as duree_totale_heures
    from inter
    group by vehicule_id
),
fleet as (
    select * from {{ ref('mart_fleet_summary') }}
)
select
    v.vehicule_id,
    v.immatriculation,
    v.marque,
    v.site_affectation,
    a.nb_interventions_total,
    a.nb_preventif,
    a.nb_curatif,
    a.ratio_preventif_pct,
    a.cout_total_eur,
    a.cout_moyen_eur,
    a.duree_totale_heures,
    a.km_derniere_intervention,
    a.date_derniere_intervention,
    f.km_compteur_actuel,
    f.km_compteur_actuel - a.km_derniere_intervention   as km_since_last_maintenance,
    case
        when f.km_compteur_actuel - a.km_derniere_intervention > 15000 then 'ALERTE'
        when f.km_compteur_actuel - a.km_derniere_intervention > 12000 then 'ATTENTION'
        else 'OK'
    end as statut_maintenance
from veh v
left join agg a on v.vehicule_id = a.vehicule_id
left join fleet f on v.vehicule_id = f.vehicule_id
