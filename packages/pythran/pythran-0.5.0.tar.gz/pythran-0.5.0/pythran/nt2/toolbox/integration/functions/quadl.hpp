/*******************************************************************************
 *         Copyright 2003-2012 LASMEA UMR 6602 CNRS/U.B.P
 *         Copyright 2011-2012 LRI    UMR 8623 CNRS/Univ Paris Sud XI
 *
 *          Distributed under the Boost Software License, Version 1.0.
 *                 See accompanying file LICENSE.txt or copy at
 *                     http://www.boost.org/LICENSE_1_0.txt
 ******************************************************************************/
#ifndef NT2_TOOLBOX_INTEGRATION_FUNCTIONS_QUADL_HPP_INCLUDED
#define NT2_TOOLBOX_INTEGRATION_FUNCTIONS_QUADL_HPP_INCLUDED

/*!
 * \file
 * \brief Defines and implements the nt2::quadl function
 */

#include <nt2/include/functor.hpp>
#include <nt2/sdk/option/options.hpp>
#include <nt2/toolbox/integration/options.hpp>
#include <nt2/include/functions/horzcat.hpp>

namespace nt2
{
  namespace tag
  {
    struct quadl_ : ext::unspecified_<quadl_>
    {
      typedef ext::unspecified_<quadl_> parent;
    };
  }

  //============================================================================
  /*!
   * Apply quadl algorithm to integrate a function over a real interval by lobatto quadrature
   *
   * \param func  Function to optimize
   * \param x    required points in the interval in ascending order
   *             (x can be replaced by 2 abscissae a and b)
   * \param opt   Options pack related to the tolerance handling
   *
   * \return  a tuple containing the results of the integration, the last error value,
   * the number of required function evaluation and a boolean
   * notifying success of the whole process.
   */
  //============================================================================
  template<class T,class F, class X> BOOST_FORCEINLINE
  typename boost::dispatch::meta
                ::call<tag::quadl_( F
                                  , X
                                  , details::integration_settings<T> const&
                                  )
                      >::type
  quadl(F f, X x)
  {
    typename boost::dispatch::make_functor<tag::quadl_, F>::type callee;
    return callee ( f
                  ,x
                  , details::integration_settings<T>()
                  );
  }

  template<class T,class F, class X, class Xpr>
  BOOST_FORCEINLINE
  typename boost::dispatch::meta
                ::call<tag::quadl_( F
                                  , X
                                  , details::integration_settings<T> const&
                                  )
                  >::type
  quadl(F f, X x, nt2::details::option_expr<Xpr> const& opt)
  {
    typename boost::dispatch::make_functor<tag::quadl_, F>::type callee;
    return callee ( f
                    , x
                    , details::integration_settings<Xpr>(opt)
      );
  }


  template<class T,class F, class A, class B> BOOST_FORCEINLINE
  typename boost::dispatch::meta
                ::call<tag::quadl_( F
                                   , typename boost::dispatch::meta
                                          ::call<tag::horzcat_(A, B)>::type
                                   , details::integration_settings<T> const&
    )
                  >::type
  quadl(F f, A a, B b)
  {
    typename boost::dispatch::make_functor<tag::quadl_, F>::type callee;
    return callee ( f
                    , nt2::cath(static_cast <T>(a),static_cast <T>(b)),
                    details::integration_settings<T>()
                  );
  }

  template<class T,class F, class A, class B, class Xpr>
  BOOST_FORCEINLINE
  typename boost::dispatch::meta
                ::call<tag::quadl_( F
                                   , typename boost::dispatch::meta
                                         ::call<tag::horzcat_(A, B)>::type
                                   , details::integration_settings<Xpr> const&
                         )
                      >::type
  quadl(F f, A a, B b, nt2::details::option_expr<Xpr> const& opt)
  {
    typename boost::dispatch::make_functor<tag::quadl_, F>::type callee;
    return callee ( f
                    , nt2::cath(static_cast<T>(a), static_cast<T>(b))
                    , details::integration_settings<Xpr>(opt)
                  );
  }
}

#endif

