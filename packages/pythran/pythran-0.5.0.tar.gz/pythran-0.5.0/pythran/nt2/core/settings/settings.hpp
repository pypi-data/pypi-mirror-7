//==============================================================================
//         Copyright 2003 - 2011   LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011   LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef NT2_CORE_SETTINGS_SETTINGS_HPP_INCLUDED
#define NT2_CORE_SETTINGS_SETTINGS_HPP_INCLUDED

#include <boost/mpl/eval_if.hpp>
#include <nt2/core/settings/option.hpp>
#include <boost/type_traits/is_same.hpp>
#include <boost/preprocessor/repetition/enum.hpp>
#include <boost/preprocessor/repetition/enum_params.hpp>
#include <boost/preprocessor/repetition/repeat_from_to.hpp>

#include <nt2/core/settings/forward/settings.hpp>

namespace nt2 { namespace meta
{
  //============================================================================
  // empty settings list returns default for any option
  //============================================================================
  template<class Option, class Default>
  struct option<settings(),Option,Default> : option<Default,Option>
  {};

  //============================================================================
  // settings list of one argument return the argument option value
  //============================================================================
  template<class S0, class Option, class Default>
  struct  option< settings(S0), Option, Default >
        : option<S0,Option,Default>
  {};

  //============================================================================
  // Non-empty settings lists are recursively inspected
  //============================================================================
  #define M0(z,n,t)                                                           \
  template< BOOST_PP_ENUM_PARAMS(n,class S), class Option, class Default>     \
  struct option < settings(BOOST_PP_ENUM_PARAMS(n,S)), Option, Default >      \
  {                                                                           \
    typedef settings tail(BOOST_PP_ENUM_PARAMS(BOOST_PP_DEC(n),S));           \
    typedef option<BOOST_PP_CAT(S,BOOST_PP_DEC(n)), Option>         current;  \
    typedef option<tail, Option,Default>                            next;     \
    typedef boost::is_same< no_such_option, typename current::type> check;    \
    typedef typename boost::mpl::eval_if<check,next,current>::type type;      \
  };                                                                          \
  /**/

  BOOST_PP_REPEAT_FROM_TO(2,NT2_META_MAX_OPTIONS_NB,M0,~)

  #undef M0
} }

#endif
