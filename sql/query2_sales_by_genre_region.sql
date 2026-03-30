-- Query 2: Sales by genre and region (NA, EU, JP)
-- Business question: Which game genres generate the most sales per region?

SELECT
    genre,
    ROUND(SUM(na_sales), 2)    AS ventas_na,
    ROUND(SUM(eu_sales), 2)    AS ventas_eu,
    ROUND(SUM(jp_sales), 2)    AS ventas_jp,
    ROUND(SUM(global_sales), 2) AS ventas_global
FROM videogames
GROUP BY genre
ORDER BY ventas_na DESC;
