/*
 * @file    DiffusionCoefficient.h
 * @brief   Definition of DiffusionCoefficient, the SBase derived class of spatial package.
 * @author  
 *
 * $Id: DiffusionCoefficient.h 10673 2010-01-17 07:18:20Z ajouraku $
 * $HeadURL: https://sbml.svn.sourceforge.net/svnroot/sbml/branches/libsbml-5/src/packages/spatial/sbml/DiffusionCoefficient.h $
 *
 *<!---------------------------------------------------------------------------
 * This file is part of libSBML.  Please visit http://sbml.org for more
 * information about SBML, and the latest version of libSBML.
 *
 * Copyright 2009 California Institute of Technology.
 * 
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation.  A copy of the license agreement is provided
 * in the file named "LICENSE.txt" included with this software distribution
 * and also available online as http://sbml.org/software/libsbml/license.html
 *------------------------------------------------------------------------- -->
 */


#ifndef DiffusionCoefficient_H__
#define DiffusionCoefficient_H__

#include <sbml/common/extern.h>
#include <sbml/common/sbmlfwd.h>
#include <sbml/packages/spatial/common/spatialfwd.h>

#ifdef __cplusplus

#include <string>

#include <sbml/SBase.h>
#include <sbml/ListOf.h>
#include <sbml/packages/spatial/extension/SpatialExtension.h>

LIBSBML_CPP_NAMESPACE_BEGIN


class LIBSBML_EXTERN DiffusionCoefficient : public SBase
{
protected:

  std::string mVariable;
  unsigned int mCoordinateIndex;

  bool  mIsSetCoordinateIndex;

public:

  /**
   * Creates a new DiffusionCoefficient with the given level, version, and package version.
   */
   DiffusionCoefficient(unsigned int level      = SpatialExtension::getDefaultLevel(),
          unsigned int version    = SpatialExtension::getDefaultVersion(),
          unsigned int pkgVersion = SpatialExtension::getDefaultPackageVersion());


  /**
   * Creates a new DiffusionCoefficient with the given SpatialPkgNamespaces object.
   */
   DiffusionCoefficient(SpatialPkgNamespaces* spatialns);


  /**
   * Copy constructor.
   */
   DiffusionCoefficient(const DiffusionCoefficient& source);


  /**
   * Assignment operator.
   */
   DiffusionCoefficient& operator=(const DiffusionCoefficient& source);


  /**
   * Destructor.
   */ 
  virtual ~DiffusionCoefficient ();


  /**
   * Returns the string of the "variable" attribute of this DiffusionCoefficient.
   *
   * @return the string of the "variable" attribute of this DiffusionCoefficient.
   */
  virtual const std::string& getVariable () const;

  /**
   * Returns the int of the "coordinateIndex" attribute of this DiffusionCoefficient.
   *
   * @return the int of the "coordinateIndex" attribute of this DiffusionCoefficient.
   */
  unsigned int getCoordinateIndex () const;

  /**
   * Predicate returning @c true or @c false depending on whether this
   * DiffusionCoefficient's "variable" attribute has been set.
   *
   * @return @c true if this DiffusionCoefficient's "variable" attribute has been set, 
   * otherwise @c false is returned.
   */
  virtual bool isSetVariable () const;

 /**
   * Predicate returning @c true or @c false depending on whether this
   * DiffusionCoefficient's "coordinateIndex" attribute has been set.
   *
   * @return @c true if this DiffusionCoefficient's "coordinateIndex" attribute has been set, 
   * otherwise @c false is returned.
   */
  virtual bool isSetCoordinateIndex () const;
  
  /**
   * Sets the SIdRef string of the "variable" attribute of this DiffusionCoefficient.
   *
   * @param variable a SIdRef string to be set.
   *
   * @return integer value indicating success/failure of the
   * function.  @if clike The value is drawn from the
   * enumeration #OperationReturnValues_t. @endif The possible values
   * returned by this function are:
   * @li LIBSBML_OPERATION_SUCCESS
   * @li LIBSBML_INVALID_ATTRIBUTE_VALUE
   */
  virtual int setVariable (const std::string& variable);

  /**
   * Sets the SIdRef string of the "coordinateIndex" attribute of this DiffusionCoefficient.
   *
   * @param variable a SIdRef string to be set.
   *
   * @return integer value indicating success/failure of the
   * function.  @if clike The value is drawn from the
   * enumeration #OperationReturnValues_t. @endif The possible values
   * returned by this function are:
   * @li LIBSBML_OPERATION_SUCCESS
   * @li LIBSBML_INVALID_ATTRIBUTE_VALUE
   */
  virtual int setCoordinateIndex (unsigned int coordinateIndex);


  /**
   * Unsets the value of the "variable" attribute of this DiffusionCoefficient.
   *
   * @return integer value indicating success/failure of the
   * function.  @if clike The value is drawn from the
   * enumeration #OperationReturnValues_t. @endif The possible values
   * returned by this function are:
   * @li LIBSBML_OPERATION_SUCCESS
   * @li LIBSBML_OPERATION_FAILED
   */
  virtual int unsetVariable ();

  /**
   * Unsets the value of the "coordinateIndex" attribute of this DiffusionCoefficient.
   *
   * @return integer value indicating success/failure of the
   * function.  @if clike The value is drawn from the
   * enumeration #OperationReturnValues_t. @endif The possible values
   * returned by this function are:
   * @li LIBSBML_OPERATION_SUCCESS
   * @li LIBSBML_OPERATION_FAILED
   */
  virtual int unsetCoordinateIndex ();


  /**
   * Subclasses should override this method to return XML element name of
   * this SBML object.
   *
   * @return the string of the name of this element.
   */
  virtual const std::string& getElementName () const ;


  /**
   * @return a (deep) copy of this DiffusionCoefficient.
   */
  virtual DiffusionCoefficient* clone () const;


  /**
   * @return the typecode (int) of this SBML object or SBML_UNKNOWN
   * (default).
   *
   * @see getElementName()
   */
  int getTypeCode () const;


  /**
   * Accepts the given SBMLVisitor.
   *
   * @return the result of calling <code>v.visit()</code>, which indicates
   * whether or not the Visitor would like to visit the SBML object's next
   * sibling object (if available).
   */
  virtual bool accept (SBMLVisitor& v) const;
  /** @endcond doxygenLibsbmlInternal */
    
protected:
  /**
   * @return the SBML object corresponding to next XMLToken in the
   * XMLInputStream or NULL if the token was not recognized.
   */
  virtual SBase*
  createObject (XMLInputStream& stream);


  /**
   * Subclasses should override this method to get the list of
   * expected attributes.
   * This function is invoked from corresponding readAttributes()
   * function.
   */
  virtual void addExpectedAttributes(ExpectedAttributes& attributes);


  /**
   * Subclasses should override this method to read values from the given
   * XMLAttributes set into their specific fields.  Be sure to call your
   * parents implementation of this method as well.
   */
  virtual void readAttributes (const XMLAttributes& attributes, 
                               const ExpectedAttributes& expectedAttributes);


  /**
   * Subclasses should override this method to write their XML attributes
   * to the XMLOutputStream.  Be sure to call your parents implementation
   * of this method as well.  For example:
   *
   *   SBase::writeAttributes(stream);
   *   stream.writeAttribute( "id"  , mId   );
   *   stream.writeAttribute( "name", mName );
   *   ...
   */
  virtual void writeAttributes (XMLOutputStream& stream) const;


  /* the validator classes need to be friends to access the 
   * protected constructor that takes no arguments
   */
  friend class Validator;
  friend class ConsistencyValidator;
  friend class IdentifierConsistencyValidator;
  friend class InternalConsistencyValidator;
/*  
  friend class L1CompatibilityValidator;
  friend class L2v1CompatibilityValidator;
  friend class L2v2CompatibilityValidator;
  friend class L2v3CompatibilityValidator;
  friend class L2v4CompatibilityValidator;
  friend class MathMLConsistencyValidator;
  friend class SBOConsistencyValidator;
  friend class UnitConsistencyValidator;
*/
  friend class ModelingPracticeValidator;
  friend class OverdeterminedValidator;

 /** @endcond doxygenLibsbmlInternal */

};


LIBSBML_CPP_NAMESPACE_END

#endif /* __cplusplus */


#ifndef SWIG

LIBSBML_CPP_NAMESPACE_BEGIN
BEGIN_C_DECLS

//
// C API will be added here.
//

LIBSBML_EXTERN
DiffusionCoefficient_t *
DiffusionCoefficient_clone (const DiffusionCoefficient_t* c);


LIBSBML_EXTERN
const char *
DiffusionCoefficient_getVariable (const DiffusionCoefficient_t *c);


LIBSBML_EXTERN
unsigned int
DiffusionCoefficient_getCoordinateIndex (const DiffusionCoefficient_t *c);


LIBSBML_EXTERN
int
DiffusionCoefficient_isSetVariable (const DiffusionCoefficient_t *c);


LIBSBML_EXTERN
int
DiffusionCoefficient_isSetCoordinateIndex (const DiffusionCoefficient_t *c);


LIBSBML_EXTERN
int
DiffusionCoefficient_setVariable (DiffusionCoefficient_t *c, const char *sid);


LIBSBML_EXTERN
int
DiffusionCoefficient_setCoordinateIndex (DiffusionCoefficient_t *c, unsigned int coordinateIndex);


LIBSBML_EXTERN
int
DiffusionCoefficient_unsetVariable (DiffusionCoefficient_t *c);


LIBSBML_EXTERN
int
DiffusionCoefficient_unsetCoordinateIndex (DiffusionCoefficient_t *c);


END_C_DECLS
LIBSBML_CPP_NAMESPACE_END


#endif  /* !SWIG */
#endif  /* DiffusionCoefficient_H__ */
