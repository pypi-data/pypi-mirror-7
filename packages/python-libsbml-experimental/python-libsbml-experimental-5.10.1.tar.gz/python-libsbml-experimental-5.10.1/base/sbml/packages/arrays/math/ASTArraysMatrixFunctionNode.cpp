/**
 * @file    ASTArraysMatrixFunctionNode.cpp
 * @brief   Base Abstract Syntax Tree (AST) class.
 * @author  Sarah Keating
 * 
 * <!--------------------------------------------------------------------------
 * This file is part of libSBML.  Please visit http://sbml.org for more
 * information about SBML, and the latest version of libSBML.
 *
 * Copyright (C) 2009-2012 jointly by the following organizations: 
 *     1. California Institute of Technology, Pasadena, CA, USA
 *     2. EMBL European Bioinformatics Institute (EMBL-EBI), Hinxton, UK
 *  
 * Copyright (C) 2006-2008 by the California Institute of Technology,
 *     Pasadena, CA, USA 
 *  
 * Copyright (C) 2002-2005 jointly by the following organizations: 
 *     1. California Institute of Technology, Pasadena, CA, USA
 *     2. Japan Science and Technology Agency, Japan
 * 
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation.  A copy of the license agreement is provided
 * in the file named "LICENSE.txt" included with this software distribution and
 * also available online as http://sbml.org/software/libsbml/license.html
 * ------------------------------------------------------------------------ -->
 */

#include <sbml/packages/arrays/math/ASTArraysMatrixFunctionNode.h>
#include <sbml/packages/arrays/extension/ArraysASTPlugin.h>
#include <sbml/math/ASTNaryFunctionNode.h>
#include <sbml/math/ASTNumber.h>
#include <sbml/math/ASTFunction.h>


/** @cond doxygen-ignored */

using namespace std;

/** @endcond */

LIBSBML_CPP_NAMESPACE_BEGIN

ASTArraysMatrixFunctionNode::ASTArraysMatrixFunctionNode (int type) :
  ASTNaryFunctionNode(type)
{
}
  

  /**
   * Copy constructor
   */
ASTArraysMatrixFunctionNode::ASTArraysMatrixFunctionNode (const ASTArraysMatrixFunctionNode& orig):
  ASTNaryFunctionNode(orig)
{
}
  /**
   * Assignment operator for ASTNode.
   */
ASTArraysMatrixFunctionNode&
ASTArraysMatrixFunctionNode::operator=(const ASTArraysMatrixFunctionNode& rhs)
{
  if(&rhs!=this)
  {
    this->ASTNaryFunctionNode::operator =(rhs);
  }
  return *this;
}
  /**
   * Destroys this ASTNode, including any child nodes.
   */
ASTArraysMatrixFunctionNode::~ASTArraysMatrixFunctionNode ()
{
}

  /**
   * Creates a copy (clone).
   */
ASTArraysMatrixFunctionNode*
ASTArraysMatrixFunctionNode::deepCopy () const
{
  return new ASTArraysMatrixFunctionNode(*this);
}

void
ASTArraysMatrixFunctionNode::write(XMLOutputStream& stream) const
{
  if (&stream == NULL) return;

  stream.startElement("matrix");
  
  ASTBase::writeAttributes(stream);

 
  /* write children */

  for (unsigned int i = 0; i < ASTFunctionBase::getNumChildren(); i++)
  {
    ASTFunctionBase::getChild(i)->write(stream);
  }
    
  stream.endElement("matrix");

}

bool
ASTArraysMatrixFunctionNode::read(XMLInputStream& stream, const std::string& reqd_prefix)
{
  bool read = false;
  ASTBase * child = NULL;
  const XMLToken element = stream.peek ();

  ASTBase::checkPrefix(stream, reqd_prefix, element);

  const char*      name;

  unsigned int numChildrenAdded = 0;
  while (stream.isGood() && numChildrenAdded < getExpectedNumChildren())// && stream.peek().isEndFor(element) == false)
  {
    stream.skipText();

    name = stream.peek().getName().c_str();

    if (strcmp(name, "matrixrow") != 0)
    {
      std::string message = 
        "A <matrix> element must contain <matrixrow> child elements.";
      logError(stream, element, BadMathMLNodeType, message);   
      break;
    }
    else
    {
      child = new ASTFunction();
    }
    
    read = child->read(stream, reqd_prefix);

    stream.skipText();

    if (read == true && addChild(child) == LIBSBML_OPERATION_SUCCESS)
    {
      numChildrenAdded++;
    }
    else
    {
      read = false;
      break;
    }
  }

  if (getExpectedNumChildren() == 0 && numChildrenAdded == 0)
  {
    read = true;
  }

  return read;
}


int
ASTArraysMatrixFunctionNode::getTypeCode () const
{
  return AST_TYPECODE_MATRIX_CONSTRUCTOR;
}




LIBSBML_CPP_NAMESPACE_END