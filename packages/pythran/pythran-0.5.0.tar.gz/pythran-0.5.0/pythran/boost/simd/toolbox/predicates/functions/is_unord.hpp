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
#ifndef BOOST_SIMD_TOOLBOX_PREDICATES_FUNCTIONS_IS_UNORD_HPP_INCLUDED
#define BOOST_SIMD_TOOLBOX_PREDICATES_FUNCTIONS_IS_UNORD_HPP_INCLUDED
#include <boost/simd/include/simd.hpp>
#include <boost/dispatch/include/functor.hpp>

/*!
 * \ingroup boost_simd_predicates
 * \defgroup boost_simd_predicates_is_unord is_unord
 *
 * \par Description
 * Returns True<result_type>() if a0 or a1 is nan.
 *
 * \par Header file
 *
 * \code
 * #include <nt2/include/functions/is_unord.hpp>
 * \endcode
 *
 *
 * \synopsis
 *
 * \code
 * namespace boost::simd
 * {
 *   template <class A0>
 *     meta::call<tag::is_unord_(A0,A0)>::type
 *     is_unord(const A0 & a0,const A0 & a1);
 * }
 * \endcode
 *
 * \param a0 the first parameter of is_unord
 * \param a1 the second parameter of is_unord
 *
 * \return an integer value
 *
 * \par Notes
 * In SIMD mode, this function acts elementwise on the inputs vectors elements
 * \par
 * This is a predicate operation. Such operations return bool in scalar mode,
 * but not in SIMD mode.
 * \par
 * The return type in SIMD mode is the common type of the parameters and is
 * a 'signed boolean' type. This means that in this case True has all its bits
 * sets to one. This is to facilitate masking operations. You are invited to
 * consult the rationale.
 *
**/

namespace boost { namespace simd { namespace tag
  {
    /*!
     * \brief Define the tag is_unord_ of functor is_unord
     *        in namespace boost::simd::tag for toolbox boost.simd.predicates
    **/
    struct is_unord_ : ext::elementwise_<is_unord_> { typedef ext::elementwise_<is_unord_> parent; };
  }
  BOOST_DISPATCH_FUNCTION_IMPLEMENTATION(tag::is_unord_, is_unord, 2)
} }

#endif

// modified by jt the 25/12/2010
