# encoding: utf-8

"""
lxml custom element classes for slide master-related XML elements.
"""

from __future__ import absolute_import

from .ns import qn
from .shared import BaseOxmlElement, Element


class CT_SlideLayoutIdList(BaseOxmlElement):
    """
    ``<p:sldLayoutIdLst>`` element, child of ``<p:sldMaster>`` containing
    references to the slide layouts that inherit from the slide master.
    """
    def __len__(self):
        """
        Return the number of ``<p:sldLayoutId>`` child elements
        """
        sldLayoutId_lst = self.findall(qn('p:sldLayoutId'))
        return len(sldLayoutId_lst)

    @classmethod
    def new(cls):
        """
        Return a new ``<p:sldLayoutIdLst>`` element.
        """
        return Element('p:sldLayoutIdLst')

    @property
    def sldLayoutId_lst(self):
        """
        Sequence of ``<p:sldLayoutId>`` child elements
        """
        return self.findall(qn('p:sldLayoutId'))


class CT_SlideLayoutIdListEntry(BaseOxmlElement):
    """
    ``<p:sldLayoutId>`` element, child of ``<p:sldLayoutIdLst>`` containing
    a reference to a slide layout.
    """
    @property
    def rId(self):
        return self.get(qn('r:id'))


class CT_SlideMaster(BaseOxmlElement):
    """
    ``<p:sldMaster>`` element, root of a slide master part
    """
    def get_or_add_sldLayoutIdLst(self):
        """
        Return the sldLayoutIdLst child element, newly added if not present.
        """
        sldLayoutIdLst = self.sldLayoutIdLst
        if sldLayoutIdLst is None:
            sldLayoutIdLst = self._add_sldLayoutIdLst()
        return sldLayoutIdLst

    @property
    def sldLayoutIdLst(self):
        """
        The first ``<p:sldLayoutIdLst>`` child element, or |None| if not
        present.
        """
        return self.find(qn('p:sldLayoutIdLst'))

    def _add_sldLayoutIdLst(self):
        """
        Return a newly added sldLayoutIdLst child element. Assumes one is not
        present.
        """
        sldLayoutIdLst = CT_SlideLayoutIdList.new()
        self.insert_element_before(
            sldLayoutIdLst, 'p:transition', 'p:timing', 'p:hf', 'p:txStyles',
            'p:extLst'
        )
        return sldLayoutIdLst
