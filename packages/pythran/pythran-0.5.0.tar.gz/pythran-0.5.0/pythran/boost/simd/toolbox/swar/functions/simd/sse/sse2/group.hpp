//==============================================================================
//         Copyright 2003 - 2011 LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011 LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef BOOST_SIMD_TOOLBOX_SWAR_FUNCTIONS_SIMD_SSE_SSE2_GROUP_HPP_INCLUDED
#define BOOST_SIMD_TOOLBOX_SWAR_FUNCTIONS_SIMD_SSE_SSE2_GROUP_HPP_INCLUDED

#ifdef BOOST_SIMD_HAS_SSE2_SUPPORT
#include <boost/simd/toolbox/swar/functions/group.hpp>
#include <boost/simd/include/functions/simd/saturate.hpp>
#include <boost/simd/include/functions/simd/bitwise_and.hpp>
#include <boost/simd/include/functions/simd/bitwise_or.hpp>
#include <boost/simd/include/functions/simd/splat.hpp>
#include <boost/simd/sdk/meta/make_dependent.hpp>
#include <boost/dispatch/meta/downgrade.hpp>
#include <boost/dispatch/meta/as_integer.hpp>
#include <boost/simd/sdk/meta/scalar_of.hpp>
#include <boost/simd/toolbox/swar/functions/details/shuffle.hpp>

namespace boost { namespace simd { namespace ext
{
  //============================================================================
  // Implementation when type A0 is double
  //============================================================================
  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::group_
                                    , boost::simd::tag::sse2_
                                    , (A0)
                                    , ((simd_<double_<A0>,boost::simd::tag::sse_>))
                                      ((simd_<double_<A0>,boost::simd::tag::sse_>))
                                    )
  {
    typedef typename meta::make_dependent<float,A0>::type           sftype;
    typedef simd::native<sftype,boost::simd::tag::sse_>             result_type;
    typedef typename dispatch::meta::as_integer<result_type>::type  itype;

    BOOST_SIMD_FUNCTOR_CALL_REPEAT(2)
    {
      result_type
      r = simd::bitwise_cast<result_type>
          ( _mm_slli_si128( simd::bitwise_cast<itype >(_mm_cvtpd_ps(a1))
                          , 8
                          )
          );

      return b_or(r, simd::bitwise_cast<result_type>(_mm_cvtpd_ps(a0)));
    }
  };

  //============================================================================
  // Implementation when type A0 is int32_t
  //============================================================================
  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::group_
                                    , boost::simd::tag::sse2_
                                    , (A0)
                                    , ((simd_<int32_<A0>,boost::simd::tag::sse_>))
                                      ((simd_<int32_<A0>,boost::simd::tag::sse_>))
                                    )
  {
      typedef typename meta::scalar_of<A0>::type              stype;
      typedef typename dispatch::meta::downgrade<stype>::type utype;
      typedef simd::native<utype,boost::simd::tag::sse_>      result_type;

    BOOST_SIMD_FUNCTOR_CALL_REPEAT(2)
    {
      return simd::bitwise_cast<result_type>(_mm_packs_epi32(a0, a1));
    }
  };

  //============================================================================
  // Implementation when type A0 is int16_t
  //============================================================================
  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::group_
                                    , boost::simd::tag::sse2_
                                    , (A0)
                                    , ((simd_<int16_<A0>,boost::simd::tag::sse_>))
                                      ((simd_<int16_<A0>,boost::simd::tag::sse_>))
                                    )
  {
    typedef typename meta::scalar_of<A0>::type              stype;
    typedef typename dispatch::meta::downgrade<stype>::type utype;
    typedef simd::native<utype,boost::simd::tag::sse_>      result_type;

    BOOST_SIMD_FUNCTOR_CALL_REPEAT(2)
    {
      return simd::bitwise_cast<result_type>(_mm_packs_epi16(a0, a1));
    }
  };

  //============================================================================
  // Implementation when type A0 is uint32_t
  //============================================================================
  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::group_
                                    , boost::simd::tag::sse2_
                                    , (A0)
                                    , ((simd_<uint32_<A0>,boost::simd::tag::sse_>))
                                      ((simd_<uint32_<A0>,boost::simd::tag::sse_>))
                                    )
  {
    typedef typename meta::scalar_of<A0>::type              stype;
    typedef typename dispatch::meta::downgrade<stype>::type utype;
    typedef simd::native<utype,boost::simd::tag::sse_>      result_type;

    BOOST_SIMD_FUNCTOR_CALL_REPEAT(2)
    {
      A0 aa0 = boost::simd::saturate<result_type>(a0);
      A0 aa1 = boost::simd::saturate<result_type>(a1);
      result_type
      r = simd::bitwise_cast<result_type >
          (_mm_set_epi16(aa1[3], aa1[2], aa1[1], aa1[0], aa0[3], aa0[2], aa0[1], aa0[0]));
      return r;
    }
  };

  //============================================================================
  // Implementation when type A0 is uint16_t
  //============================================================================
  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::group_
                                    , boost::simd::tag::sse2_
                                    , (A0)
                                    , ((simd_<uint16_<A0>,boost::simd::tag::sse_>))
                                      ((simd_<uint16_<A0>,boost::simd::tag::sse_>))
                                    )
  {
    typedef typename meta::scalar_of<A0>::type              stype;
    typedef typename dispatch::meta::downgrade<stype>::type utype;
    typedef simd::native<utype,boost::simd::tag::sse_>      result_type;

    BOOST_SIMD_FUNCTOR_CALL_REPEAT(2)
    {
      A0 aa0 = boost::simd::saturate<result_type>(a0);
      A0 aa1 = boost::simd::saturate<result_type>(a1);
      return simd::bitwise_cast<result_type>(_mm_packus_epi16(aa0, aa1));
    }
  };

  //============================================================================
  // Implementation when type A0 is ints64_
  //============================================================================
  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::group_
                                    , boost::simd::tag::sse2_
                                    , (A0)
                                    , ((simd_<ints64_<A0>,boost::simd::tag::sse_>))
                                      ((simd_<ints64_<A0>,boost::simd::tag::sse_>))
                                    )
  {
    typedef typename dispatch::meta::downgrade<A0>::type result_type;

    BOOST_SIMD_FUNCTOR_CALL_REPEAT(2)
    {
      A0 mask = boost::simd::splat<A0>(Valmax<uint32_t>());
      A0 that0 =  b_and(boost::simd::saturate<result_type>(a0), mask);
      A0 that1 =  b_and(boost::simd::saturate<result_type>(a1), mask);
      result_type b = _mm_slli_si128(simd::bitwise_cast<result_type>(that1),4);
      b = b_or(b, that0);
      return simd::bitwise_cast<result_type>(details::shuffle<0,2,1,3>(b) );
    }
  };
} } }

#endif
#endif
