USE SalesAnalytics_DB;
GO

CREATE VIEW vw_ReviewSummary AS

SELECT

    review_score,

    COUNT(*) AS total_reviews,

    COUNT(review_comment_message) AS reviews_with_comments,

    COUNT(*) - COUNT(review_comment_message) AS reviews_without_comments,

    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage_of_reviews

FROM Reviews

GROUP BY

    review_score;
GO