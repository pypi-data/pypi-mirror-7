/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignator.cpp,v 1.3 2005/02/24 11:07:25 aheger Exp $

  Copyright (C) 2004 Andreas Heger

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */


#include <iostream>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"

#include "MultipleAlignator.h"

using namespace std;

namespace alignlib
{

  //----------------------------------------------------------------------------------------
  MultipleAlignator::MultipleAlignator() : AlignlibBase()
    {
	  debug_func_cerr( 5 );
    }

  MultipleAlignator::~MultipleAlignator()

    {
      debug_func_cerr(5);

    }

  MultipleAlignator::MultipleAlignator( const MultipleAlignator & src ) : AlignlibBase(src)
  {
  }

} // namespace alignlib
