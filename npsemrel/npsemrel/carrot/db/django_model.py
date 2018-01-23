# coding=utf-8
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
from django.db import connections
from django.db import connection
from datetime import datetime, timedelta
from django.db.models import Count

class Lexicalunit(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID') 
    lemma = models.CharField(max_length=765)
    domain = models.IntegerField()
    pos = models.IntegerField()
    tagcount = models.IntegerField(default = 0)
    source = models.IntegerField(default = 0)
    status = models.IntegerField(default = 0)
    comment = models.CharField(max_length=765, default = "")
    variant = models.IntegerField()
    project = models.IntegerField()
    owner = models.CharField(max_length=765, default = "")

    @staticmethod
    def get_pos_string(pos):
	if pos == 0: return "unknown"
        if pos == 1: return "verb"
        if pos == 2: return "subst"
        if pos == 3: return "adv"
        if pos == 4: return "adj"
        if pos == 5: return "PWN verb"
        if pos == 6: return "PWN subst"
        if pos == 7: return "PWN adv"
        if pos == 8: return "PWN adj"
        return "undefined"

    @staticmethod
    def get_pos_string_plural(pos):
	if pos == 0: return "unknown"
        if pos == 1: return "verbs"
        if pos == 2: return "substs"
        if pos == 3: return "advs"
        if pos == 4: return "adjs"
        if pos == 5: return "PWN verbs"
        if pos == 6: return "PWN substs"
        if pos == 7: return "PWN advs"
        if pos == 8: return "PWN adjs"
        return "undefined"

    @staticmethod
    def get_pwn_poses():
        return set([5,6,7,8])

    @staticmethod
    def get_plwn_poses():
        return set([1,2,3,4])

    def __unicode__(self):
        return self.lemma + " " + str(self.variant)

    class Meta:
        db_table = u'lexicalunit'
        app_label = 'wordnet_data'

    def synset(self):
        synsets = self.synsets_m.all()
        if len(synsets) > 1:
            raise ValueError("Lexical unit %d has %d synsets (more than one)" % (self.id, len(synsets)))
        if len(synsets) == 0:
            return None
        sm = synsets[0]
        return sm.syn

    def relation_subtree(self, reltype, history, maxdepth=10):
        if maxdepth == 0:
            return []
        ret = []
        for r in self.child_rels.select_related().filter(rel=reltype):
            l = r.child
            edge = (self.id, l.id)
            edge_rev = edge[::-1]
            if edge not in history and edge_rev not in history:
                history.add(edge)
                ret.append(([l], l.relation_subtree(reltype, history, maxdepth-1)))
        return ret

    def get_pos(self):
        return self.pos

class Relationtype(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID')
    objecttype = models.IntegerField()
    parent = models.ForeignKey("self", null=True, db_column='PARENT_ID', blank=True, related_name='child')
    reverse = models.ForeignKey("self", null=True, db_column='REVERSE_ID', blank=True, related_name='reverse_back')
    name = models.CharField(max_length=765)
    description = models.CharField(max_length=1500)
    posstr = models.CharField(max_length=765)
    autoreverse = models.IntegerField(null=True, blank=True)
    display = models.CharField(max_length=765)
    shortcut = models.CharField(max_length=765)
    pwn = models.CharField(max_length=10)


    def get_full_name(self):
        if self.parent is not None:
            return "%s: %s" % (self.parent.name, self.name)
        return self.name

    class Meta:
        db_table = u'relationtype'
        app_label = 'wordnet_data'

class Lexicalrelation(models.Model):
    parent = models.ForeignKey(Lexicalunit, primary_key=True, db_column='PARENT_ID', related_name='child_rels')
    child = models.ForeignKey(Lexicalunit, unique=True, db_column='CHILD_ID', related_name='parent_rels')
    rel = models.ForeignKey(Relationtype, db_column='REL_ID', related_name='lexical_instances')
    valid = models.IntegerField(null=True, blank=True)
    owner = models.CharField(max_length=765)
    class Meta:
        db_table = u'lexicalrelation'
        app_label = 'wordnet_data'

class Synset(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    split = models.IntegerField(default = 1)
    definition = models.CharField(max_length=765, default = "")
    isabstract = models.IntegerField(default = 0)
    status = models.IntegerField(default = 0)
    comment = models.CharField(max_length=765, default = "")
    owner = models.CharField(max_length=765, default = "")
    unitsstr = models.CharField(max_length=3072, default = "")
    class Meta:
        db_table = u'synset'
        app_label = 'wordnet_data'

    def lexunits(self):
        return [e.lex for e in self.lexunits_m.all().order_by('unitindex')]

    def __unicode__(self):
        return "{" + " ".join([unicode(e) for e in self.lexunits()]) + "}"

    def synset_relation_subtree(self, reltype, history, maxdepth=10):
        """Return a synset relation subtree for one relation type"""
        if maxdepth == 0:
            return []
        rels = self.child_rels.select_related().filter(rel=reltype)

        ss = [r.child for r in rels]
        ret = []
        for s in ss:
            edge = (self.id, s.id)
            edge_rev = edge[::-1]
            if edge not in history and edge_rev not in history:
                history.add(edge)
                ret.append((s, s.relation_subtree(reltype, history, maxdepth-1)))
        return ret
        
    def relation_subtree(self, reltype, history, maxdepth=10):
        """Return a synset relation subtree for one relation type"""
        if maxdepth == 0:
            return []
        rels = self.child_rels.select_related().filter(rel=reltype)

        ss = [r.child for r in rels]
        ret = []
        for s in ss:
            edge = (self.id, s.id)
            edge_rev = edge[::-1]
            if edge not in history and edge_rev not in history:
                history.add(edge)
                ret.append((s.lexunits(), s.relation_subtree(reltype, history, maxdepth-1)))
        return ret

    def get_pos(self):
        units = self.lexunits()
        if len(units) == 0:
            return -1
        return units[0].pos

class Synsetrelation(models.Model):
    parent = models.ForeignKey(Synset, primary_key=True, db_column='PARENT_ID', related_name='child_rels')
    child = models.ForeignKey(Synset, db_column='CHILD_ID', related_name='parent_rels')
    rel = models.ForeignKey(Relationtype, db_column='REL_ID', related_name='synset_instances')
    valid = models.IntegerField(null=True, blank=True)
    owner = models.CharField(max_length=765)
    class Meta:
        db_table = u'synsetrelation'
        app_label = 'wordnet_data'

class Extgraph(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=384)
    syn = models.ForeignKey(Synset, db_column='synid', related_name='extgraphs')
    score1 = models.FloatField()
    score2 = models.FloatField()
    weak = models.IntegerField()
    packageno = models.IntegerField(null=True, blank=True)
    pos = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'extgraph'

class Unitandsynset(models.Model):
    """
    jednostki leksykalne w synsecie
    """
    lex = models.ForeignKey(Lexicalunit, primary_key=True, db_column='LEX_ID', related_name='synsets_m')
    syn = models.ForeignKey(Synset, db_column='SYN_ID', related_name='lexunits_m')
    unitindex = models.IntegerField()
    class Meta:
        db_table = u'unitandsynset'
        app_label = 'wordnet_data'

class Unitdistance(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID') 
    lemma = models.CharField(max_length=765)
    child = models.CharField(max_length=765)
    distance = models.IntegerField()

    def dist(self):
        return self.distance / 1000.0

    class Meta:
        db_table = u'unitdistance'
        app_label = 'wordnet_data'

class Wordforms(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID')
    baseform = models.CharField(max_length=384)
    definition = models.CharField(max_length=192)
    finalform = models.CharField(max_length=384)
    class Meta:
        db_table = u'wordforms'
        app_label = 'wordnet_data'

def relation_tree(what, maxdepth=5):
    """Return the per-type relation subtrees for all relation types outgoing from a synset or lexical unit"""
    reltypes = what.child_rels.values_list('rel_id', flat=True).distinct()
    ret = []
    for reltype in reltypes:
        r = Relationtype.objects.get(id=reltype)
        ident = "%s - %s" % (unicode(what), r.get_full_name())
        ret.append((r, ident, what.relation_subtree(reltype, set(), maxdepth)))
    return ret

class WordHit(models.Model):
    ip = models.CharField(max_length=32)
    word = models.CharField(max_length=255)
    ts = models.DateTimeField()

    def save(self):
        if self.ts == None:
            self.ts = datetime.now()
        super(WordHit, self).save()

    @staticmethod
    def count_hits(ip, days_ago=1, seconds_ago=0):
        cutoff = datetime.now() - timedelta(days_ago, seconds_ago)
        return WordHit.objects.filter(ip=ip, ts__gt=cutoff).count()

    @staticmethod
    def add(ip, word):
        h = WordHit()
        h.ip = ip
        h.word = word
        h.save()

"""
class Message(models.Model):
    id = models.IntegerField(db_column='ID') 
    eventdate = models.CharField(max_length=765)
    message = models.CharField(max_length=765)
    class Meta:
        db_table = u'message'

class Pkglock(models.Model):
    pkgnum = models.IntegerField(primary_key=True)
    time = models.DateTimeField()
    locktype = models.IntegerField()
    pos = models.IntegerField(primary_key=True)
    owner = models.CharField(max_length=765)
    g_progress = models.FloatField(null=True, blank=True)
    l_progress = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'pkglock'

class Projects(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=48)
    class Meta:
        db_table = u'projects'

class Proposedconnectiontype(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=192)
    description = models.CharField(max_length=765)
    class Meta:
        db_table = u'proposedconnectiontype'

"""

"""
class Dblock(models.Model):
    time = models.DateTimeField()
    id = models.CharField(max_length=384, blank=True, primary_key=True)
    class Meta:
        db_table = u'dblock'

class Errorreasontype(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=192)
    description = models.CharField(max_length=765)
    class Meta:
        db_table = u'errorreasontype'



class Extgraphevaluation(models.Model):
    id = models.IntegerField(primary_key=True)
    owner = models.CharField(max_length=765)
    word = models.CharField(max_length=384)
    proposedsynid = models.IntegerField()
    assignedsynid = models.IntegerField()
    distance = models.IntegerField()
    proposedconnectiontypeid = models.IntegerField()
    relationtypeid = models.IntegerField()
    errorreasontypeid = models.IntegerField()
    comment = models.TextField()
    date = models.DateField()
    time = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'extgraphevaluation'
"""

class Stats:
    def __init__(self):
        self.cursor = connections['wordnet'].cursor()

    def lemma_stats(self):
        aa = Lexicalunit.objects.values('pos').annotate(Count('lemma', distinct=True)).annotate(Count('id')).order_by('pos')
        
        mono_all = self.monosemy()
        res = {}
        for a in aa:
            pos = a['pos']
            if pos in mono_all:
		    val = {}
		    val['count'] = a['id__count']
		    val['lemmas'] = a['lemma__count']
		    val['lemmas_mono'] = mono_all[pos]
		    val['lemmas_poly'] = val['lemmas'] - val['lemmas_mono']
		    val['polysemy'] = val['count'] * 1.0 / val['lemmas']
		    if val['lemmas_poly'] == 0:
		        val['polysemy_nomono'] = -1
		    else:
		        val['polysemy_nomono'] = (val['count'] - val['lemmas_mono']) * 1.0 / (val['lemmas_poly'])
		    res[pos] = val
        return res

    def synset_stats(self):
        query = """SELECT pos, count( DISTINCT synset.id )
            FROM synset
            INNER JOIN `unitandsynset` AS us ON synset.id = us.SYN_ID
            INNER JOIN lexicalunit ON lexicalunit.id = us.LEX_ID
            GROUP BY pos
            """
        self.cursor.execute(query)
        return dict(self.cursor.fetchall())

    def monosemy(self):
        query = """SELECT pos, COUNT(*)
            FROM (
                SELECT pos, count(variant) as cv
                FROM lexicalunit
                GROUP BY lemma
                HAVING cv=1
                ) AS z
            GROUP BY pos"""
        self.cursor.execute(query)
        return dict(self.cursor.fetchall())

    def _two_d(self, clamp):
        res = {}
        for pos, size, c in self.cursor.fetchall():
            size = min(size, clamp)
            if res.has_key(pos):
                if res[pos].has_key(size):
                    res[pos][size] += c
                else:
                    res[pos][size] = c
            else:
                res[pos] = {size:c}
        for e in res.values():
            for i in xrange(1,clamp+1):
                if not e.has_key(i):
                    e[i] = 0.0
        return res

    def _two_d_freq(self, td):
        for k in td.keys():
            td[k] = self._freqs(td[k])
        return td

    def _freqs(self, data):
        vsum = sum(data.values()) * 1.0
        for k in data.keys():
            data[k] = data[k] / vsum
        return data

    def synsetsize(self, clamp=10):
        query = """SELECT pos, lus, COUNT(id) as c
            FROM (
                SELECT synset.id, count( lexicalunit.id ) as lus, lexicalunit.pos
                FROM synset
                INNER JOIN `unitandsynset` AS us ON synset.id = us.SYN_ID
                INNER JOIN lexicalunit ON lexicalunit.id = us.LEX_ID
                GROUP BY synset.id
            ) Z
            GROUP BY pos, lus
            ORDER BY pos ASC, lus ASC"""
        self.cursor.execute(query)
        return self._two_d(clamp)

    def synset_size_freq(self, clamp=10):
        return self._two_d_freq(self.synsetsize(clamp))

    def lemmavariants(self, clamp=10):
        query = """SELECT pos, vas, COUNT(id) as c
            FROM (
                SELECT id, count( variant ) as vas, pos
                FROM lexicalunit
                GROUP BY lemma
            ) Z
            GROUP BY pos, vas
            ORDER BY pos ASC, vas ASC"""
        self.cursor.execute(query)
        return self._two_d(clamp)

    def synset_relations(self):
        query = """SELECT rt2.name, rt.name, pos, COUNT(zzz) AS C                 
                FROM (                                                                        
                    SELECT DISTINCT synset.id, pos, sr.rel_id, sr.CHILD_ID, sr.PARENT_ID AS zzz
                    FROM synsetrelation sr                                                    
                    INNER JOIN synset ON sr.parent_id = synset.id                             
                    INNER JOIN `unitandsynset` AS us ON synset.id = us.SYN_ID                 
                    INNER JOIN lexicalunit ON lexicalunit.id = us.LEX_ID                      
                    ) z                                                                           
                INNER JOIN relationtype rt ON rt.id = z.rel_id                                
                LEFT JOIN relationtype rt2 ON rt.parent_id = rt2.id
                WHERE (rt.objecttype = 1 AND rt.parent_id is NULL) OR (rt.parent_id is not NULL and rt2.objecttype = 1)
                GROUP BY rel_id, pos                                                          
                ORDER BY rt2.name,rt.name, pos"""

        self.cursor.execute(query)
        res = {}
        for parent,rel,pos,count in self.cursor.fetchall():
            if not res.has_key(parent):
                res[parent] = {'rels':{},'sorted':[]}
            if not res[parent]['rels'].has_key(rel):
                d = {}
                res[parent]['rels'][rel] = d
                res[parent]['sorted'].append({'name':rel,'pos':d})
 
            res[parent]['rels'][rel][pos] = count
        return res

    def lexical_relations(self):
        query = """SELECT rt2.name, rt.name,lu1.pos,COUNT(*) AS c
            FROM lexicalrelation lr
            INNER JOIN lexicalunit lu1 ON lr.parent_id = lu1.id
            INNER JOIN relationtype rt ON lr.rel_id = rt.id
            LEFT JOIN relationtype rt2 ON rt.parent_id = rt2.id
            WHERE (rt.objecttype = 0 AND rt.parent_id is NULL) OR (rt.parent_id is not NULL and rt2.objecttype = 0)
            GROUP BY rel_id, lu1.pos
            ORDER BY rt2.name, rt.name,pos"""
        self.cursor.execute(query)
        res = {}
        for parent,rel,pos,count in self.cursor.fetchall():
            if not res.has_key(parent):
                res[parent] = {'rels':{},'sorted':[]}
            if not res[parent]['rels'].has_key(rel):
                d = {} 
                res[parent]['rels'][rel] = d
                res[parent]['sorted'].append({'name':rel,'pos':d})

            res[parent]['rels'][rel][pos] = count
        return res

    def lemma_variants_freq(self, clamp=10):
        return self._two_d_freq(self.lemmavariants(clamp))












        
