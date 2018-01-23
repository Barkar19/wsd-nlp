/*
dziedzina rel = 43
*/

SELECT 
	DISTINCT lemma
FROM 
	lexicalunit 
WHERE 
	pos = 4 AND 
	domain = 43 AND 
	variant = 1;

