//==============================================================================
//         Copyright 2003 - 2011   LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011   LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
/*!
 * \file
**/
#ifndef BOOST_SIMD_TOOLBOX_CONSTANT_CONSTANTS_MINEXPONENT_HPP_INCLUDED
#define BOOST_SIMD_TOOLBOX_CONSTANT_CONSTANTS_MINEXPONENT_HPP_INCLUDED

#include <boost/simd/include/simd.hpp>
#include <boost/simd/sdk/meta/int_c.hpp>
#include <boost/simd/sdk/constant/constant.hpp>

/*!
 * \ingroup boost_simd_constant
 * \defgroup boost_simd_constant_minexponent Minexponent
 *
 * \par Description
 * Constant Minexponent
 *
 * \par Header file
 *
 * \code
 * #include <nt2/include/functions/minexponent.hpp>
 * \endcode
 *
 *
 * \synopsis
 *
 * \code
 * namespace boost::simd
 * {
 *   template <class T,class A0>
 *     meta::call<tag::minexponent_(A0)>::type
 *     Minexponent();
 * }
 * \endcode
 *
 *
 * \param T template parameter of Minexponent
 *
 * \return type T value
 *
 *
**/

namespace boost { namespace simd
{
  namespace tag
  {
    /*!
     * \brief Define the tag Minexponent of functor Minexponent
     *        in namespace boost::simd::tag for toolbox boost.simd.constant
    **/
    struct Minexponent : ext::pure_constant_<Minexponent>
    {
      template<class Target, class Dummy=void>
      struct  apply : meta::int_c<typename Target::type,0> {};
    };

  template<class T, class Dummy>
  struct  Minexponent::apply<boost::dispatch::meta::single_<T>,Dummy>
        : meta::int_c<boost::simd::int32_t,-126> {};

  template<class T, class Dummy>
  struct  Minexponent::apply<boost::dispatch::meta::double_<T>,Dummy>
        : meta::int_c<boost::simd::int64_t,-1022> {};
  }

  BOOST_SIMD_CONSTANT_IMPLEMENTATION(boost::simd::tag::Minexponent, Minexponent)
} }

#include <boost/simd/sdk/constant/common.hpp>

#endif
