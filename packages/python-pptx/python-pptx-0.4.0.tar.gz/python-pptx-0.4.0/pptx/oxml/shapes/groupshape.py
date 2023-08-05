# encoding: utf-8

"""
lxml custom element classes for shape tree-related XML elements.
"""

from __future__ import absolute_import

from .autoshape import CT_Shape
from .graphfrm import CT_GraphicalObjectFrame
from ..ns import qn
from .picture import CT_Picture
from .shared import BaseShapeElement
from ..shared import BaseOxmlElement, Element


class CT_GroupShape(BaseShapeElement):
    """
    Used for the shape tree (``<p:spTree>``) element as well as the group
    shape (``<p:grpSp>``) element.
    """

    _shape_tags = (
        qn('p:sp'), qn('p:grpSp'), qn('p:graphicFrame'), qn('p:cxnSp'),
        qn('p:pic'), qn('p:contentPart')
    )

    def add_autoshape(self, id_, name, prst, x, y, cx, cy):
        """
        Append a new ``<p:sp>`` shape to the group/shapetree having the
        properties specified in call.
        """
        sp = CT_Shape.new_autoshape_sp(id_, name, prst, x, y, cx, cy)
        self.insert_element_before(sp, 'p:extLst')
        return sp

    def add_pic(self, id_, name, desc, rId, x, y, cx, cy):
        """
        Append a ``<p:pic>`` shape to the group/shapetree having properties
        as specified in call.
        """
        pic = CT_Picture.new_pic(id_, name, desc, rId, x, y, cx, cy)
        self.insert_element_before(pic, 'p:extLst')
        return pic

    def add_placeholder(self, id_, name, ph_type, orient, sz, idx):
        """
        Append a newly-created placeholder ``<p:sp>`` shape having the
        specified placeholder properties.
        """
        sp = CT_Shape.new_placeholder_sp(
            id_, name, ph_type, orient, sz, idx
        )
        self.insert_element_before(sp, 'p:extLst')
        return sp

    def add_table(self, id_, name, rows, cols, x, y, cx, cy):
        """
        Append a ``<p:graphicFrame>`` shape containing a table as specified
        in call.
        """
        graphicFrame = CT_GraphicalObjectFrame.new_table(
            id_, name, rows, cols, x, y, cx, cy
        )
        self.insert_element_before(graphicFrame, 'p:extLst')
        return graphicFrame

    def add_textbox(self, id_, name, x, y, cx, cy):
        """
        Append a newly-created textbox ``<p:sp>`` shape having the specified
        position and size.
        """
        sp = CT_Shape.new_textbox_sp(id_, name, x, y, cx, cy)
        self.insert_element_before(sp, 'p:extLst')
        return sp

    def get_or_add_xfrm(self):
        """
        Return the ``<a:xfrm>`` grandchild element, newly-added if not
        present.
        """
        return self.grpSpPr.get_or_add_xfrm()

    @property
    def grpSpPr(self):
        """
        The required ``<p:grpSpPr>`` child element
        """
        return self.find(qn('p:grpSpPr'))

    def iter_shape_elms(self):
        """
        Generate each child of this ``<p:spTree>`` element that corresponds
        to a shape, in the sequence they appear in the XML.
        """
        for elm in self.iterchildren():
            if elm.tag in self._shape_tags:
                yield elm

    @property
    def xfrm(self):
        """
        The ``<a:xfrm>`` grandchild element or |None| if not found
        """
        return self.grpSpPr.xfrm


class CT_GroupShapeProperties(BaseOxmlElement):
    """
    The ``<p:grpSpPr>`` element
    """
    def get_or_add_xfrm(self):
        """
        Return the <a:xfrm> child element, newly added if not already
        present.
        """
        xfrm = self.xfrm
        if xfrm is None:
            xfrm = Element('a:xfrm')
            self.insert(0, xfrm)
        return xfrm

    @property
    def xfrm(self):
        """
        The ``<a:xfrm>`` child element, or |None| if not present
        """
        return self.find(qn('a:xfrm'))
