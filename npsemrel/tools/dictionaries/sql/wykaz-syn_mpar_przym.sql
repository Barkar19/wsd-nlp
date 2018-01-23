/*
synonimia miedzyparadygmatyczna dla relacyjnych: 169
*/
SELECT DISTINCT
	lemma
FROM 
	lexicalunit LU JOIN lexicalrelation LR ON (LU.ID = LR.PARENT_ID) 
WHERE 
	LU.pos = 4 AND
	LU.variant = 1 AND
	LR.REL_ID IN (SELECT id FROM relationtype WHERE name LIKE '%dzyparadygmatyczna dla rela%');
