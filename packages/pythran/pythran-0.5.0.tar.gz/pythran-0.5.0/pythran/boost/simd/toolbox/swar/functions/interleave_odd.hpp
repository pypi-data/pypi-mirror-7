//==============================================================================
//         Copyright 2003 - 2012   LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2012   LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
/*!
 * \file
**/
#ifndef BOOST_SIMD_TOOLBOX_SWAR_FUNCTIONS_INTERLEAVE_ODD_HPP_INCLUDED
#define BOOST_SIMD_TOOLBOX_SWAR_FUNCTIONS_INTERLEAVE_ODD_HPP_INCLUDED

#include <boost/simd/include/simd.hpp>
#include <boost/dispatch/include/functor.hpp>

/*!
 * \ingroup boost_simd_swar
 * \defgroup boost_simd_swar_interleave_odd interleave_odd
 *
 * \par Description
 * Compute
 *
 * \par Header file
 *
 * \code
 * #include <nt2/include/functions/interleave_odd.hpp>
 * \endcode
 *
 *
 * \synopsis
 *
 * \code
 * namespace boost::simd
 * {
 *   template<class A0,class A1> inline
 *   typename boost::dispatch::meta::call<tag::interleave_odd_(A0 const&,A1 const&)
 *                                       >::type
 *   interleave_odd(A0 const& a0,A1 const& a1);
 *
 *   template<class A0,class A1> inline
 *   A0 interleave_odd(A0 const& a0,A1 const& a1);
 * }
 * \endcode
 *
 * \param a0 the odd parameter of interleave_odd
 * \param a1 the second parameter of interleave_odd
 *
 * \return
 *
 * \par Notes
 * \par
 * This is a swar operation. As such it has not real interest outside
 * SIMD mode.
 * \par
 * Such an operation is a transform of an SIMD vector, that will return
 * vectors obtained on a non necessarily elementwise basis from the inputs
 * elements
 * \par
 * If usable and used in scalar mode, it reduces to the operation
 * on a one element vector.
 *
**/

namespace boost { namespace simd {
  namespace tag
  {
    /*!
     * \brief Define the tag interleave_odd_ of functor interleave_odd
     *        in namespace boost::simd::tag for toolbox boost.simd.swar
    **/
    struct interleave_odd_
    : ext::unspecified_<interleave_odd_>
    {
      typedef ext::unspecified_<interleave_odd_> parent;
    };
  }
  BOOST_DISPATCH_FUNCTION_IMPLEMENTATION(tag::interleave_odd_, interleave_odd, 2)

} }

#endif
