#! /usr/bin/env python

import unittest

def suite():
	loader=unittest.TestLoader()
	loader.testMethodPrefix='test'
	return unittest.TestSuite((
		loader.loadTestsFromTestCase(CSDLTests)
		))

def load_tests(loader, tests, pattern):
	return suite()

from pyslet.odata2.csdl import *

import pyslet.xml20081126.structures as xml
import pyslet.odata2.edmx as edmx
from pyslet.vfs import OSFilePath as FilePath

import decimal

TEST_DATA_DIR=FilePath(FilePath(__file__).abspath().split()[0],'data_mc_csdl')


class CSDLTests(unittest.TestCase):
	def testCaseConstants(self):
		self.assertTrue(EDM_NAMESPACE=="http://schemas.microsoft.com/ado/2009/11/edm","Wrong CSDL namespace: %s"%EDM_NAMESPACE)

	def testCaseSimpleIdentifier(self):
		# basic tests here:
		for iTest in ("45",
			"M'",
			"M;",
			"M=",
			"M\\",
			"M.N",
			"M+","M-","M*","M/","M<","M>","M=","M~","M!","M@","M#","M%","M^","M&","M|","M`","M?",
			"M(","M)","M[","M]","M,","M;","M*","M."
			):
			try:
				self.assertFalse(ValidateSimpleIdentifier(iTest),"%s: Fail"%repr(iTest))
			except ValueError,e:
				pass
	
	def testCaseSimpleType(self):
		"""Test the SimpleType enumeration."""
		self.assertTrue(SimpleType.Binary==getattr(SimpleType,'Edm.Binary'),"Dual declaration form.")
		# Given a python type value (as returned by the type() function) we find the SimpleType
		self.assertTrue(SimpleType.PythonType[type(3.14)]==SimpleType.Double,"Bad float type") 
		self.assertTrue(SimpleType.PythonType[type(3)]==SimpleType.Int64,"Bad int type") 
		self.assertTrue(SimpleType.PythonType[type("Hello")]==SimpleType.String,"Bad string type") 			
		self.assertTrue(SimpleType.PythonType[type(u"Hello")]==SimpleType.String,"Bad unicode type") 
		# Given a python value we coerce to the correct type
# 		self.assertTrue(SimpleType.CoerceValue(SimpleType.Boolean,3.14) is True,"Boolean coercion True")
# 		self.assertTrue(SimpleType.CoerceValue(SimpleType.Boolean,0.0) is False,"Boolean coercion False")
# 		self.assertTrue(SimpleType.CoerceValue(SimpleType.Int32,3.14) is 3,"Int32 coercion")
# 		self.assertTrue(SimpleType.CoerceValue(SimpleType.Int32,"3") is 3,"Int32 coercion")
# 		self.assertTrue(SimpleType.CoerceValue(SimpleType.Double,"3.14")==3.14,"Double coercion")
		
	def testSimpleValue(self):
		"""Test the SimpleValue class."""
		p=Property(None)
		p.simpleTypeCode=SimpleType.Boolean
		v=SimpleValue.NewValue(p)
		self.assertTrue(isinstance(v,EDMValue),"SimpleValue inherits from EDMValue")
		self.assertTrue(v.value is None,"Null value on construction")
		p.name="flag"
		v=SimpleValue.NewValue(p)
		self.assertTrue(v.pDef.name=="flag","SimpleValue property definition set on constructor")
		self.assertTrue(v.value is None,"Null value on construction")
	
	def testSimpleValueCasts(self):
		p=Property(None)
		p.simpleTypeCode=SimpleType.Byte
		v=SimpleValue.NewValue(p)
		v.value=13
		cast=Property(None)
		cast.simpleTypeCode=SimpleType.Int16
		v2=v.Cast(EDMValue.NewValue(cast))
		self.assertTrue(isinstance(v2,SimpleValue),"Cast gives a SimpleValue")
		self.assertTrue(v2.typeCode==SimpleType.Int16,"Cast uses passed type")
		self.assertTrue(v2.value == 13,"Cast to Int16")
		cast=Property(None)
		cast.simpleTypeCode=SimpleType.Int32
		v2=v2.Cast(EDMValue.NewValue(cast))
		self.assertTrue(v2.typeCode==SimpleType.Int32,"Cast uses passed type")
		self.assertTrue(v2.value == 13,"Cast to Int32")
		cast=Property(None)
		cast.simpleTypeCode=SimpleType.Int64
		v2=v2.Cast(EDMValue.NewValue(cast))
		self.assertTrue(v2.typeCode==SimpleType.Int64,"Cast uses passed type")
		self.assertTrue(type(v2.value) is LongType,"Cast to Int64")
		self.assertTrue(v2.value == 13L,"Cast to Int64")
		cast=Property(None)
		cast.simpleTypeCode=SimpleType.Single
		v3=v2.Cast(EDMValue.NewValue(cast))
		self.assertTrue(v3.typeCode==SimpleType.Single,"Cast uses passed type")
		self.assertTrue(type(v3.value) is FloatType,"Cast to Single")
		cast=Property(None)
		cast.simpleTypeCode=SimpleType.Double
		v3=v3.Cast(EDMValue.NewValue(cast))
		self.assertTrue(v3.typeCode==SimpleType.Double,"Cast uses passed type")
		self.assertTrue(type(v3.value) is FloatType,"Cast to Double")
		self.assertTrue(v3.value==13.0,"Cast to Double")
		cast=Property(None)
		cast.simpleTypeCode=SimpleType.Decimal
		v3=v2.Cast(EDMValue.NewValue(cast))
		self.assertTrue(v3.typeCode==SimpleType.Decimal,"Cast uses passed type")
		self.assertTrue(isinstance(v3.value,decimal.Decimal),"Cast to Decimal")
		self.assertTrue(v3==13,"Cast to Double")
		
	def testCaseSchema(self):
		s=Schema(None)
		self.assertTrue(isinstance(s,xml.Element),"Schema not an XML element")
		self.assertTrue(s.ns==EDM_NAMESPACE,"CSDL namespace")
		self.assertTrue(s.name=='Default','Namespace default')
		self.assertTrue(s.alias==None,'Alias default')
		self.assertTrue(len(s.Using)==0,"No Using elements allowed on construction")
		self.assertTrue(len(s.Association)==0,"No Association elements allowed on construction")
		self.assertTrue(len(s.ComplexType)==0,"No ComplexType elements allowed on construction")
		self.assertTrue(len(s.EntityType)==0,"No EntityType elements allowed on construction")
		self.assertTrue(len(s.EntityContainer)==0,"No EntityContainer elements allowed on construction")
		self.assertTrue(len(s.Function)==0,"No Function elements allowed on construction")
		self.assertTrue(len(s.Annotations)==0,"No Annotations elements allowed on construction")
		self.assertTrue(len(s.ValueTerm)==0,"No ValueTerm elements allowed on construction")
		e=s.ChildElement(EntityType)
		e.name="TestType"
		s.ContentChanged()
		self.assertTrue(s['TestType'] is e,"Schema subscripting, EntityType declared")
		
	def testCaseEntityType(self):
		et=EntityType(None)
		self.assertTrue(isinstance(et,CSDLElement),"EntityType not a CSDLelement")
		self.assertTrue(et.name=="Default","Default name")
		et.SetAttribute('Name',"NewName")
		self.assertTrue(et.name=="NewName","Name attribute setter")
		self.assertTrue(et.baseType is None,"Default baseType")
		et.SetAttribute('BaseType',"ParentClass")
		self.assertTrue(et.baseType=="ParentClass","BaseType attribute setter")
		self.assertTrue(et.abstract is False,"Default abstract")
		et.SetAttribute('Abstract',"true")
		self.assertTrue(et.abstract is True,"Abstract attribute setter")
		self.assertTrue(et.Documentation is None,"No Documentation elements allowed on construction")
		self.assertTrue(et.Key is None,"No Key elements allowed on construction")
		self.assertTrue(len(et.Property)==0,"No Property elements allowed on construction")
		self.assertTrue(len(et.NavigationProperty)==0,"No Property elements allowed on construction")
		self.assertTrue(len(et.TypeAnnotation)==0,"No TypeAnnotation elements allowed on construction")
		self.assertTrue(len(et.ValueAnnotation)==0,"No ValueAnnotation elements allowed on construction")

	def testCaseProperty(self):
		p=Property(None)
		self.assertTrue(isinstance(p,CSDLElement),"Property not a CSDLelement")
		self.assertTrue(p.name=="Default","Default name")
		p.SetAttribute('Name',"NewName")
		self.assertTrue(p.name=="NewName","Name attribute setter")
		self.assertTrue(p.type=="Edm.String","Default type")
		p.SetAttribute('Type',"Edm.Int32")
		self.assertTrue(p.type=="Edm.Int32","Type attribute setter")
		self.assertTrue(p.TypeRef is None,"No TypeRef child on construction")
		self.assertTrue(p.nullable==True,"Default nullable value")
		p.SetAttribute('Nullable',"false")
		self.assertTrue(p.nullable is False,"Nullable attribute setter")
		self.assertTrue(p.defaultValue is None,"DefaultValue on construction")
		p.SetAttribute('DefaultValue',"5")
		self.assertTrue(p.defaultValue=="5","DefaultValue attribute setter")
		self.assertTrue(p.maxLength is None,"MaxLength on construction")
		p.SetAttribute('MaxLength',"5")
		self.assertTrue(p.maxLength==5,"MaxLength attribute setter")
		self.assertTrue(p.fixedLength is None,"FixedLength on construction")
		p.SetAttribute('FixedLength',"false")
		self.assertTrue(p.fixedLength is False,"FixedLength attribute setter")
		self.assertTrue(p.precision is None,"Precision on construction")
		self.assertTrue(p.scale is None,"Scale on construction")
		self.assertTrue(p.unicode is None,"Unicode on construction")
		self.assertTrue(p.collation is None,"Collation on construction")
		self.assertTrue(p.SRID is None,"SRID on construction")
		self.assertTrue(p.collectionKind is None,"CollectionKind on construction")
		self.assertTrue(p.concurrencyMode is None,"ConcurrencyMode on construction")
		self.assertTrue(p.Documentation is None,"No Documentation elements allowed on construction")
		self.assertTrue(len(p.TypeAnnotation)==0,"No TypeAnnotation elements allowed on construction")
		self.assertTrue(len(p.ValueAnnotation)==0,"No ValueAnnotation elements allowed on construction")

	def testCaseNavigationProperty(self):
		np=NavigationProperty(None)
		self.assertTrue(isinstance(np,CSDLElement),"NavigationProperty not a CSDLElement")
		self.assertTrue(np.name=="Default","Default name")
		self.assertTrue(np.relationship is None,"Default relationship")
		self.assertTrue(np.toRole is None,"Default ToRole")
		self.assertTrue(np.fromRole is None,"Default FromRole")
		self.assertTrue(np.Documentation is None,"No Documentation elements allowed on construction")
		self.assertTrue(len(np.TypeAnnotation)==0,"No TypeAnnotation elements allowed on construction")
		self.assertTrue(len(np.ValueAnnotation)==0,"No ValueAnnotation elements allowed on construction")
	
	def testCaseKey(self):
		k=Key(None)
		self.assertTrue(isinstance(k,CSDLElement),"Key not a CSDLElement")
		self.assertTrue(len(k.PropertyRef)==0,"No PropertyRef elements allowed on construction")
	
	def testCasePropertyRef(self):
		pr=PropertyRef(None)
		self.assertTrue(isinstance(pr,CSDLElement),"PropertyRef not a CSDLElement")
		self.assertTrue(pr.name=="Default","Default name")

	def testCaseComplexType(self):
		ct=ComplexType(None)
		self.assertTrue(isinstance(ct,CSDLElement),"ComplexType not a CSDLElement")
		self.assertTrue(ct.name=="Default","Default name")
		self.assertTrue(ct.baseType is None,"Default baseType")
		ct.SetAttribute('BaseType',"ParentClass")
		self.assertTrue(ct.baseType=="ParentClass","BaseType attribute setter")
		self.assertTrue(ct.abstract is False,"Default abstract")
		ct.SetAttribute('Abstract',"true")
		self.assertTrue(ct.abstract is True,"Abstract attribute setter")
		self.assertTrue(ct.Documentation is None,"No Documentation elements allowed on construction")
		self.assertTrue(len(ct.Property)==0,"No Property elements allowed on construction")
		self.assertTrue(len(ct.TypeAnnotation)==0,"No TypeAnnotation elements allowed on construction")
		self.assertTrue(len(ct.ValueAnnotation)==0,"No ValueAnnotation elements allowed on construction")

	def testCaseAssociation(self):
		a=Association(None)
		self.assertTrue(isinstance(a,CSDLElement),"Association not a CSDLElement")
		self.assertTrue(a.name=="Default","Default name")
		a.SetAttribute('Name',"NewName")
		self.assertTrue(a.name=="NewName","Name attribute setter: %s"%repr(a.name))
		self.assertTrue(a.Documentation is None,"No Documentation elements allowed on construction")
		self.assertTrue(len(a.AssociationEnd)==0,"No AssociationEnds allowed on construction")
		self.assertTrue(a.ReferentialConstraint is None,"No ReferentialConstraint elements allowed on construction")
		self.assertTrue(len(a.TypeAnnotation)==0,"No TypeAnnotation elements allowed on construction")
		self.assertTrue(len(a.ValueAnnotation)==0,"No ValueAnnotation elements allowed on construction")

	def testCaseEnd(self):
		e=AssociationEnd(None)
		self.assertTrue(isinstance(e,CSDLElement),"AssociationEnd not a CSDLElement")
		self.assertTrue(e.type is None,"Default type")
		e.SetAttribute('Type',"MySchema.Person")
		self.assertTrue(e.type=="MySchema.Person","Type attribute setter")
		self.assertTrue(e.name is None,"Default role")
		e.SetAttribute('Role',"Source")
		self.assertTrue(e.name=="Source","Role attribute setter")
		self.assertTrue(e.multiplicity==Multiplicity.One,"Default Multiplicity")
		e.SetAttribute('Multiplicity',"0..1")
		self.assertTrue(e.multiplicity==Multiplicity.ZeroToOne,"Multiplicity attribute setter")
		e.SetAttribute('Multiplicity',"*")
		self.assertTrue(e.multiplicity==Multiplicity.Many,"Multiplicity attribute setter")
		self.assertTrue(e.Documentation is None,"No Documentation elements allowed on construction")
		self.assertTrue(e.OnDelete is None,"No OnDelete elements allowed on construction")

	def testCaseEntity(self):
		minimalNavSchema="""<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<Schema Namespace="SampleModel" xmlns="http://schemas.microsoft.com/ado/2006/04/edm">
	<EntityContainer Name="SampleEntities" m:IsDefaultEntityContainer="true">
    	<EntitySet Name="Customers" EntityType="SampleModel.Customer"/>
        <EntitySet Name="Orders" EntityType="SampleModel.Order"/>
		<AssociationSet Name="Orders_Customers" Association="SampleModel.Orders_Customers">
			<End Role="Customer" EntitySet="Customers"/>
			<End Role="Order" EntitySet="Orders"/>
		</AssociationSet>
    </EntityContainer>
	<EntityType Name="Order">
		<Key>
			<PropertyRef Name="OrderID"/>
		</Key>
		<Property Name="OrderID" Type="Edm.Int32" Nullable="false"/>
	</EntityType>
	<EntityType Name="Customer">
		<Key>
			<PropertyRef Name="CustomerID"/>
		</Key>
		<Property Name="CustomerID" Type="Edm.String"/>
		<NavigationProperty Name="Orders" Relationship="SampleModel.Orders_Customers"
			FromRole="Customer" ToRole="Order"/>
	</EntityType>
	<Association Name="Orders_Customers">
		<End Role="Customer" Type="SampleModel.Customer" Multiplicity="0..1"/>
		<End Role="Order" Type="SampleModel.Order" Multiplicity="*"/>
	</Association>
</Schema>"""
		doc=Document()
		doc.Read(src=minimalNavSchema)
		scope=NameTableMixin()
		scope.Declare(doc.root)
		doc.root.UpdateTypeRefs(scope)
		doc.root.UpdateSetRefs(scope)
		es=doc.root["SampleEntities.Customers"]
		e=Entity(es)
		# initially the entity is marked as a new entity
		self.assertFalse(e.exists)
		self.assertTrue(isinstance(e['CustomerID'],StringValue),"Type of simple property")
		self.assertTrue(isinstance(e['Orders'],DeferredValue),"Type of navigation property")

				
if __name__ == "__main__":
	unittest.main()
