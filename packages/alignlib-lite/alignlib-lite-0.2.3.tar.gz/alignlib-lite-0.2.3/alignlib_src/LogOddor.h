/*
  alignlib - a library for aligning protein sequences

  $Id: LogOddor.h,v 1.2 2004/01/07 14:35:37 aheger Exp $

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


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef LOGODDOR_H
#define LOGODDOR_H 1

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

  /** @short Protocoll class for objects that convert residue frequencies into profile scores.
   *
   * Typically the scores are log-odds scores, hence the name.

      This class is a protocol class and as such defines only the general interface.

      @author Andreas Heger
      @version $Id: LogOddor.h,v 1.2 2004/01/07 14:35:37 aheger Exp $

  */

class LogOddor : public virtual AlignlibBase
{

 public:
    // constructors and desctructors

    /** default constructor */
    LogOddor ();

    /** copy constructor */
    LogOddor (const LogOddor &);

    /** destructor */
    virtual ~LogOddor ();

    DEFINE_ABSTRACT_CLONE( HLogOddor )

    /** insert scores into a profile @ref ScoreMatrix
     *
     * @param scores		@ref ScoreMatrix to be filled.
     * @param frequencies 	@ref @FrequencyMatrix to use for filling.
     * @param encoder 	@ref Encoder object.
     * */
    virtual void fillProfile(
    		ScoreMatrix & scores,
    		const FrequencyMatrix & frequencies,
    		const HEncoder & translator ) const = 0;

};


}

#endif /* LOGODDOR_H */

