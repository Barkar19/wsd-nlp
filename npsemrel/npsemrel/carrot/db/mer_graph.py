# coding=utf8
import networkx as nx

def rel_to_str(rel):
    if rel.parent_id is None:
        return rel.name
    else:
        return "%s:%s" % (rel.parent.name, rel.name)


def create_graph(wn_db):
    graph = nx.DiGraph()

    syns = wn_db.Synset.objects.all()
    for s in syns:
        units_db = s.lexunits()
        units = [u.lemma for u in units_db]
        if len(units) > 0:
            graph.add_node(s.id, lemmas =  units, pos = units_db[0].pos, domain = units_db[0].domain)

    r_types = \
        wn_db.Relationtype.objects.filter(name = "sumo_instance") | \
        wn_db.Relationtype.objects.filter(name = "synonimia") | \
        wn_db.Relationtype.objects.filter(name = "hiperonimia") | \
        wn_db.Relationtype.objects.filter(name = "hiponimia") | \
        wn_db.Relationtype.objects.filter(name = "meronimia") | \
        wn_db.Relationtype.objects.filter(name = "holonimia") | \
        wn_db.Relationtype.objects.filter(name = "typ") | \
        wn_db.Relationtype.objects.filter(name = "egzemplarz") | \
        wn_db.Relationtype.objects.filter(name = "mieszkaniec") | \
        wn_db.Relationtype.objects.filter(name = "uprzedniość".decode("utf8")) | \
        wn_db.Relationtype.objects.filter(name = "tstanowość".decode("utf8")) | \
        wn_db.Relationtype.objects.filter(name = "procesywność".decode("utf8")) | \
        wn_db.Relationtype.objects.filter(name = "kauzacja") | \
        wn_db.Relationtype.objects.filter(name = "bliskoznaczność".decode('utf8')) | \
				wn_db.Relationtype.objects.filter(name = "żeńskość".decode("utf8")) | \
        wn_db.Relationtype.objects.filter(name = "nacechowanie".decode("utf8"))
    rels = wn_db.Synsetrelation.objects.filter(rel__in = r_types)

    for r in rels:
        if r.parent_id not in graph or r.child_id not in graph:
            try:
                print "fail %s:" % r.rel.name, r.parent, r.child, r.parent_id, r.child_id
            except Exception, e:
                pass
        else:
            rel_str = rel_to_str(r.rel)
            graph.add_edge(r.parent_id, r.child_id, rel = rel_str)

    return graph
