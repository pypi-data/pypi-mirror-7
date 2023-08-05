/*******************************************************************************
 *         Copyright 2003-2012 LASMEA UMR 6602 CNRS/U.B.P
 *         Copyright 2009-2012 LRI    UMR 8623 CNRS/Univ Paris Sud XI
 *
 *          Distributed under the Boost Software License, Version 1.0.
 *                 See accompanying file LICENSE.txt or copy at
 *                     http://www.boost.org/LICENSE_1_0.txt
 ******************************************************************************/
#ifndef NT2_TOOLBOX_LINALG_FUNCTIONS_EXPM_HPP_INCLUDED
#define NT2_TOOLBOX_LINALG_FUNCTIONS_EXPM_HPP_INCLUDED
#include <nt2/include/functor.hpp>
#include <nt2/sdk/meta/size_as.hpp>
#include <nt2/sdk/meta/value_as.hpp>
#include <nt2/core/container/dsl/size.hpp>
#include <boost/simd/include/simd.hpp>
#include <boost/dispatch/include/functor.hpp>
#include <nt2/sdk/memory/container.hpp>
#include <nt2/sdk/meta/tieable_hierarchy.hpp>
#include <nt2/core/container/dsl/value_type.hpp>

namespace nt2 { namespace tag
  {
    /*!
     * \brief Define the tag expm_ of functor expm
     *        in namespace nt2::tag for toolbox algebra
    **/
    struct expm_ :   ext::tieable_<expm_>
    {
      typedef ext::tieable_<expm_>  parent;
    };
  }
  /**
   * @brief compute exponential of a matricial expression
   *
   * expm(a0) must not be confused with exp(a0) that computes on an
   * elementwise basis the powers of the elements of matrix a0.
   *
   * a0  can be a any square matricial expression
   *
   * @param  a0  Matrix expression or scalar
   *
   * @return a matrix containing e^a1
   **/


  BOOST_DISPATCH_FUNCTION_IMPLEMENTATION(tag::expm_, expm, 1)

}

namespace nt2 { namespace ext
{
  template<class Domain, int N, class Expr>
  struct  size_of<tag::expm_,Domain,N,Expr>
  {
    typedef typename boost::proto::result_of::child_c<Expr&,0>::value_type  c0_t;
    typedef typename c0_t::extent_type                               result_type;
    BOOST_FORCEINLINE result_type operator()(Expr& e) const
    {
      BOOST_ASSERT_MSG(issquare(boost::proto::child_c<0>(e)),
                       "expm needs a square matrix expression");

      return nt2::extent(boost::proto::child_c<0>(e));
    }
  };

  template<class Domain, int N, class Expr>
  struct  value_type<tag::expm_,Domain,N,Expr>
        : meta::value_as<Expr,0>
  {};
} }
#endif

