/*
podtypy roli
+-----+------------+
| ID  | name       |
+-----+------------+
| 154 | agens      |
| 155 | pacjens    |
| 156 | instrument |
| 157 | miejsce    |
| 158 | czas       |
| 160 | rezultat   |
| 161 | kauzacja   |
+-----+------------+
*/
/*
SELECT 
	RT2.ID, RT2.name 
FROM 
	relationtype RT1 JOIN relationtype RT2 ON (RT1.ID = RT2.PARENT_ID)
WHERE
	RT1.ID = (SELECT id FROM relationtype WHERE name LIKE '%rola Adj%');
*/

SELECT 
	DISTINCT lemma
FROM 
	lexicalunit LU JOIN lexicalrelation LR ON (LU.ID = LR.PARENT_ID) 
WHERE 
	LU.pos = 4 AND
	LR.REL_ID IN (
		SELECT 
			RT2.ID
		FROM 
			relationtype RT1 JOIN relationtype RT2 ON (RT1.ID = RT2.PARENT_ID) 
		WHERE 
			RT1.ID = (SELECT id FROM relationtype WHERE name LIKE '%rola Adj%'));
