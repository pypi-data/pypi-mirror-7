//==============================================================================
//         Copyright 2003 - 2011   LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011   LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef BOOST_SIMD_TOOLBOX_BOOLEAN_FUNCTIONS_LOGICAL_ORNOT_HPP_INCLUDED
#define BOOST_SIMD_TOOLBOX_BOOLEAN_FUNCTIONS_LOGICAL_ORNOT_HPP_INCLUDED
/*!
 * \file
**/
#include <boost/simd/include/simd.hpp>
#include <boost/dispatch/include/functor.hpp>
#include <boost/proto/tags.hpp>

/*!
 * \ingroup boost_simd_operator
 * \defgroup boost_simd_operator_logical_ornot logical_ornot
 *
 * \par Description
 * return the logical or of the first parameter and of the negation the second parameter
 * the result type is logical type associated to the first parameter
 *
 * \par Header file
 *
 * \code
 * #include <nt2/include/functions/logical_ornot.hpp>
 * \endcode
 *
 * \par Alias
 * \arg l_ornot
 *
 * \synopsis
 *
 * \code
 * namespace boost::simd
 * {
 *   template <class A0>
 *     meta::call<tag::logical_ornot_(A0,A1)>::type
 *     logical_ornot(const A0 & a0,const A1 & a1);
 * }
 * \endcode
 *
 * \param a0 the first parameter of logical_ornot
 * \param a1 the second parameter of logical_ornot
 *
 * \return a value of the logical type associated to the first parameter
 *
 * \par Notes
 * In SIMD mode, this function acts elementwise on the inputs vectors elements
 * \par
 * This is a logical operation. Such operations return logical types.
 * You are invited to consult the rationale.
 *
**/

namespace boost { namespace simd
{
  namespace tag
  {
    /*!
     * \brief Define the tag logical_ornot_ of functor logical_ornot
     *        in namespace boost::simd::tag for toolbox boost.simd.operator
    **/
    struct logical_ornot_ : ext::elementwise_<logical_ornot_> { typedef ext::elementwise_<logical_ornot_> parent; };
  }

  BOOST_DISPATCH_FUNCTION_IMPLEMENTATION(tag::logical_ornot_      , logical_ornot     , 2 )
  BOOST_DISPATCH_FUNCTION_IMPLEMENTATION(tag::logical_ornot_      , l_ornot           , 2 )
} }

#include <boost/simd/toolbox/operator/specific/common.hpp>

#endif
