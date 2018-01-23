/*
derywacyjnosc - 59
*/

SELECT 
	DISTINCT LU1.lemma
FROM 
	lexicalunit LU1 JOIN lexicalrelation LR ON (LU1.ID = LR.PARENT_ID) 
	JOIN lexicalunit LU2 ON (LU2.ID = LR.CHILD_ID)
WHERE 
	LU1.pos = 4 AND
	LU2.pos = 2 AND
	LR.REL_ID IN (SELECT id FROM relationtype WHERE name LIKE '%derywacyjno%');
