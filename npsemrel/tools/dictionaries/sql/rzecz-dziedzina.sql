-- mysql -u wordnet -D wordnet_work --default-character-set=utf8  -p < rzecz-dziedzina.sql > rzecz-dziedzina.out
select lemma, variant, domain FROM lexicalunit WHERE pos = 2;
