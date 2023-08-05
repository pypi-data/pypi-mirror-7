/*******************************************************************************
 *         Copyright 2003 & onward LASMEA UMR 6602 CNRS/Univ. Clermont II
 *         Copyright 2009 & onward LRI    UMR 8623 CNRS/Univ Paris Sud XI
 *
 *          Distributed under the Boost Software License, Version 1.0.
 *                 See accompanying file LICENSE.txt or copy at
 *                     http://www.boost.org/LICENSE_1_0.txt
 ******************************************************************************/
#ifndef BOOST_SIMD_SDK_SIMD_IO_HPP_INCLUDED
#define BOOST_SIMD_SDK_SIMD_IO_HPP_INCLUDED

#include <boost/simd/sdk/simd/native.hpp>
#include <boost/fusion/sequence/io/out.hpp>
#include <complex>

namespace boost { namespace simd
{
  //////////////////////////////////////////////////////////////////////////////
  // Stream insertion for swar types
  //////////////////////////////////////////////////////////////////////////////
  template<class S,class E> inline std::ostream&
  operator<<( std::ostream& os, native<S,E> const & v )
  {
    return boost::fusion::operators::operator<<(os, v);
  }

} }

#endif
