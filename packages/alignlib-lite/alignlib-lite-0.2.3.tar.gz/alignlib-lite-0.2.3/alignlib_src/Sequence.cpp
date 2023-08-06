/*
  alignlib - a library for aligning protein sequences

  $Id: Sequence.cpp,v 1.2 2004/01/07 14:35:31 aheger Exp $

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
#include <iomanip>
#include "Sequence.h"

using namespace std;

namespace alignlib
{

//--------------------------------------------------------------------------------------
Sequence::Sequence() : Alignandum()
{
}

//--------------------------------------------------------------------------------------
Sequence::~Sequence ()
{
}

//--------------------------------------------------------------------------------------
Sequence::Sequence(const Sequence & src) : Alignandum(src)
{
}

//--------------------------------------------------------------------------------------
HSequence toSequence( HAlignandum & src )
{
    return boost::dynamic_pointer_cast<Sequence, Alignandum>(src);
}

//--------------------------------------------------------------------------------------
const HSequence toSequence( const HAlignandum & src )
{
    return boost::dynamic_pointer_cast<Sequence, Alignandum>(src);
}

//--------------------------------------------------------------------------------------
std::ostream & operator<<( std::ostream & output, const Sequence & src)
{
  src.write( output );
  return output;
}

} // namespace alignlib
