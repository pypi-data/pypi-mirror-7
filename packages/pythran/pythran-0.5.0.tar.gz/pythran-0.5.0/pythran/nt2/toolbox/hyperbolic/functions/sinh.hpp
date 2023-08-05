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
#ifndef NT2_TOOLBOX_HYPERBOLIC_FUNCTIONS_SINH_HPP_INCLUDED
#define NT2_TOOLBOX_HYPERBOLIC_FUNCTIONS_SINH_HPP_INCLUDED
#include <nt2/include/simd.hpp>
#include <nt2/include/functor.hpp>

/*!
 * \ingroup hyperbolic
 * \defgroup hyperbolic_sinh sinh
 *
 * \par Description
 * hyperbolic sine: \f$\frac{e^{a_0}-e^{-a_0}}2\f$.
 *
 * \par Header file
 *
 * \code
 * #include <nt2/include/functions/sinh.hpp>
 * \endcode
 *
 *
 * \synopsis
 *
 * \code
 * namespace nt2
 * {
 *   template <class A0>
 *     meta::call<tag::sinh_(A0)>::type
 *     sinh(const A0 & a0);
 * }
 * \endcode
 *
 * \param a0 the unique parameter of sinh
 *
 * \return a value of the same type as the parameter
 *
 * \par Notes
 * In SIMD mode, this function acts elementwise on the inputs vectors elements
 * \par
 *
**/

namespace nt2 { namespace tag
  {
    /*!
     * \brief Define the tag sinh_ of functor sinh
     *        in namespace nt2::tag for toolbox hyperbolic
    **/
    struct sinh_ : ext::elementwise_<sinh_> { typedef ext::elementwise_<sinh_> parent; };
  }
  NT2_FUNCTION_IMPLEMENTATION(tag::sinh_, sinh, 1)
}

#endif

// modified by jt the 25/12/2010
