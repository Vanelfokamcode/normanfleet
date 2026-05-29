with tel as (
    select * from {{ ref('stg_telemetrie') }}
    where consommation_l100 > 0
),
monthly as (
    select
        vehicule_id,
        date_trunc('month', date_jour)          as mois,
        round(avg(consommation_l100), 2)        as conso_moy_mois,
        sum(km_jour)                            as km_mois,
        count(*)                                as nb_jours
    from tel
    group by vehicule_id, date_trunc('month', date_jour)
),
global_stats as (
    select
        avg(consommation_l100)   as mu,
        stddev(consommation_l100) as sigma
    from tel
),
veh_avg as (
    select
        vehicule_id,
        round(avg(consommation_l100), 2) as conso_moy_globale,
        round(stddev(consommation_l100), 2) as conso_stddev
    from tel
    group by vehicule_id
),
flagged as (
    select
        va.vehicule_id,
        va.conso_moy_globale,
        va.conso_stddev,
        g.mu,
        g.sigma,
        case when va.conso_moy_globale > g.mu + 2 * g.sigma then true else false end as est_outlier
    from veh_avg va cross join global_stats g
)
select
    f.vehicule_id,
    f.conso_moy_globale,
    f.conso_stddev,
    round(f.mu, 2)      as conso_flotte_moy,
    round(f.sigma, 2)   as conso_flotte_sigma,
    f.est_outlier,
    case when f.est_outlier then round(f.conso_moy_globale - f.mu, 2) end as ecart_vs_moyenne
from flagged f
order by f.conso_moy_globale desc
