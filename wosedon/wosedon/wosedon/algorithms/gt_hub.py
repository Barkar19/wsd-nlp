#
# <one line to give the library's name and an idea of what it does.>
# Copyright (C) 2014  <copyright holder> <email>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
#

import numpy as np
from graph_tool.centrality import hits
from graph_tool.centrality import pagerank
from wosedon.algorithms.wsdalgorithminterface import WSDAlgorithmInterface
from wosedon.ranking.wsd_ranking import WSDRanking

class GTHub(WSDAlgorithmInterface):
  """!
  Personalized Page Rank algorithm based on the set of synsets which
  correspond to lemmas from the analyzed context. All synsets which belong
  to lemmas from the analyzed context have the same value in personalized
  vector "v", which is equal to 1/N, where N is the number of these synsets.
  Remaining synsets which do not belong to lemmas from the analyzed context
  have value equal to 0 in personalized vector "v".
  """

  def __init__(self, str_name = 'GTHub'):
    """!
    @param str_name - default value same as the class name "GTPersonalizedPR"
    """
    super(GTHub, self).__init__(str_name)
    self._context_node_set = None
  
  def prepare_v(self, wsd_context, graph):
    """!
    Create personalized vector "v".

    All synsets which belong to lemmas from the analyzed context have value
    equal to 1/N, where N is the number of these synsets, in personalized vector
    "v".

    Remaining synsets which do not belong to lemmas from the analyzed context
    have value equal to 0 in personalized vector "v".

    @param wsd_context - object of WSDContext class
    @param graph - object of BaseGraph class
    @return PropertyMap (see: http://graph-tool.skewed.de/static/doc/graph_tool.html?highlight=new_vertex_property#graph_tool.Graph.new_vertex_property) of personalized vector "v"
    """
    v = graph.use_graph_tool().new_vertex_property("double")
    for node in self._context_node_set:
      v[node.use_graph_tool()] = self._multiply_factor * \
        (1.0 / float(len(self._context_node_set)))
    return v
  
  def run(self, wsd_context, graph, options, resources):
    """!
    Disambiguate analyzed context.

    @param wsd_context - object of WSDContext class
    @param graph - object of BaseGraph class
    @param options - object of AlgorithmOptions class
    @param resources - object of Resources class
    @return tuple of object of WSDRanking class and number of algorithm iterations
    """
    wsd_rank = WSDRanking()
    (lemma_on_node_dict, lemma_on_only_synset_node_dict) = \
      wsd_rank.get_lemma_on_node_dict(wsd_context, graph, options.ini_nodes())
    self._set_context_node_set(lemma_on_node_dict)

    pers_v = self.prepare_v(wsd_context, graph)
    
    """
    Betweenness algorithm params:
    @param g            Graph
    @param pivots=None  If provided, the betweenness will be estimated using the vertices 
                        in this list as pivots. If the list contains all nodes (the default)
                        the algorithm will be exact, and if the vertices are randomly chosen 
                        the result will be an unbiased estimator.
    @param vprop=None  Vertex property map to store the vertex betweenness values.
    @param eprop=None  Edge property map to store the edge betweenness values.
    @param weight=None Edge property map corresponding to the weight value of each edge.
    @param norm=True   Whether or not the betweenness values should be normalized.

    """
    print("************************************************************************************")
    

    gtGraph = graph.use_graph_tool()
    print("Graph size: " + str(gtGraph.num_vertices))
    pers_v = self.prepare_v(wsd_context, graph)
    (ranking, ret_iter) = pagerank(gtGraph, 
                                   pers = pers_v, 
                                   max_iter = 2 * options.max_iter(),
                                   damping = options.damping_factor(),
                                   ret_iter = True,
                                   weight = gtGraph.ep["weight"])
    
    array = ranking.get_array()
    max_array = np.percentile(array, 90)
    bool_array = array >= max_array

    #array.astype(bool)
    ranking.a = bool_array
    print "Number vertices: " + str(gtGraph.num_vertices()) + "\n"
    propMap = gtGraph.new_vertex_property("bool", bool_array)
    gtGraph.set_vertex_filter(propMap)
    print "type of gtGraph: " + str(type(gtGraph))
    print "Number vertices: " + str(gtGraph.num_vertices()) + "\n"
    (_,__, vertex_hub) = hits(gtGraph, 
                                   #pers = pers_v,                       
                                   #max_iter = 2 * options.max_iter(),
                                   #damping = options.damping_factor(),
                                   #ret_iter = True,
                                   weight = gtGraph.ep["weight"])
    print "vertex_hub size: " + str(vertex_hub.get_array().size)

    vertex_hub = graph.ungraph_tool(vertex_hub)
    #edge_betweenness = graph.ungraph_tool(edge_betweenness)
    print "vertex_hub after ungraph: " + str(type(vertex_hub)) + " " + str(len(vertex_hub)) 



    for (lemma, pos_str) in lemma_on_only_synset_node_dict.iterkeys():
      wsd_rank.set_ranking_for_lemma(lemma, pos_str, vertex_hub)

    return (wsd_rank, 0)

  def _set_context_node_set(self, lemma_on_node_dict):
    """!
    Create a set of synsets (precisely nodes from the graph) which belong
    to lemmas from the analyzed context.

    @param lemma_on_node_dict - dictionary where key is (lemma, pos_str) and
                                value is set of synsets (nodes from the graph)
                                belong to this lemma
    """
    self._context_node_set = set()
    for nodes in lemma_on_node_dict.itervalues():
      for node in nodes:
        self._context_node_set.add(node)
