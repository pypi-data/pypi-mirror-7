#! /usr/bin/env python

import pyslet.xml20081126.structures as xml
import pyslet.xmlnames20091208 as xmlns
import pyslet.xsdatatypes20041028 as xsi
import pyslet.html40_19991224 as html

import pyslet.qtiv2.core as core
import pyslet.qtiv2.items as items

import string
import itertools
import random
import types


class AssessmentTest(core.QTIElement, core.DeclarationContainer):

    """A test is a group of assessmentItems with an associated set of rules that
    determine which of the items the candidate sees, in what order, and in what
    way the candidate interacts with them. The rules describe the valid paths
    through the test, when responses are submitted for response processing and
    when (if at all) feedback is to be given::

            <xsd:attributeGroup name="assessmentTest.AttrGroup">
                    <xsd:attribute name="identifier" type="string.Type" use="required"/>
                    <xsd:attribute name="title" type="string.Type" use="required"/>
                    <xsd:attribute name="toolName" type="string256.Type" use="optional"/>
                    <xsd:attribute name="toolVersion" type="string256.Type" use="optional"/>
            </xsd:attributeGroup>

            <xsd:group name="assessmentTest.ContentGroup">
                    <xsd:sequence>
                            <xsd:element ref="outcomeDeclaration" minOccurs="0" maxOccurs="unbounded"/>
                            <xsd:element ref="timeLimits" minOccurs="0" maxOccurs="1"/>
                            <xsd:element ref="testPart" minOccurs="1" maxOccurs="unbounded"/>
                            <xsd:element ref="outcomeProcessing" minOccurs="0" maxOccurs="1"/>
                            <xsd:element ref="testFeedback" minOccurs="0" maxOccurs="unbounded"/>
                    </xsd:sequence>
            </xsd:group>"""
    XMLNAME = (core.IMSQTI_NAMESPACE, 'assessmentTest')
    XMLATTR_identifier = 'identifier'
    XMLATTR_title = 'title'
    XMLATTR_toolName = 'toolName'
    XMLATTR_toolVersion = 'toolVersion'
    XMLCONTENT = xmlns.ElementContent

    def __init__(self, parent):
        core.QTIElement.__init__(self, parent)
        core.DeclarationContainer.__init__(self)
        self.identifier = None
        self.title = None
        self.toolName = None
        self.toolVersion = None
        self.OutcomeDeclaration = []
        self.TimeLimits = None
        self.TestPart = []
        self.OutcomeProcessing = None
        self.TestFeedback = []
        # : a dictionary of testPart, assessmentSection and assessmentItemRef keyed on identifier
        self.parts = {}

    def GetChildren(self):
        for d in self.OutcomeDeclaration:
            yield d
        if self.TimeLimits:
            yield self.TimeLimits
        for d in self.TestPart:
            yield d
        if self.OutcomeProcessing:
            yield self.OutcomeProcessing
        for child in self.TestFeedback:
            yield child

    def ContentChanged(self):
        self.SortDeclarations()

    def SortDeclarations(self):
        """Sort the outcome declarations so that they are in identifier order.
        This is not essential but it does help ensure that output is
        predictable. This method is called automatically when reading items from
        XML files."""
        self.OutcomeDeclaration.sort()

    def RegisterPart(self, part):
        """Registers a testPart, asssessmentSection or assessmentItemRef in
        :py:attr:`parts`."""
        if part.identifier in self.parts:
            raise KeyError("Duplicate identifier: %s" % part.identifier)
        else:
            self.parts[part.identifier] = part

    def GetPart(self, identifier):
        """Returns the testPart, assessmentSection or assessmentItemRef with the
        given identifier."""
        return self.parts[identifier]


class NavigationMode(xsi.Enumeration):

    """The navigation mode determines the general paths that the candidate may
    take. A testPart in linear mode restricts the candidate to attempt each item
    in turn. Once the candidate moves on they are not permitted to return. A
    testPart in nonlinear mode removes this restriction - the candidate is free
    to navigate to any item in the test at any time::

            <xsd:simpleType name="navigationMode.Type">
                    <xsd:restriction base="xsd:NMTOKEN">
                            <xsd:enumeration value="linear"/>
                            <xsd:enumeration value="nonlinear"/>
                    </xsd:restriction>
            </xsd:simpleType>

    Defines constants for the above modes.  Usage example::

            NavigationMode.linear

    Note that::

            NavigationMode.DEFAULT == None

    For more methods see :py:class:`~pyslet.xsdatatypes20041028.Enumeration`"""
    decode = {
        'linear': 1,
        'nonlinear': 2
    }
xsi.MakeEnumeration(NavigationMode)


class SubmissionMode(xsi.Enumeration):

    """The submission mode determines when the candidate's responses are
    submitted for response processing. A testPart in individual mode requires
    the candidate to submit their responses on an item-by-item basis. In
    simultaneous mode the candidate's responses are all submitted together at
    the end of the testPart::

            <xsd:simpleType name="submissionMode.Type">
                    <xsd:restriction base="xsd:NMTOKEN">
                            <xsd:enumeration value="individual"/>
                            <xsd:enumeration value="simultaneous"/>
                    </xsd:restriction>
            </xsd:simpleType>

    Defines constants for the above modes.  Usage example::

            SubmissionMode.individual

    Note that::

            SubmissionMode.DEFAULT == None

    For more methods see :py:class:`~pyslet.xsdatatypes20041028.Enumeration`"""
    decode = {
        'individual': 1,
        'simultaneous': 2
    }
xsi.MakeEnumeration(SubmissionMode)


class TestPart(core.QTIElement):

    """Each test is divided into one or more parts which may in turn be divided
    into sections, sub-sections, and so on::

            <xsd:attributeGroup name="testPart.AttrGroup">
                    <xsd:attribute name="identifier" type="identifier.Type" use="required"/>
                    <xsd:attribute name="navigationMode" type="navigationMode.Type" use="required"/>
                    <xsd:attribute name="submissionMode" type="submissionMode.Type" use="required"/>
            </xsd:attributeGroup>

            <xsd:group name="testPart.ContentGroup">
                    <xsd:sequence>
                            <xsd:element ref="preCondition" minOccurs="0" maxOccurs="unbounded"/>
                            <xsd:element ref="branchRule" minOccurs="0" maxOccurs="unbounded"/>
                            <xsd:element ref="itemSessionControl" minOccurs="0" maxOccurs="1"/>
                            <xsd:element ref="timeLimits" minOccurs="0" maxOccurs="1"/>
                            <xsd:element ref="assessmentSection" minOccurs="1" maxOccurs="unbounded"/>
                            <xsd:element ref="testFeedback" minOccurs="0" maxOccurs="unbounded"/>
                    </xsd:sequence>
            </xsd:group>"""
    XMLNAME = (core.IMSQTI_NAMESPACE, 'testPart')
    XMLATTR_identifier = 'identifier'
    XMLATTR_navigationMode = (
        'navigationMode',
        NavigationMode.DecodeValue,
        NavigationMode.EncodeValue)
    XMLATTR_submissionMode = (
        'submissionMode',
        SubmissionMode.DecodeValue,
        SubmissionMode.EncodeValue)
    XMLCONTENT = xmlns.ElementContent

    def __init__(self, parent):
        core.QTIElement.__init__(self, parent)
        self.identifier = None
        self.navigationMode = NavigationMode.DEFAULT
        self.submissionMode = SubmissionMode.DEFAULT
        self.PreCondition = []
        self.BranchRule = []
        self.ItemSessionControl = None
        self.TimeLimits = None
        self.AssessmentSection = []
        self.TestFeedback = []

    def GetChildren(self):
        for c in self.PreCondition:
            yield c
        for c in self.BranchRule:
            yield c
        if self.ItemSessionControl:
            yield self.ItemSessionControl
        if self.TimeLimits:
            yield self.TimeLimits
        for c in self.AssessmentSection:
            yield c
        for c in self.TestFeedback:
            yield c

    def ContentChanged(self):
        test = self.FindParent(AssessmentTest)
        if test:
            test.RegisterPart(self)

    def CheckPreConditions(self, state):
        """Returns True if this testPart's pre-conditions are satisfied or if
        there are no pre-conditions in effect."""
        for c in self.PreCondition:
            if not c.Evaluate(state):
                return False
        return True

    def GetBranchTarget(self, state):
        """Returns the identifier of the testPart to branch to, or the
        pre-defined EXIT_TEST identifier.  If there is no branch rule in effect
        then None is returned.  *state* is a
        :py:class:`variables.TestSessionState` instance used to evaluate the
        branch rule expressions."""
        test = self.FindParent(AssessmentTest)
        for r in self.BranchRule:
            if r.Evaluate(state):
                try:
                    if r.target == u"EXIT_TEST":
                        return r.target
                    target = test.GetPart(r.target)
                    if not isinstance(target, TestPart):
                        # test parts can only point at other test parts
                        raise core.ProcessingError(
                            "Target of testPart branch rule is not a testPart: %s" %
                            r.target)
                    return r.target
                except KeyError:
                    raise core.ProcessingError(
                        "Target of testPart branch rule has not been declared: %s" %
                        r.target)


class Selection(core.QTIElement):

    """The selection class specifies the rules used to select the child elements
    of a section for each test session::

            <xsd:attributeGroup name="selection.AttrGroup">
                    <xsd:attribute name="select" type="integer.Type" use="required"/>
                    <xsd:attribute name="withReplacement" type="boolean.Type" use="optional"/>
                    <xsd:anyAttribute namespace="##other"/>
            </xsd:attributeGroup>

            <xsd:group name="selection.ContentGroup">
                    <xsd:sequence>
                    <xsd:any namespace="##any" minOccurs="0" maxOccurs="unbounded" processContents="skip"/>
                    </xsd:sequence>
            </xsd:group>"""
    XMLNAME = (core.IMSQTI_NAMESPACE, 'selection')
    XMLATTR_select = ('select', xsi.DecodeInteger, xsi.EncodeInteger)
    XMLATTR_withReplacement = (
        'withReplacement', xsi.DecodeBoolean, xsi.EncodeBoolean)
    XMLCONTENT = xmlns.ElementContent

    def __init__(self, parent):
        core.QTIElement.__init__(self, parent)
        self.select = None
        self.withReplacement = False


class Ordering(core.QTIElement):

    """The ordering class specifies the rule used to arrange the child elements
    of a section following selection. If no ordering rule is given we assume
    that the elements are to be ordered in the order in which they are defined::

            <xsd:attributeGroup name="ordering.AttrGroup">
                    <xsd:attribute name="shuffle" type="boolean.Type" use="required"/>
                    <xsd:anyAttribute namespace="##other"/>
            </xsd:attributeGroup>

            <xsd:group name="ordering.ContentGroup">
                    <xsd:sequence>
                    <xsd:any namespace="##any" minOccurs="0" maxOccurs="unbounded" processContents="skip"/>
                    </xsd:sequence>
            </xsd:group>"""
    XMLNAME = (core.IMSQTI_NAMESPACE, 'ordering')
    XMLATTR_shuffle = ('shuffle', xsi.DecodeBoolean, xsi.EncodeBoolean)
    XMLCONTENT = xmlns.ElementContent

    def __init__(self, parent):
        core.QTIElement.__init__(self, parent)
        self.shuffle = False


class SectionPart(core.QTIElement):

    """Sections group together individual item references and/or sub-sections. A
    number of common parameters are shared by both types of child element::

            <xsd:attributeGroup name="sectionPart.AttrGroup">
                    <xsd:attribute name="identifier" type="identifier.Type" use="required"/>
                    <xsd:attribute name="required" type="boolean.Type" use="optional"/>
                    <xsd:attribute name="fixed" type="boolean.Type" use="optional"/>
            </xsd:attributeGroup>

            <xsd:group name="sectionPart.ContentGroup">
                    <xsd:sequence>
                            <xsd:element ref="preCondition" minOccurs="0" maxOccurs="unbounded"/>
                            <xsd:element ref="branchRule" minOccurs="0" maxOccurs="unbounded"/>
                            <xsd:element ref="itemSessionControl" minOccurs="0" maxOccurs="1"/>
                            <xsd:element ref="timeLimits" minOccurs="0" maxOccurs="1"/>
                    </xsd:sequence>
            </xsd:group>"""
    XMLATTR_identifier = 'identifier'
    XMLATTR_required = ('required', xsi.DecodeBoolean, xsi.EncodeBoolean)
    XMLATTR_fixed = ('fixed', xsi.DecodeBoolean, xsi.EncodeBoolean)

    def __init__(self, parent):
        core.QTIElement.__init__(self, parent)
        self.identifier = None
        self.required = False
        self.fixed = False
        self.PreCondition = []
        self.BranchRule = []
        self.ItemSessionControl = None
        self.TimeLimits = None

    def GetChildren(self):
        for c in self.PreCondition:
            yield c
        for c in self.BranchRule:
            yield c
        if self.ItemSessionControl:
            yield self.ItemSessionControl
        if self.TimeLimits:
            yield self.TimeLimits

    def ContentChanged(self):
        test = self.FindParent(AssessmentTest)
        if test:
            test.RegisterPart(self)

    def CheckPreConditions(self, state):
        """Returns True if this item or section's pre-conditions are satisfied
        or if there are no pre-conditions in effect."""
        test = self.FindParent(AssessmentTest)
        testPart = self.FindParent(TestPart)
        if testPart.navigationMode != NavigationMode.linear:
            return None
        for c in self.PreCondition:
            if not c.Evaluate(state):
                return False
        return True

    def GetBranchTarget(self, state):
        """Returns the identifier of the next item or section to branch to, or
        one of the pre-defined EXIT_* identifiers.  If there is no branch rule
        in effect then None is returned.  *state* is a
        :py:class:`variables.TestSessionState` instance used to evaluate the
        branch rule expressions."""
        test = self.FindParent(AssessmentTest)
        testPart = self.FindParent(TestPart)
        if testPart.navigationMode != NavigationMode.linear:
            return None
        for r in self.BranchRule:
            if r.Evaluate(state):
                try:
                    if r.target in (u"EXIT_SECTION", u"EXIT_TESTPART", u"EXIT_TEST"):
                        return r.target
                    target = test.GetPart(r.target)
                    if not isinstance(target, SectionPart):
                        # section parts can only point at other section parts
                        raise core.ProcessingError(
                            "Target of section or item branch rule is not a section or item: %s" %
                            r.target)
                    if target.FindParent(TestPart) is not testPart:
                        raise core.ProcessingError(
                            "Target or section or item branch rule is not in the same testPart: %s" %
                            r.target)
                    return r.target
                except KeyError:
                    raise core.ProcessingError(
                        "Target of section or item branch rule has not been declared: %s" %
                        r.target)


class AssessmentSection(SectionPart):

    """Represents assessmentSection element
    ::

            <xsd:attributeGroup name="assessmentSection.AttrGroup">
                    <xsd:attributeGroup ref="sectionPart.AttrGroup"/>
                    <xsd:attribute name="title" type="string.Type" use="required"/>
                    <xsd:attribute name="visible" type="boolean.Type" use="required"/>
                    <xsd:attribute name="keepTogether" type="boolean.Type" use="optional"/>
            </xsd:attributeGroup>

            <xsd:group name="assessmentSection.ContentGroup">
                    <xsd:sequence>
                            <xsd:group ref="sectionPart.ContentGroup"/>
                            <xsd:element ref="selection" minOccurs="0" maxOccurs="1"/>
                            <xsd:element ref="ordering" minOccurs="0" maxOccurs="1"/>
                            <xsd:element ref="rubricBlock" minOccurs="0" maxOccurs="unbounded"/>
                            <xsd:group ref="sectionPart.ElementGroup" minOccurs="0" maxOccurs="unbounded"/>
                    </xsd:sequence>
            </xsd:group>"""
    XMLNAME = (core.IMSQTI_NAMESPACE, 'assessmentSection')
    XMLATTR_title = 'title'
    XMLATTR_visible = ('visible', xsi.DecodeBoolean, xsi.EncodeBoolean)
    XMLATTR_keepTogether = (
        'keepTogether', xsi.DecodeBoolean, xsi.EncodeBoolean)
    XMLCONTENT = xmlns.ElementContent

    def __init__(self, parent):
        SectionPart.__init__(self, parent)
        self.title = None
        self.visible = None
        self.keepTogether = True
        self.Selection = None
        self.Ordering = None
        self.RubricBlock = []
        self.SectionPart = []

    def GetChildren(self):
        for c in SectionPart.GetChildren(self):
            yield c
        if self.Selection:
            yield self.Selection
        if self.Ordering:
            yield self.Ordering
        for c in self.RubricBlock:
            yield c
        for c in self.SectionPart:
            yield c


class AssessmentItemRef(SectionPart):

    """Items are incorporated into the test by reference and not by direct
    aggregation::

            <xsd:attributeGroup name="assessmentItemRef.AttrGroup">
                    <xsd:attributeGroup ref="sectionPart.AttrGroup"/>
                    <xsd:attribute name="href" type="uri.Type" use="required"/>
                    <xsd:attribute name="category" use="optional">
                            <xsd:simpleType>
                                    <xsd:list itemType="identifier.Type"/>
                            </xsd:simpleType>
                    </xsd:attribute>
            </xsd:attributeGroup>

            <xsd:group name="assessmentItemRef.ContentGroup">
                    <xsd:sequence>
                            <xsd:group ref="sectionPart.ContentGroup"/>
                            <xsd:element ref="variableMapping" minOccurs="0" maxOccurs="unbounded"/>
                            <xsd:element ref="weight" minOccurs="0" maxOccurs="unbounded"/>
                            <xsd:element ref="templateDefault" minOccurs="0" maxOccurs="unbounded"/>
                    </xsd:sequence>
            </xsd:group>"""
    XMLNAME = (core.IMSQTI_NAMESPACE, 'assessmentItemRef')
    XMLATTR_href = ('href', html.DecodeURI, html.EncodeURI)
    XMLATTR_category = ('category', None, None, types.ListType)
    XMLCONTENT = xmlns.ElementContent

    def __init__(self, parent):
        SectionPart.__init__(self, parent)
        self.href = None
        self.item = None
        self.category = []
        self.VariableMapping = []
        self.Weight = []
        self.TemplateDefault = []

    def GetChildren(self):
        for c in SectionPart.GetChildren(self):
            yield c
        for c in self.VariableMapping:
            yield c
        for c in self.Weight:
            yield c
        for c in self.TemplateDefault:
            yield c

    def GetItem(self):
        """Returns the AssessmentItem referred to by this reference."""
        if self.item is None:
            if self.href:
                itemLocation = self.ResolveURI(self.href)
                doc = core.QTIDocument(baseURI=itemLocation)
                doc.Read()
                if isinstance(doc.root, items.AssessmentItem):
                    self.item = doc.root
        return self.item

    def SetTemplateDefaults(self, itemState, testState):
        for td in self.TemplateDefault:
            td.Run(itemState, testState)


class TestForm(object):

    """A TestForm is a particular instance of a test, after selection and
    ordering rules have been applied.

    QTI tests can contain selection and ordering rules that enable basic
    variation between instances, or 'forms' of the test.  Selection and ordering
    is not the only source of variation but it provides the basic framework for
    the test.

    The TestForm acts like a (read-only) sequence of component identifiers.  The
    identifiers are the identifiers of the test components in the order they
    have been selected.  Identifiers of test parts and sections are included as
    they are legitimate targets of branch rules and may have their own
    pre-conditions, however, the sequence also contains closing identifiers for
    each section and test part.  A closing identifier is the identifier of the
    section or test part preceded by "-".  For example, a simple test with a
    single part and a single section might appear like this::

            [ "", "PartI", "SectionA", "Q1", "Q2", "-SectionA", "-PartI" ]

    Notice that index 0 is always an empty string corresponding to the test itself."""

    def __init__(self, test):
        self.test = test		#: the test from which this form was created
        self.components = []  # : the ordered list of identifiers
        #: a mapping from component identifiers to (lists of) indexes into the component list
        self.map = {}
        # Index 0 represents the test itself!
        self.components.append("")
        for part in self.test.TestPart:
            self.components.append(part.identifier)
            # A part always contains all child sections
            for s in part.AssessmentSection:
                self.components.append(s.identifier)
                # no shuffling in test parts, just add a hidden section as a
                # block
                self.components.extend(self.Select(s))
                self.components.append(u"-" + s.identifier)
            self.components.append(u"-" + part.identifier)
        for i in xrange(len(self.components)):
            id = self.components[i]
            if id in self.map:
                self.map[id].append(i)
            else:
                self.map[id] = [i]

    def Select(self, section, expandChildren=True):
        """Runs the selection and ordering rules for *section*.

        It returns a list of identifiers, not including the identifier of the section
        itself."""
        children = section.SectionPart
        if section.Ordering:
            shuffle = section.Ordering.shuffle
        else:
            shuffle = False
        if section.Selection:
            targetSize = section.Selection.select
            withReplacement = section.Selection.withReplacement
        else:
            targetSize = len(children)
            withReplacement = False
        selection = []
        bag = list(xrange(len(children)))
        shuffleList = []
        # Step 1: make sure we select required children at least once
        for i in xrange(len(children)):
            if children[i].required:
                selection.append(i)
                if not withReplacement:
                    bag.remove(i)
        if len(selection) > targetSize:
            raise core.SelectionError(
                "#%s contains a selection rule that selects fewer child elements than the number of required elements" %
                section.identifier)
        # Step 2: top up the selection until we reach the target size
        while len(selection) < targetSize:
            if bag:
                i = random.choice(bag)
                selection.append(i)
                if not withReplacement:
                    bag.remove(i)
            else:
                raise core.SelectionError(
                    "Number of children to select in #%s exceeds the number of child elements, use withReplacement to resolve" %
                    section.identifier)
        shuffleList = []
        # Step 3: sort the list to ensure the position of fixed children is
        # honoured
        selection.sort()
        # Step 4: transform to a list of identifiers...
        #			replace invisible sections with their contents if we need to split/shuffle them
        # replace floating children with empty slots and put them in the
        # shuffle list
        newSelection = []
        for i in selection:
            child = children[i]
            invisibleSection = isinstance(
                child, AssessmentSection) and not child.visible
            if shuffle and not child.fixed:
                # We're shuffling, add a free slot to the selection
                newSelection.append(None)
                if invisibleSection and not child.keepTogether:
                    # the grand-children go into the shuffleList independently
                    # What does a fixed grand-child mean in this situation?
                    # we raise an error at the moment.  Note that we don't expand
                    # the grand children (unless they are also mixed in from a nested
                    # invisible section)
                    for gChildID in self.Select(child, False):
                        gChild = self.test.GetPart(gChildID)
                        if gChild.fixed:
                            raise core.SelectionError(
                                "Fixed child of invisible section #%s is subject to parent shuffling, use keepTogether to resolve" %
                                child.identifier)
                        shuffleList.append(gChildID)
                else:
                    # invisible sections with keepTogether go in to the shuffle
                    # list just like items
                    shuffleList.append(child.identifier)
            else:
                # We're not shuffling or this child is fixed in position
                # (doesn't matter whether visible or not)
                newSelection.append(child.identifier)
                if isinstance(child, AssessmentSection) and expandChildren:
                    newSelection = newSelection + self.Select(child, True)
                    newSelection.append(u"-" + child.identifier)
        selection = newSelection
        if shuffleList:
            # Step 5: shuffle!
            random.shuffle(shuffleList)
            # Expanded invisible sections may mean we have more shuffled items than free slots
            # We need to partition the shuffle list into n buckets where n is the number of slots
            # We choose to put one item in each bucket initially then randomly assign the rest
            # This gives the expected result in the case where the shuffle list contains one
            # item for each slot.  It also preserves the relative order of fixed items and
            # ensures that adjacent fixed items are not split by a random choice.  Similarly,
            # items fixed at the start or end of the section remain in place
            i = 0
            buckets = []
            for child in selection:
                if child is None:
                    buckets.append([shuffleList[i]])
                    i += 1
            while i < len(shuffleList):
                # choose a random bucket
                random.choice(buckets).append(shuffleList[i])
                i += 1
            # Now splice the buckets into the selection
            for b in buckets:
                # We need to expand any sections that appear in the buckets
                newBucket = []
                for childID in b:
                    newBucket.append(childID)
                    child = self.test.GetPart(childID)
                    if isinstance(child, AssessmentSection):
                        newBucket.extend(self.Select(childID, True))
                        newBucket.append(u"-" + childID)
                i = selection.index(None)
                selection[i:i + 1] = newBucket
        return selection

    def find(self, pName):
        if pName in self.map:
            return self.map[pName]
        else:
            return []

    def index(self, pName):
        return self.components.index(pName)

    def __len__(self):
        return len(self.components)

    def __getitem__(self, index):
        return self.components[index]

    def __setitem__(self, index, value):
        raise TypeError("TestForms are read-only")

    def __delitem__(self, index):
        raise TypeError("TestForms are read-only")

    def __iter__(self):
        return iter(self.components)
