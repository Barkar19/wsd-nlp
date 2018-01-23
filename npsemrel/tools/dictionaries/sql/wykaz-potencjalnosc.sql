/*
potencjalnosc - 163
*/

SELECT 
	DISTINCT lemma
FROM 
	lexicalunit LU JOIN lexicalrelation LR ON (LU.ID = LR.PARENT_ID) 
WHERE 
	LU.pos = 4 AND
	LR.REL_ID IN (SELECT id FROM relationtype WHERE name LIKE '%potencjalno%');
