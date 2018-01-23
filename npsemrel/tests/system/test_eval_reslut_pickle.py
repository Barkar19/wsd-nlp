import sys
import corpus2
from npsemrel.evaluate import evaluate as ev

if len(sys.argv) < 2:
	print ''
	print 'USAGE: python', sys.argv[0], '<filename>'
	print ''
	exit(1)

filename = sys.argv[1]
tagset = corpus2.get_named_tagset('nkjp')
odir   = ev.OutputDirs(None, None)
sres   = odir.load_single_result(filename, tagset)
srel   = sres.syntax_relation
npadjp = srel.np_adjp_phrase()
npadjp.dump_phrase(tagset, full_dump = 2)


print 'Zapisany wymik dotyczy:'
print '\t -> relacja skladniowa (1):', srel.tokens_positions(), ' -> ', ' '.join(npadjp.get_orth_at_pos(p, tagset) for p in srel.tokens_positions())
print '\t -> relacja skladniowa (2):', \
		[npadjp.phrase_bound[p] for p in srel.tokens_positions()], \
		' -> ', ' '.join(tok.orth_utf8() for tok in srel.annotated_sentence().tokens())
print '\t -> recznie dodana        :', sres.manual_semantic_relation
print '\t -> automatycznie wykryta :', sres.auto_semantic_relation
print '\t -> poprawna skladniowa   :', sres.correct_pair_triple
print '\t -> niepopr. semantyczna  :', sres.incorrect_auto_relation
