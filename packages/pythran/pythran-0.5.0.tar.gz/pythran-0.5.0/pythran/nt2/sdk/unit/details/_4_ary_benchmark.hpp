/*******************************************************************************
 *         Copyright 2003 & onward LASMEA UMR 6602 CNRS/Univ. Clermont II
 *         Copyright 2009 & onward LRI    UMR 8623 CNRS/Univ Paris Sud XI
 *
 *          Distributed under the Boost Software License, Version 1.0.
 *                 See accompanying file LICENSE.txt or copy at
 *                     http://www.boost.org/LICENSE_1_0.txt
 ******************************************************************************/
#ifndef NT2_SDK_UNIT_DETAILS_4_ARY_BENCHMARK_HPP_INCLUDED
#define NT2_SDK_UNIT_DETAILS_4_ARY_BENCHMARK_HPP_INCLUDED

#include <vector>
#include <iostream>
#include <algorithm>
#include <nt2/sdk/meta/type_id.hpp>
#include <nt2/sdk/timing/tic.hpp>
#include <nt2/sdk/timing/ctic.hpp>
#include <nt2/include/functions/load.hpp>
#include <nt2/include/functions/store.hpp>
#include <nt2/sdk/meta/scalar_of.hpp>
#include <boost/simd/sdk/meta/cardinal_of.hpp>
#include <boost/simd/sdk/memory/allocator.hpp>
#include <boost/type_traits/is_same.hpp>
#include <boost/mpl/if.hpp>
#include <nt2/sdk/meta/strip.hpp>

template<class T0,class T1, class T2, class T3
        ,class Dummy,class Func
        ,class MN0, class MX0
        ,class MN1, class MX1
        ,class MN2, class MX2
        ,class MN3, class MX3
        >
void timing_test( Func callee, size_t size
                , MN0 min0, MX0 max0
                , MN1 min1, MX1 max1
                , MN2 min2, MX2 max2
                , MN3 min3, MX3 max3
                , const char* name = NULL )
{
  typedef T0                                      r_in0;
  typedef T1                                      r_in1;
  typedef T2                                      r_in2;
  typedef T3                                      r_in3;
  typedef typename nt2::meta::scalar_of<T0>::type t_in0;
  typedef typename nt2::meta::scalar_of<T1>::type t_in1;
  typedef typename nt2::meta::scalar_of<T2>::type t_in2;
  typedef typename nt2::meta::scalar_of<T3>::type t_in3;

  // Input samples
  static std::vector<t_in0, boost::simd::memory::allocator<t_in0> >  in0(size);
  static std::vector<t_in1, boost::simd::memory::allocator<t_in1> >  in1(size);
  static std::vector<t_in2, boost::simd::memory::allocator<t_in2> >  in2(size);
  static std::vector<t_in3, boost::simd::memory::allocator<t_in3> >  in3(size);

  // Output samples
  typedef typename nt2::meta::result_of<Func(r_in0,r_in1,r_in2,r_in3)>::type  r_out;
  typedef typename nt2::meta::scalar_of<r_out>::type         scalar_out;
  typedef typename nt2::meta::strip<scalar_out>::type         strip_out;
  typedef typename boost::mpl::if_< typename boost::is_same< strip_out
                                                           , bool >::type
                                  , typename std::vector<nt2::uint8_t
                                                        , boost::simd::memory::allocator<nt2::uint8_t> >
                                  , typename std::vector<strip_out
                                                        , boost::simd::memory::allocator<strip_out> >
                                  >::type out_;
  static out_ out(size);

  // Filling samples randomly
  for(size_t i=0; i<size; ++i)
  {
    in0[i] = roll<t_in0>(min0,max0);
    in1[i] = roll<t_in1>(min1,max1);
    in2[i] = roll<t_in2>(min2,max2);
    in3[i] = roll<t_in3>(min3,max3);
  }

  std::cout << name << "("
                    << nt2::type_id<r_in0>().c_str()
            << ", " << nt2::type_id<r_in1>().c_str()
            << ", " << nt2::type_id<r_in2>().c_str()
            << ", " << nt2::type_id<r_in3>().c_str()
            << ") " << std::flush;

  std::vector<double> timings;
  double c(0.),t(0.);

  static const size_t c0 = boost::simd::meta::cardinal_of<r_in0>::value;
  static const size_t c1 = boost::simd::meta::cardinal_of<r_in1>::value;
  static const size_t c2 = boost::simd::meta::cardinal_of<r_in2>::value;
  static const size_t c3 = boost::simd::meta::cardinal_of<r_in3>::value;
  static const size_t nb1 = (c0 < c1) ? c1 : c0;
  static const size_t nb2 = (c2 < nb1) ? nb1 : c2;
  static const size_t nb = (c3 < nb2) ? nb2 : c3;

  do
  {
    nt2::tic();
    {
      nt2::ctic();
      for(size_t i=0; i<size; i+=nb)
      {
        nt2::store(
          callee( nt2::load<r_in0>(&in0[0],i)
                , nt2::load<r_in1>(&in1[0],i)
                , nt2::load<r_in2>(&in2[0],i)
                , nt2::load<r_in3>(&in3[0],i)
                )
        , &out[0], i
        );
      }
      c = nt2::ctoc(false) / double(size);
    }
    t += nt2::toc(false);
    timings.push_back(c);
  } while(t < NT2_TEST_DURATION);

  std::sort(timings.begin(),timings.end());
  std::cout << timings[timings.size()/2] << " cycles/value\n" << std::flush;
}

#endif
