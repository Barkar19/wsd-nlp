-- mysql -u wordnet -D wordnet_work --default-character-set=utf8  -p < rzecz-czas-mpar.sql > rzecz-czas-mpar.out
select LU1.lemma, LU1.variant, LU1.domain, LU2.lemma, LU2.variant, LU2.domain from lexicalunit LU1 JOIN lexicalrelation LR ON (LU1.ID = LR.PARENT_ID) JOIN lexicalunit LU2 on (LR.CHILD_ID = LU2.ID) WHERE REL_ID = 62;
