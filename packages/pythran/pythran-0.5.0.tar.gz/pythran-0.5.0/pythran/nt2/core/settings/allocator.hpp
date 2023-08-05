//==============================================================================
//         Copyright 2003 - 2011   LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011   LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef NT2_CORE_SETTINGS_ALLOCATOR_HPP_INCLUDED
#define NT2_CORE_SETTINGS_ALLOCATOR_HPP_INCLUDED

#include <nt2/core/settings/forward/allocator.hpp>
#include <boost/mpl/placeholders.hpp>
#include <nt2/core/settings/option.hpp>

namespace nt2
{
  namespace meta
  {
    //==========================================================================
    // Make options extracting the Allocator from allcoator_
    //==========================================================================
    template<class Allocator, class Default>
    struct option<allocator_<Allocator>, tag::allocator_, Default>
    {
      typedef allocator_<Allocator> type;
    };
  }
}

#endif
