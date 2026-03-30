-- Query 1: Top 10 best-selling video games of all time
-- Business question: What are the top 10 video games with the highest global sales?

SELECT
    name,
    platform,
    year,
    genre,
    publisher,
    global_sales
FROM videogames
ORDER BY global_sales DESC
LIMIT 10;
