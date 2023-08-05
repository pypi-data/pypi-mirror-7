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
#ifndef NT2_TOOLBOX_BOOST_MATH_FUNCTIONS_SPHERICAL_HARMONIC_HPP_INCLUDED
#define NT2_TOOLBOX_BOOST_MATH_FUNCTIONS_SPHERICAL_HARMONIC_HPP_INCLUDED
#include <nt2/include/simd.hpp>
#include <nt2/include/functor.hpp>
#include <boost/math/special_functions/spherical_harmonic.hpp>

/*!
 * \ingroup boost_math
 * \defgroup boost_math_spherical_harmonic spherical_harmonic
 *
 * \par Description
 * Please for details consult the proper documentation of the external
 * library boost_math.
 *
 * \par Header file
 *
 * \code
 * #include <nt2/toolbox/boost_math/include/functions/spherical_harmonic.hpp>
 * \endcode
 *
 *
 * \synopsis
 *
 * \code
 * namespace nt2
 * {
 *   namespace boost_math
 *   {
 *     template <class A0>
 *       meta::call<tag::spherical_harmonic_(A0,A0,A0,A0)>::type
 *       spherical_harmonic(const A0 & a0,const A0 & a1,const A0 & a2,const A0 & a3);
 *   }
 * }
 * \endcode
 *
 * \param a0 the first parameter of spherical_harmonic
 * \param a1 the second parameter of spherical_harmonic
 * \param a2 the third parameter of spherical_harmonic
 * \param a3 the fourth parameter of spherical_harmonic
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
 *
**/

namespace nt2 { namespace boost_math { namespace tag
  {
    /*!
     * \brief Define the tag spherical_harmonic_ of functor spherical_harmonic
     *        in namespace nt2::boost_math::tag for toolbox boost_math
    **/
    struct spherical_harmonic_ : ext::elementwise_<spherical_harmonic_> { typedef ext::elementwise_<spherical_harmonic_> parent; };
  }
  NT2_FUNCTION_IMPLEMENTATION(boost_math::tag::spherical_harmonic_, spherical_harmonic, 4)
  } }

#include <nt2/toolbox/boost_math/functions/scalar/spherical_harmonic.hpp>
// #include <nt2/toolbox/boost_math/functions/simd/all/spherical_harmonic.hpp>

#endif

// modified by jt the 29/12/2010
