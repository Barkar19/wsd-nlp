select 
	LU2.lemma, LU1.lemma 
from 
	lexicalrelation LR 
		JOIN lexicalunit LU1 ON (LR.PARENT_ID = LU1.ID) 
		JOIN lexicalunit LU2 ON (LR.CHILD_ID = LU2.ID) 
WHERE 
	LU2.variant = 1 AND
	LR.REL_ID IN (
		SELECT ID FROM relationtype WHERE relationtype.PARENT_ID IN (32, 33)
	) 
	AND LU1.pos = 1 AND LU2.pos = 2
	UNION
select 
	LU1.lemma, LU2.lemma 
from 
	lexicalrelation LR 
		JOIN lexicalunit LU1 ON (LR.PARENT_ID = LU1.ID) 
		JOIN lexicalunit LU2 ON (LR.CHILD_ID = LU2.ID) 
WHERE 
	LU1.variant = 1 AND
	LR.REL_ID IN (
		SELECT ID FROM relationtype WHERE relationtype.PARENT_ID IN (32, 33)
	) 
	AND LU1.pos = 2 and LU2.pos = 1
;
