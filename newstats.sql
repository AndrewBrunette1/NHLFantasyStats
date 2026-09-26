CREATE OR REPLACE VIEW vw_fantasy_value AS
WITH season_stats AS (
    SELECT
        p.id                                                    AS player_id,
        p.name || ' ' || COALESCE(p.last_name, '')             AS full_name,
        p.position,
        p.dob,
        t.abbreviation                                          AS team_abbrev,
        s.label                                                 AS season,
        s.start_date                                             AS season_start,

        COUNT(*)                                                AS games_played,
        SUM(pgs.goals)                                          AS goals,
        SUM(pgs.assists)                                        AS assists,
        SUM(pgs.pim)                                             AS pim,
        SUM(pgs.powerplay_goals)                                AS powerplay_goals,
        SUM(pgs.shots)                                          AS shots,
        SUM(pgs.blocks)                                         AS blocks

    FROM player_game_stats pgs
    JOIN players p ON p.id = pgs.player_id
    JOIN games   g ON g.id = pgs.game_id
    JOIN seasons s ON s.id = g.season_id
    JOIN teams   t ON t.id = pgs.team_id
    WHERE g.game_type = 'regular'
    GROUP BY p.id, p.name, p.last_name, p.position, p.dob, t.abbreviation, s.label, s.start_date
),
ranked AS (
    SELECT
        *,
        -- Age as of the season start date
        DATE_PART('year', AGE(season_start, dob))               AS age,

        RANK() OVER (PARTITION BY season, position ORDER BY goals           DESC) AS rank_goals,
        RANK() OVER (PARTITION BY season, position ORDER BY assists         DESC) AS rank_assists,
        RANK() OVER (PARTITION BY season, position ORDER BY pim             DESC) AS rank_pim,
        RANK() OVER (PARTITION BY season, position ORDER BY powerplay_goals DESC) AS rank_ppg,
        RANK() OVER (PARTITION BY season, position ORDER BY shots          DESC) AS rank_shots,
        RANK() OVER (PARTITION BY season, position ORDER BY blocks         DESC) AS rank_blocks,

        COUNT(*) OVER (PARTITION BY season, position)           AS position_pool_size
    FROM season_stats
)
SELECT
    player_id,
    full_name,
    position,
    age,
    team_abbrev,
    season,
    games_played,
    goals,
    assists,
    pim,
    powerplay_goals,
    shots,
    blocks,

    (
        (position_pool_size - rank_goals   + 1) +
        (position_pool_size - rank_assists + 1) +
        (position_pool_size - rank_pim     + 1) +
        (position_pool_size - rank_ppg     + 1) +
        (position_pool_size - rank_shots   + 1) +
        (position_pool_size - rank_blocks  + 1)
    )                                                            AS fantasy_value

FROM ranked;


-- Best value, but filter to players in their prime (24-29)
SELECT full_name, position, age, team_abbrev, fantasy_value
FROM vw_fantasy_value
WHERE season = '2024-25'
  AND games_played >= 20
  AND age BETWEEN 24 AND 29
ORDER BY fantasy_value DESC
LIMIT 25;

-- Flag potential decline candidates — high historical value, older age
SELECT full_name, position, age, team_abbrev, fantasy_value
FROM vw_fantasy_value
WHERE season = '2024-25'
  AND age >= 32
ORDER BY fantasy_value DESC
LIMIT 25;
