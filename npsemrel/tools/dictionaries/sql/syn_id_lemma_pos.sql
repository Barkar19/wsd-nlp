SELECT SYN_ID, ';', lemma, ';', pos , ';', variant, ';', domain FROM lexicalunit LU JOIN unitandsynset US ON (US.LEX_ID = LU.ID);
