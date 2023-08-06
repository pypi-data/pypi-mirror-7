#! /usr/bin/env python

import pyslet.xml20081126.structures as xml
import pyslet.xmlnames20091208 as xmlns
import pyslet.xsdatatypes20041028 as xsi
import pyslet.html40_19991224 as html

import string


IMSQTI_NAMESPACE = "http://www.imsglobal.org/xsd/imsqti_v2p1"
"""The namespace used to recognise elements in XML documents."""

IMSQTI_SCHEMALOCATION = "http://www.imsglobal.org/xsd/imsqti_v2p1.xsd"
"""The location of the QTI 2.1 schema file on the IMS website."""

IMSQTI_ITEM_RESOURCETYPE = "imsqti_item_xmlv2p1"
"""The resource type to use for the QTI 2.1 items when added to content packages."""


class QTIError(Exception):

    """Abstract class used for all QTI v2 exceptions."""
    pass


class DeclarationError(QTIError):

    """Error raised when a variable declaration is invalid."""
    pass


class ProcessingError(QTIError):

    """Error raised when an invalid processing element is encountered."""
    pass


class SelectionError(QTIError):

    """Error raised when there is a problem with creating test forms."""
    pass


class QTIValidityError(QTIError):
    pass


def ValidateIdentifier(value, prefix='_'):
    """Decodes an identifier from a string::

            <xsd:simpleType name="identifier.Type">
                    <xsd:restriction base="xsd:NCName"/>
            </xsd:simpleType>

    This function takes a string that is supposed to match the production for
    NCName in XML and forces it to comply by replacing illegal characters with
    '_', except the ':' which is replaced with a hyphen for compatibility with
    previous versions of the QTI migraiton script.  If name starts with a valid
    name character but not a valid name start character, it is prefixed with '_'
    too, but the prefix string used can be overridden."""
    if value:
        goodName = []
        if not xmlns.IsNameStartChar(value[0]):
            goodName.append(prefix)
        elif value[0] == ':':
            # Previous versions of the migrate script didn't catch this problem
            # as a result, we deviate from its broken behaviour of using '-'
            # by using the prefix too.
            goodName.append(prefix)
        for c in value:
            if c == ':':
                goodName.append('-')
            elif xmlns.IsNameChar(c):
                goodName.append(c)
            else:
                goodName.append('_')
        return string.join(goodName, '')
    else:
        return prefix


class Orientation(xsi.Enumeration):

    """Orientation attribute values provide a hint to rendering systems that an
    element has an inherent vertical or horizontal interpretation::

            <xsd:simpleType name="orientation.Type">
                    <xsd:restriction base="xsd:NMTOKEN">
                            <xsd:enumeration value="horizontal"/>
                            <xsd:enumeration value="vertical"/>
                    </xsd:restriction>
            </xsd:simpleType>

    Defines constants for the above orientations.  Usage example::

            Orientation.horizontal

    Note that::

            Orientation.DEFAULT == None

    For more methods see :py:class:`~pyslet.xsdatatypes20041028.Enumeration`"""
    decode = {
        'horizontal': 1,
        'vertical': 2
    }
xsi.MakeEnumeration(Orientation)


class Shape(xsi.Enumeration):

    """A value of a shape is always accompanied by coordinates and an associated
    image which provides a context for interpreting them::

            <xsd:simpleType name="shape.Type">
                    <xsd:restriction base="xsd:NMTOKEN">
                            <xsd:enumeration value="circle"/>
                            <xsd:enumeration value="default"/>
                            <xsd:enumeration value="ellipse"/>
                            <xsd:enumeration value="poly"/>
                            <xsd:enumeration value="rect"/>
                    </xsd:restriction>
            </xsd:simpleType>

    Defines constants for the above types of Shape.  Usage example::

            Shape.circle

    Note that::

            Shape.DEFAULT == Shape.default

    For more methods see :py:class:`~pyslet.xsdatatypes20041028.Enumeration`"""
    decode = {
        'circle': 1,
        'default': 2,
        'ellipse': 3,
        'poly': 4,
        'rect': 5
    }
xsi.MakeEnumeration(Shape, 'default')


def CalculateShapeBounds(shape, coords):
    """Calculates a bounding rectangle from a Shape value and a
    :py:class:`pyslet.html40_19991224.Coords` instance."""
    if shape == Shape.circle:
        return [coords[0].GetValue(1024) - coords[2].GetValue(768),
                coords[1].GetValue(768) - coords[2].GetValue(768),
                coords[0].GetValue(1024) + coords[2].GetValue(768),
                coords[1].GetValue(768) + coords[2].GetValue(768)]
    elif shape == Shape.default:
        return [0, 0, 1024, 768]
    elif shape == Shape.ellipse:
        return [coords[0].GetValue(1024) - coords[2].GetValue(1024),
                coords[1].GetValue(768) - coords[3].GetValue(768),
                coords[0].GetValue(1024) + coords[2].GetValue(1024),
                coords[1].GetValue(768) + coords[3].GetValue(768)]
    elif shape == Shape.poly:
        output = [coords[0].GetValue(1024), coords[1].GetValue(768),
                  coords[0].GetValue(1024), coords[1].GetValue(768)]
        i = 1
        while 2 * i + 1 < len(coords):
            x = coords[2 * i].GetValue(1024)
            y = coords[2 * i + 1].GetValue(768)
            if x < output[0]:
                output[0] = x
            elif x > output[2]:
                output[2] = x
            if y < output[1]:
                output[1] = y
            elif y > output[3]:
                output[3] = y
        return output
    elif shape == Shape.rect:
        return [coords[0].GetValue(1024), coords[1].GetValue(768),
                coords[2].GetValue(1024), coords[3].GetValue(768)]
    else:
        raise ValueError("Unknown value for shape: %s" % str(shape))


def OffsetShape(shape, coords, xOffset, yOffset):
    """Interprets the shape and coords relative to the given offset and maps them back to the origin.

    In other words, xOffset and yOffset are subtracted from the coordinates."""
    if shape == Shape.circle:
        coords[0].Add(-xOffset)
        coords[1].Add(-yOffset)
    elif shape == Shape.default:
        pass
    elif shape == Shape.ellipse:
        coords[0].Add(-xOffset)
        coords[1].Add(-yOffset)
    elif shape == Shape.poly:
        i = 0
        while 2 * i + 1 < len(coords):
            coords[2 * i].Add(-xOffset)
            coords[2 * i + 1].Add(-yOffset)
    elif shape == Shape.rect:
        coords[0].Add(-xOffset)
        coords[1].Add(-yOffset)
        coords[2].Add(-xOffset)
        coords[3].Add(-yOffset)
    else:
        raise ValueError("Unknown value for shape: %s" % str(shape))


class ShapeElementMixin:
    XMLATTR_shape = ('shape', Shape.DecodeLowerValue, Shape.EncodeValue)
    XMLATTR_coords = ('coords', html.Coords, html.Coords.__unicode__)

    def __init__(self):
        self.shape = Shape.DEFAULT  # : The shape
        self.coords = None			#: A list of Length values

    def TestPoint(self, point, width, height):
        """Tests *point* to see if it is in this area."""
        x, y = point
        if self.shape == Shape.circle:
            return self.coords.TestCircle(x, y, width, height)
        elif self.shape == Shape.default:
            # The entire region
            return x >= 0 and y >= 0 and (
                width is None or x <= width) and (
                height is None or y <= height)
        elif self.shape == Shape.ellipse:
            # Ellipse is deprecated because there is no HTML equivalent test
            return self.TestEllipse(x, y, width, height)
        elif self.shape == Shape.poly:
            return self.coords.TestPoly(x, y, width, height)
        elif self.shape == Shape.rect:
            return self.coords.TestRect(x, y, width, height)
        else:
            raise ValueError("Unknown Shape type")

    def TestEllipse(self, x, y, width, height):
        """Tests an x,y point against an ellipse with these coordinates.

        HTML does not define ellipse, we take our definition from the QTI
        specification itself: center-x, center-y, x-radius, y-radius."""
        if len(self.coords.values) < 4:
            raise ValueError(
                "Ellipse test requires 4 coordinates: %s" % str(
                    self.coords.values))
        dx = x - self.coords.values[0].GetValue(width)
        dy = y - self.coords.values[1].GetValue(height)
        rx = self.coords.values[2].GetValue(width)
        ry = self.coords.values[3].GetValue(height)
        return dx * dx * ry * ry + dy * dy * rx * rx <= rx * rx * ry * ry


class ShowHide(xsi.Enumeration):

    """Used to control content visibility with variables
    ::

            <xsd:simpleType name="showHide.Type">
                    <xsd:restriction base="xsd:NMTOKEN">
                            <xsd:enumeration value="hide"/>
                            <xsd:enumeration value="show"/>
                    </xsd:restriction>
            </xsd:simpleType>

    Note that ShowHide.DEFAULT == ShowHide.show"""
    decode = {
        'show': 1,
        'hide': 2
    }
xsi.MakeEnumeration(ShowHide, 'show')


class View(xsi.Enumeration):

    """Used to represent roles when restricting view::

            <xsd:simpleType name="view.Type">
                    <xsd:restriction base="xsd:NMTOKEN">
                            <xsd:enumeration value="author"/>
                            <xsd:enumeration value="candidate"/>
                            <xsd:enumeration value="proctor"/>
                            <xsd:enumeration value="scorer"/>
                            <xsd:enumeration value="testConstructor"/>
                            <xsd:enumeration value="tutor"/>
                    </xsd:restriction>
            </xsd:simpleType>

    Defines constants for the above views.  Usage example::

            View.candidate

    There is no default view.  Views are represented in XML as space-separated
    lists of values.  Typical usage::

            view=View.DecodeValueDict("tutor scorer")
            # returns...
            { View.tutor:'tutor', View.scorer:'scorer' }
            View.EncodeValueDict(view)
            # returns...
            "scorer tutor"

    For more methods see :py:class:`~pyslet.xsdatatypes20041028.Enumeration`"""
    decode = {
        'author': 1,
        'candidate': 2,
        'proctor': 3,
        'scorer': 4,
        'testConstructor': 5,
        'tutor': 6
    }
xsi.MakeEnumeration(View)
xsi.MakeLowerAliases(View)


class QTIElement(xmlns.XMLNSElement):

    """Basic element to represent all QTI elements"""

    def AddToCPResource(self, cp, resource, beenThere):
        """We need to add any files with URL's in the local file system to the
        content package.

        beenThere is a dictionary we use for mapping URLs to File objects so
        that we don't keep adding the same linked resource multiple times.

        This implementation is a little more horrid, we avoid circular module
        references by playing dumb about our children.  HTML doesn't actually
        know anything about QTI even though QTI wants to define children for
        some XHTML elements so we pass the call only to "CP-Aware" elements."""
        for child in self.GetChildren():
            if hasattr(child, 'AddToCPResource'):
                child.AddToCPResource(cp, resource, beenThere)


class QTIDocument(xmlns.XMLNSDocument):

    """Used to represent all documents representing information from the QTI v2
    specification."""

    classMap = {}

    def __init__(self, **args):
        xmlns.XMLNSDocument.__init__(self, defaultNS=IMSQTI_NAMESPACE, **args)
        self.MakePrefix(xsi.XMLSCHEMA_NAMESPACE, 'xsi')
        if isinstance(self.root, QTIElement):
            self.root.SetAttribute(
                (xsi.XMLSCHEMA_NAMESPACE,
                 'schemaLocation'),
                IMSQTI_NAMESPACE +
                ' ' +
                IMSQTI_SCHEMALOCATION)

    def GetElementClass(self, name):
        return QTIDocument.classMap.get(
            name, QTIDocument.classMap.get(
                (name[0], None), xmlns.XMLNSElement))

    def AddToContentPackage(self, cp, metadata, dName=None):
        """Copies this QTI document into a content package and returns the resource ID used.

        An optional directory name can be specified in which to put the resource files."""
        # We call the element's AddToContentPackage method which returns the new resource
        # The document's base is automatically set to the URI of the resource
        # entry point
        resource = self.root.AddToContentPackage(cp, metadata, dName)
        # Finish by writing out the document to the new baseURI
        self.Create()
        return resource


class DeclarationContainer:

    """An abstract mix-in class used to manage a dictionary of variable
    declarations."""

    def __init__(self):
        #: a dictionary of outcome variable declarations
        self.declarations = {}

    def RegisterDeclaration(self, declaration):
        if declaration.identifier in self.declarations:
            raise DeclarationError
        else:
            self.declarations[declaration.identifier] = declaration

    def IsDeclared(self, identifier):
        return identifier in self.declarations

    def GetDeclaration(self, identifier):
        return self.declarations.get(identifier, None)


def GetTemplateRef(value):
    """Given a string used to set an attribute of an *...orTemplateRef* type
    this function returns the name of the variable being referred to or None if
    the value does not look like a template variable reference."""
    if value.startswith('{') and value.endswith('}'):
        idValue = value[1:-1]
        if xsi.IsValidNCName(idValue):
            return idValue
    return None
