/*
  alignlib - a library for aligning protein sequences

  $Id: alignlib.h,v 1.5 2005/02/24 11:07:25 aheger Exp $

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

/** Interface makefile.
 *
 * Defines all the classes, types, interfaces and functions.
 */

#ifndef IMPLALIGNLIBBASE_H_
#define IMPLALIGNLIBBASE_H_

#if HAVE_CONFIG_H
#include <config.h>
#endif

#include "alignlib_fwd.h"
#include "AlignlibBase.h"

namespace alignlib
{

/** common interface definition for all classes in
 * alignlib
 */
class ImplAlignlibBase : public virtual AlignlibBase
{
public:
	/** constructor */
	ImplAlignlibBase();

	/** destructor */
	virtual ~ImplAlignlibBase();

	/** set the toolkit used by this object
	 *
	 * @param toolkit toolkit to use
	 */
	virtual void setToolkit( const HToolkit & toolkit);

	/** clone the toolkit used by this object such that it
	 * is private.
	 *
	 */
	virtual void cloneToolkit();

	/** set the toolkit used by this object
	 *
	 * @param toolkit toolkit to use
	 */
	virtual HToolkit getToolkit() const;

private:

	/** handle to toolkit */
	HToolkit mToolkit;

};

}

#endif /* ImplAlignlibBase_H_ */
