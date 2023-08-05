//==============================================================================
//         Copyright 2003 - 2011 LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011 LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef BOOST_SIMD_TOOLBOX_SWAR_FUNCTIONS_SIMD_SSE_SSE2_ENUMERATE_HPP_INCLUDED
#define BOOST_SIMD_TOOLBOX_SWAR_FUNCTIONS_SIMD_SSE_SSE2_ENUMERATE_HPP_INCLUDED
#ifdef BOOST_SIMD_HAS_SSE2_SUPPORT

#include <boost/simd/toolbox/swar/functions/enumerate.hpp>
#include <boost/simd/include/functions/simd/make.hpp>

namespace boost { namespace simd { namespace ext
{
  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::enumerate_
                                    , boost::simd::tag::sse2_
                                    , (A0)(T)
                                    , (scalar_< arithmetic_<A0> >)
                                      ((target_ < simd_ < type64_<T>
                                                        , boost::simd::tag::sse_
                                                        >
                                                >
                                      ))
                                    )
  {
    typedef typename T::type result_type;

    result_type operator()(A0 const& a0, T const& ) const
    {
      return make<result_type>(a0, a0+1);
    }
  };


  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::enumerate_
                                    , boost::simd::tag::sse2_
                                    , (A0)(T)
                                    , (scalar_< arithmetic_<A0> >)
                                      ((target_ < simd_ < type32_<T>
                                                        , boost::simd::tag::sse_
                                                        >
                                                >
                                      ))
                                    )
  {
    typedef typename T::type result_type;

    result_type operator()(A0 const& a0, T const& ) const
    {
      return make<result_type>(a0, a0+1, a0+2, a0+3);
    }
  };

  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::enumerate_
                                    , boost::simd::tag::sse2_
                                    , (A0)(T)
                                    , (scalar_< arithmetic_<A0> >)
                                      ((target_ < simd_ < type16_<T>
                                                        , boost::simd::tag::sse_
                                                        >
                                                >
                                      ))
                                    )
  {
    typedef typename T::type result_type;

    result_type operator()(A0 const& a0, T const& ) const
    {
      return make<result_type>(a0,a0+1,a0+2,a0+3,a0+4,a0+5,a0+6,a0+7);
    }
  };

  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::enumerate_
                                    , boost::simd::tag::sse2_
                                    , (A0)(T)
                                    , (scalar_< arithmetic_<A0> >)
                                      ((target_ < simd_ < type8_<T>
                                                        , boost::simd::tag::sse_
                                                        >
                                                >
                                      ))
                                    )
  {
    typedef typename T::type result_type;

    result_type operator()(A0 const& a0, T const& ) const
    {
      return make<result_type>( a0    , a0+1  , a0+2  , a0+3
                              , a0+4  , a0+5  , a0+6  , a0+7
                              , a0+8  , a0+9  , a0+10 , a0+11
                              , a0+12 , a0+13 , a0+14 , a0+15
                              );
    }
  };

  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::enumerate_
                                    , boost::simd::tag::sse2_
                                    , (A0)(A1)(T)
                                    , (scalar_< arithmetic_<A0> >)
                                      (scalar_< arithmetic_<A1> >)
                                      ((target_ < simd_ < double_<T>
                                                        , boost::simd::tag::sse_
                                                        >
                                                >
                                      ))
                                    )
  {
    typedef typename T::type result_type;

    result_type operator()(A0 const& a0, A1 const& a1, T const& ) const
    {
      return _mm_set_pd(a0+a1,a0);
    }
  };

  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::enumerate_
                                    , boost::simd::tag::sse2_
                                    , (A0)(A1)(T)
                                    , (scalar_< arithmetic_<A0> >)
                                      (scalar_< arithmetic_<A1> >)
                                      ((target_ < simd_ <  single_<T>
                                                        , boost::simd::tag::sse_
                                                        >
                                                >
                                      ))
                                    )
  {
    typedef typename T::type result_type;

    result_type operator()(A0 const& a0, A1 const& a1, T const& ) const
    {
      return _mm_set_ps(a0+3*a1,a0+2*a1,a0+a1,a0);
    }
  };

  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::enumerate_
                                    , boost::simd::tag::sse2_
                                    , (A0)(A1)(T)
                                    , (scalar_< arithmetic_<A0> >)
                                      (scalar_< arithmetic_<A1> >)
                                      ((target_ < simd_ < ints64_<T>
                                                        , boost::simd::tag::sse_
                                                        >
                                                >
                                      ))
                                    )
  {
    typedef typename T::type result_type;

    result_type operator()(A0 const& a0, A1 const& a1, T const& ) const
    {
      return make<result_type>(a0, a0+a1);
    }
  };

  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::enumerate_
                                    , boost::simd::tag::sse2_
                                    , (A0)(A1)(T)
                                    , (scalar_< arithmetic_<A0> >)
                                      (scalar_< arithmetic_<A1> >)
                                      ((target_ < simd_ < ints32_<T>
                                                        , boost::simd::tag::sse_
                                                        >
                                                >
                                      ))
                                    )
  {
    typedef typename T::type result_type;

    result_type operator()(A0 const& a0, A1 const& a1, T const& ) const
    {
      return _mm_set_epi32(a0+3*a1,a0+2*a1,a0+a1,a0);
    }
  };

  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::enumerate_
                                    , boost::simd::tag::sse2_
                                    , (A0)(A1)(T)
                                    , (scalar_< arithmetic_<A0> >)
                                      (scalar_< arithmetic_<A1> >)
                                      ((target_ < simd_ < ints16_<T>
                                                        , boost::simd::tag::sse_
                                                        >
                                                >
                                      ))
                                    )
  {
    typedef typename T::type result_type;

    result_type operator()(A0 const& a0, A1 const& a1, T const& ) const
    {
      return _mm_set_epi16(a0+7*a1,a0+6*a1,a0+5*a1,a0+4*a1,a0+3*a1,a0+2*a1,a0+a1,a0);
    }
  };

  BOOST_SIMD_FUNCTOR_IMPLEMENTATION ( boost::simd::tag::enumerate_
                                    , boost::simd::tag::sse2_
                                    , (A0)(A1)(T)
                                    , (scalar_< arithmetic_<A0> >)
                                      (scalar_< arithmetic_<A1> >)
                                      ((target_ < simd_ < ints8_<T>
                                                        , boost::simd::tag::sse_
                                                        >
                                                >
                                      ))
                                    )
  {
    typedef typename T::type result_type;

    result_type operator()(A0 const& a0, A1 const& a1, T const& ) const
    {
      return _mm_set_epi8( a0+15*a1,a0+14*a1,a0+13*a1,a0+12*a1,a0+11*a1,a0+10*a1
                                        , a0+9*a1, a0+8*a1, a0+7*a1, a0+6*a1, a0+5*a1, a0+4*a1
                                        , a0+3*a1, a0+2*a1, a0+a1,   a0
                                        );
    }
  };
} } }

#endif
#endif
