//==============================================================================
//         Copyright 2003 - 2012   LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2012   LRI    UMR 8623 CNRS/Univ Paris Sud XI
//         Copyright 2011 - 2012   MetaScale SAS
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef NT2_CORE_FUNCTIONS_IND2SUB_HPP_INCLUDED
#define NT2_CORE_FUNCTIONS_IND2SUB_HPP_INCLUDED

/*!
  @file
  @brief Define and implements the ind2sub function
**/

#include <nt2/include/functor.hpp>

namespace nt2
{
  namespace tag
  {
    /*!
      @brief Tag for the ind2sub functor
    **/
    struct ind2sub_ : boost::dispatch::tag::formal_
    {
      typedef boost::dispatch::tag::formal_ parent;
    };
  }

  //============================================================================
  /*!
   * Determines the subscript equivalent to a C linear index.
   *
   * \param size Size sequence of source container
   * \param pos  Linear index to convert
   * \param base Optional base index sequence for non canonic container
   * \return A C linear index pointing to the same element than \c pos.
   */
  //============================================================================
  NT2_FUNCTION_IMPLEMENTATION(nt2::tag::ind2sub_, ind2sub, 2)
  NT2_FUNCTION_IMPLEMENTATION(nt2::tag::ind2sub_, ind2sub, 3)
}

#endif
