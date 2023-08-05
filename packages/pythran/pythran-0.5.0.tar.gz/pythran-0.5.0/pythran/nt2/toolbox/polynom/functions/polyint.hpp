//////////////////////////////////////////////////////////////////////////////
///   Copyright 2003 and onward LASMEA UMR 6602 CNRS/U.B.P Clermont-Ferrand
///   Copyright 2009 and onward LRI    UMR 8623 CNRS/Univ Paris Sud XI
///
///          Distributed under the Boost Software License, Version 1.0
///                 See accompanying file LICENSE.txt or copy at
///                     http://www.boost.org/LICENSE_1_0.txt
//////////////////////////////////////////////////////////////////////////////
#ifndef NT2_TOOLBOX_POLYNOM_FUNCTIONS_POLYINT__HPP_INCLUDED
#define NT2_TOOLBOX_POLYNOM_FUNCTIONS_POLYINT__HPP_INCLUDED
#include <nt2/include/functor.hpp>

/**
 * @brief Perform polynomial integration
 *
 *   polyint(p, k) returns the primitive of the polynomial whose
 *   coefficients are the elements of vector p with integration constant k
 *   defaulting to 0.
 *
 **/
namespace nt2 { namespace tag
  {
    struct polyint_: ext::elementwise_<polyint_> { typedef ext::elementwise_<polyint_> parent; };
  }
  NT2_FUNCTION_IMPLEMENTATION(tag::polyint_,polyint, 1)
  NT2_FUNCTION_IMPLEMENTATION(tag::polyint_,polyint, 2)
}
#endif
