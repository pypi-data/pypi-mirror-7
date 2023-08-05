#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014 CNRS (Hervé BREDIN - http://herve.niderb.fr)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import unicode_literals

import networkx as nx
from networkx.readwrite.json_graph import node_link_data, node_link_graph

from time import T, TStart, TEnd
from segment import Segment
from json import PYANNOTE_JSON_TRANSCRIPTION

import itertools


class Transcription(nx.MultiDiGraph):
    """Transcription stored as annotation graph"""

    def __init__(self, graph=None, **attrs):
        super(Transcription, self).__init__(data=graph)
        self.graph.update(attrs)

    def drifting(self):
        """Get list of drifting times"""
        return [n for n in self if n.drifting]

    def anchored(self):
        """Get list of anchored times"""
        return [n for n in self if n.anchored]

    def add_edge(self, t1, t2, key=None, attr_dict=None, **attrs):
        """Add annotation to the graph between times t1 and t2

        Parameters
        ----------
        t1, t2: float, str or None
        data : dict, optional
            {annotation_type: annotation_value} dictionary

        Example
        -------
        >>> G = Transcription()
        >>> G.add_edge(T(1.), T(), speaker='John', 'speech'='Hello world!')
        """
        t1 = T(t1)
        t2 = T(t2)

        # make sure Ts are connected in correct chronological order
        if t1.anchored and t2.anchored:
            assert t1 <= t2

        super(Transcription, self).add_edge(t1, t2, key=key, attr_dict=attr_dict, **attrs)

    def relabel_drifting_nodes(self, mapping=None):
        """Relabel drifting nodes

        Parameters
        ----------
        mapping : dict, optional
            A dictionary with the old labels as keys and new labels as values.
            

        Returns
        -------
        g : Transcription
            New annotation graph
        mapping : dict
            A dictionary with the new labels as keys and old labels as values.
            Can be used to get back to the version before relabelling.
        """

        if mapping is None:
            old2new = {n: T() for n in self.drifting()}
        else:
            old2new = dict(mapping)

        new2old = {new: old for old, new in old2new.iteritems()}
        return nx.relabel_nodes(self, old2new, copy=True), new2old

    def crop(self, source, target=None):
        """Get subgraph between source and target

        Parameters
        ----------
        source : Segment, 
        target : float or str, optional

        Returns
        -------
        g : Transcription
            Sub-graph between source and target
        """
        
        if isinstance(source, Segment):
            source, target = source.start, source.end

        source = T(source)
        target = T(target)

        if source.anchored:
            before = [n for n in self.anchored() if n <= source]
            if before:
                source = sorted(before)[-1] 

        if target.anchored:
            after = [n for n in self.anchored() if n >= target]
            if after:
                target = sorted(after)[0]

        from_source = nx.algorithms.descendants(self, source)
        to_target = nx.algorithms.ancestors(self, target)
        nbunch = {source, target} | (from_source & to_target)
        return self.subgraph(nbunch)

    # =========================================================================

    def _merge(self, drifting_t, another_t):
        """Helper function to merge `drifting_t` with `another_t`

        Assumes that both `drifting_t` and `another_t` exists.
        Also assumes that `drifting_t` is an instance of `TFloating`
        (otherwise, this might lead to weird graph configuration)

        Parameters
        ----------
        drifting_t :
            Existing drifting time in graph
        another_t : 
            Existing time in graph
        """
        # drifting_t and another_t must exist in graph

        # add a (t --> another_t) edge for each (t --> drifting_t) edge
        for t, _, key, data in self.in_edges_iter(
            nbunch=[drifting_t], data=True, keys=True
        ):
            self.add_edge(t, another_t, key=key, attr_dict=data)

        # add a (another_t --> t) edge for each (drifting_t --> t) edge
        for _, t, key, data in self.edges_iter(
            nbunch=[drifting_t], data=True, keys=True
        ):
            self.add_edge(another_t, t, key=key, attr_dict=data)

        # remove drifting_t node (as it was replaced by another_t)
        self.remove_node(drifting_t)

    def anchor(self, drifting_t, anchored_t):
        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        o -- [ D ] -- o  ==>  o -- [ A ] -- o

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        Anchor `drifting_t` at `anchored_t`

        Parameters
        ----------
        drifting_t : 
            Drifting time to anchor
        anchored_t : 
            When to anchor `drifting_t`

        """

        drifting_t = T(drifting_t)
        anchored_t = T(anchored_t)

        assert (drifting_t in self) and (drifting_t.drifting)
        assert anchored_t.anchored

        if anchored_t not in self:
            self.add_node(anchored_t)

        self._merge(drifting_t, anchored_t)

    def align(self, one_t, another_t):
        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        o -- [ F ] -- o      o          o
                               ⟍     ⟋   
                        ==>     [ F ]
                               ⟋     ⟍
        o -- [ f ] -- o      o          o    

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        Align two (potentially drifting) times

        `one_t` and `another_t` cannot both be anchored at the same time
        In case `another_t` is anchored, this is similar to `anchor` method

        Parameters
        ----------
        one_t, another_t
            Two times to be aligned.
        """

        one_t = T(one_t)
        another_t = T(another_t)

        assert one_t in self
        assert another_t in self

        # first time is drifting
        if one_t.drifting:
            self._merge(one_t, another_t)

        # second time is drifting
        elif another_t.drifting:
            self._merge(another_t, one_t)

        # both times are anchored --> FAIL
        else:
            raise ValueError(
                'Cannot align two anchored times')

    # =========================================================================

    def pre_align(self, t1, t2, t):
        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        p -- [ t1 ]       p         [ t1 ]
                            ⟍     ⟋   
                     ==>     [ t ]
                            ⟋     ⟍
        p' -- [ t2 ]      p'        [ t2 ]    

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        """

        t1 = T(t1)
        t2 = T(t2)
        t = T(t)

        # make sure --[t1] incoming edges are empty
        # because they're going to be removed afterwards,
        # and we don't want to loose data
        pred1 = self.predecessors(t1)
        for p in pred1:
            for key, data in self[p][t1].iteritems():
                assert not data

        # make sure --[t2] incoming edges are empty
        # (for the same reason...)
        pred2 = self.predecessors(t2)
        for p in pred2:
            for key, data in self[p][t2].iteritems():
                assert not data

        # let's get started (remove all incoming edges)
        for p in pred1:
            for key in list(self[p][t1]):
                self.remove_edge(p, t1, key=key)
        for p in pred2:
            for key in list(self[p][t2]):
                self.remove_edge(p, t2, key=key)

        for p in set(pred1) | set(pred2):
            self.add_edge(p, t)

        self.add_edge(t, t1)
        self.add_edge(t, t2)

    def post_align(self, t1, t2, t):
        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        [ t1 ] -- s       [ t1 ]         s
                                ⟍     ⟋   
                     ==>         [ t ]
                                ⟋     ⟍
        [ t2 ] -- s'      [ t2 ]        s'    

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        t1 = T(t1)
        t2 = T(t2)
        t = T(t)

        # make sure [t1]-- outgoing edges are empty
        # because they're going to be removed afterwards,
        # and we don't want to loose data
        succ1 = self.successors(t1)
        for s in succ1:
            for key, data in self[t1][s].iteritems():
                assert not data

        # make sure --[t2] outgoing edges are empty
        # (for the same reason...)
        succ2 = self.successors(t2)
        for s in succ2:
            for key, data in self[t2][s].iteritems():
                assert not data

        # let's get started (remove all outgoing edges)
        for s in succ1:
            for key in list(self[t1][s]):
                self.remove_edge(t1, s, key=key)
        for s in succ2:
            for key in list(self[t2][s]):
                self.remove_edge(t2, s, key=key)

        for s in set(succ1) | set(succ2):
            self.add_edge(t, s)

        self.add_edge(t1, t)
        self.add_edge(t2, t)

    # =========================================================================

    def ordering_graph(self):
        """Ordering graph

        t1 --> t2 in the ordering graph indicates that t1 happens before t2.
        A missing edge simply means that it is not clear yet.

        """

        g = nx.DiGraph()

        # add times
        for t in self.nodes_iter():
            g.add_node(t)

        # add existing edges
        for t1, t2 in self.edges_iter():
            g.add_edge(t1, t2)

        # connect every pair of anchored times
        anchored = sorted(self.anchored())
        for t1, t2 in itertools.combinations(anchored, 2):
            g.add_edge(t1, t2)

        # connect every time with its sucessors
        _g = g.copy()
        for t1 in _g:
            for t2 in set([target for (_, target) in nx.bfs_edges(_g, t1)]):
                g.add_edge(t1, t2)

        return g

    def ordered_edges_iter(self, data=False, keys=False):
        """Return an iterator over the edges in temporal/topological order.

        Ordered edges are returned as tuples with optional data and keys
        in the order (t1, t2, key, data).

        Parameters
        ----------
        data : bool, optional (default=False)
            If True, return edge attribute dict with each edge.
        keys : bool, optional (default=False)
            If True, return edge keys with each edge.

        Returns
        -------
        edge_iter : iterator
            An iterator of (u,v), (u,v,d) or (u,v,key,d) tuples of edges.
        """

        # start by sorting nodes in temporal+topological order
        o = self.ordering_graph()
        nodes = nx.topological_sort(o)

        # iterate over edges using this very order
        for _ in self.edges_iter(nbunch=nodes, data=data, keys=keys):
            yield _

    # =========================================================================

    def _anchored_successors(self, n):
        """Get all first anchored successors"""

        # loop on all outgoing edges
        for t in self.successors(n):
            
            # if neighbor is anchored
            # stop looking for (necessarily later) successors
            if t.anchored:
                yield t
                continue

            # if neighbor is not anchored
            # look one level deeper
            for tt in self._anchored_successors(t):
                yield tt

    def _anchored_predecessors(self, n):
        """Get all first anchored predecessors"""

        # loop on all incoming edges
        for t in self.predecessors(n):
            
            # if predecessor is anchored
            # stop looking for (necessarily earlier) predecessors
            if t.anchored:
                yield t
                continue
            
            # if neighbor is not anchored
            # look one level deeper
            for tt in self._anchored_predecessors(t):
                yield tt

    def timerange(self, t):
        """Infer smallest possible timerange from graph structure

        Returns
        -------
        (left, right) tuple
            left == None or right == None indicates that the current state of
            the annotation graph does not allow to decide the boundary.

        """

        t = T(t)

        if t.anchored:
            return (t.T, t.T)
        successors = [n for n in self._anchored_successors(t)]
        predecessors = [n for n in self._anchored_predecessors(t)]

        earlier_successor = None
        if successors:
            earlier_successor = min(successors)

        later_predecessor = None
        if predecessors:
            later_predecessor = max(predecessors)

        return (later_predecessor.T, earlier_successor.T)

    # =========================================================================

    def for_json(self):
        return {PYANNOTE_JSON_TRANSCRIPTION: node_link_data(self)}

    @classmethod
    def from_json(cls, data):
        graph = node_link_graph(data[PYANNOTE_JSON_TRANSCRIPTION])
        mapping = {node: T(node) for node in graph}
        graph = nx.relabel_nodes(graph, mapping)
        return cls(graph=graph, **graph.graph)

    # === IPython Notebook displays ===========================================

    def _repr_svg_(self):
        from notebook import repr_transcription
        return repr_transcription(self)
