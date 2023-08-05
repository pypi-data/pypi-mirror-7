//////////////////////////////////////////////////////////////////////////////
///   Copyright 2003 and onward LASMEA UMR 6602 CNRS/U.B.P Clermont-Ferrand
///   Copyright 2009 and onward LRI    UMR 8623 CNRS/Univ Paris Sud XI
///
///          Distributed under the Boost Software License, Version 1.0
///                 See accompanying file LICENSE.txt or copy at
///                     http://www.boost.org/LICENSE_1_0.txt
//////////////////////////////////////////////////////////////////////////////
/*!
 * \file
**/
#ifndef NT2_TOOLBOX_LIBC_FUNCTIONS_ATAN2_HPP_INCLUDED
#define NT2_TOOLBOX_LIBC_FUNCTIONS_ATAN2_HPP_INCLUDED
#include <nt2/include/simd.hpp>
#include <nt2/include/functor.hpp>

/*!
 * \ingroup libc
 * \defgroup libc_atan2 atan2
 *
 * \par Description
 * Please for details consult the proper documentation of the external
 * library libc.
 *
 * \par Header file
 *
 * \code
 * #include <nt2/toolbox/libc/include/functions/atan2.hpp>
 * \endcode
 *
 *
 * \synopsis
 *
 * \code
 * namespace nt2
 * {
 *   namespace libc
 *   {
 *     template <class A0>
 *       meta::call<tag::atan2_(A0,A0)>::type
 *       atan2(const A0 & a0,const A0 & a1);
 *   }
 * }
 * \endcode
 *
 * \param a0 the first parameter of atan2
 * \param a1 the second parameter of atan2
 *
 * \return a value of the common type of the parameters
 *
 * \par Notes
 * In SIMD mode, this function acts elementwise on the inputs vectors elements
 * \par
 * When calling external library, nt2 simply encapsulates the
 * original proper call to provide easy use.
 * \par
 * Remenber that SIMD implementation is therefore merely
 * mapping the scalar function to each SIMD vectors elements
 * and will not provide acceleration, but ease.
 * \par
 * libc library defines functions for float and double entries.
 * \par
 * As they are written in C the original name of the float version is
 * generally terminated by and extra 'f',
 * this is not the case for the nt2 version which dispatch to
 * the correct function according to the inputs types.
 *
**/

namespace nt2 { namespace libc { namespace tag
  {
    /*!
     * \brief Define the tag atan2_ of functor atan2
     *        in namespace nt2::libc::tag for toolbox libc
    **/
    struct atan2_ : ext::elementwise_<atan2_> { typedef ext::elementwise_<atan2_> parent; };
  }
  NT2_FUNCTION_IMPLEMENTATION(libc::tag::atan2_, atan2, 2)
  } }

#include <nt2/toolbox/libc/functions/scalar/atan2.hpp>
// #include <nt2/toolbox/libc/functions/simd/all/atan2.hpp>

#endif

// modified by jt the 29/12/2010
