-- Query 3: Top publishers by decade
-- Business question: Which publishers dominated the market each decade?
-- Filtered to the top 5 publishers by historical global sales volume.

SELECT
    CASE
        WHEN year BETWEEN 1980 AND 1989 THEN '1980s'
        WHEN year BETWEEN 1990 AND 1999 THEN '1990s'
        WHEN year BETWEEN 2000 AND 2009 THEN '2000s'
        WHEN year BETWEEN 2010 AND 2019 THEN '2010s'
        ELSE 'Other'
    END AS decade,
    publisher,
    ROUND(SUM(global_sales), 2) AS total_sales
FROM videogames
WHERE publisher IN (
    'Nintendo',
    'Electronic Arts',
    'Activision',
    'Sony Computer Entertainment',
    'Ubisoft'
)
GROUP BY
    CASE
        WHEN year BETWEEN 1980 AND 1989 THEN '1980s'
        WHEN year BETWEEN 1990 AND 1999 THEN '1990s'
        WHEN year BETWEEN 2000 AND 2009 THEN '2000s'
        WHEN year BETWEEN 2010 AND 2019 THEN '2010s'
        ELSE 'Other'
    END,
    publisher
ORDER BY decade, total_sales DESC;
