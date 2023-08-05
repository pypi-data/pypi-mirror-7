# -*- coding: utf-8 -*-
# cython: language_level=3, always_allow_keywords=True

## Copyright 2009-2014 by LivingLogic AG, Bayreuth/Germany
## Copyright 2009-2014 by Walter Dörwald
##
## All Rights Reserved
##
## See ll/xist/__init__.py for the license


from ll import misc
from ll.xist import xsc


###
### Processing instruction for comments
###

class note(xsc.ProcInst):
	"""
	A :class:`note` processing instruction contains a comment (which will be
	ignored when compiling the template).
	"""


###
### Processing instructions for output
###

class print_(xsc.ProcInst):
	"""
	Prints the expression in the processing instruction data.
	"""
	xmlname = "print"


class printx(xsc.ProcInst):
	"""
	Prints the expression in the processing instruction data and escapes
	the characters ``&``, ``<``, ``>``, ``'`` and ``"``.
	"""


###
### Processing instruction for statements
###

class code(xsc.ProcInst):
	"""
	A :class:`code` processing instruction contains a statement (such as an
	assignment or augmented assignment) or expressions (with side effects).
	"""


###
### Element for conditional attributes
###

class attr_if(xsc.AttrElement):
	"""
	Conditional attribute: The ``cond`` attribute is a expression. If this
	expression is true, the attribute will be output normally (with the elements
	content as content (except for boolean attributes)), otherwise the attribute
	itself will be skipped. Outside of an attribute this will produce a normal
	UL4 ``if`` around its content.
	"""

	class Attrs(xsc.Element.Attrs):
		class cond(xsc.TextAttr): required = True

	def publish(self, publisher):
		yield publisher.encode('<?if {cond}?>'.format(cond=str(self.attrs.cond)))
		yield from self.content.publish(publisher)
		yield publisher.encode('<?end if?>')

	def publishattr(self, publisher, attr):
		publisher.inattr += 1
		yield publisher.encode('<?if {cond}?> {name}="'.format(cond=str(self.attrs.cond), name=attr._publishname(publisher)))
		publisher.pushtextfilter(misc.xmlescape_attr)
		yield from self.content.publish(publisher)
		publisher.poptextfilter()
		yield publisher.encode('"<?end if?>')
		publisher.inattr -= 1

	def publishboolattr(self, publisher, attr):
		name = attr._publishname(publisher)
		yield publisher.encode('<?if {cond}?> {name}'.format(cond=str(self.attrs.cond), name=name))
		if publisher.xhtml>0:
			yield publisher.encode('="{name}"'.format(name=name))
		yield publisher.encode('<?end if?>')


###
### Processing instructions for block structures (if/elif/else/for and def)
###

class if_(xsc.ProcInst):
	xmlname = "if"
	prettyindentbefore = 0
	prettyindentafter = 1



class elif_(xsc.ProcInst):
	xmlname = "elif"
	prettyindentbefore = -1
	prettyindentafter = 1


class else_(xsc.ProcInst):
	xmlname = "else"
	prettyindentbefore = -1
	prettyindentafter = 1


class end(xsc.ProcInst):
	"""
	Ends an :class:`if_`, :class:`for_` or :class:`def_`. The PI value may be the
	type of the block (either ``"if"``, ``"for"`` or ``"def"``). If the value is
	empty the innermost block will be closed without any checks for the type of
	block.
	"""
	prettyindentbefore = -1
	prettyindentafter = 0


class for_(xsc.ProcInst):
	xmlname = "for"
	prettyindentbefore = 0
	prettyindentafter = 1


class break_(xsc.ProcInst):
	xmlname = "break"


class continue_(xsc.ProcInst):
	xmlname = "continue"


class return_(xsc.ProcInst):
	xmlname = "return"


class def_(xsc.ProcInst):
	xmlname = "def"
	prettyindentbefore = 0
	prettyindentafter = 1
