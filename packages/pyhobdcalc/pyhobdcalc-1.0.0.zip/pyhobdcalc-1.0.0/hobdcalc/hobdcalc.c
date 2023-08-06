/**
 * pyhobdcalc: an multibase calculator python module written in C.
 * Copyright (C) 2014 Bruggemann Eddie.
 * 
 * This file is part of pyhobdcalc python module.
 * pyhobdcalc is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * pyhobdcalc is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with pyhobdcalc. If not, see <http://www.gnu.org/licenses/>
 * 
 ************************************************************************************/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <tgmath.h>
#include <ctype.h>
#include <limits.h>
#include <inttypes.h>
#include <stdbool.h>
#include <ctype.h>
#include <errno.h>
#include <sys/time.h>

#include "conversion/utils/conversion_utils.c"

#include "conversion/int_hex/int_hex.c"
#include "conversion/int_bin/int_bin.c"
#include "conversion/int_oct/int_oct.c" 


#include "conversion/float_to_bin/float_bin.c"
#include "conversion/float_to_oct/float_oct.c"
#include "conversion/float_to_hex/float_hex.c"

#include "operations/int_result/calc_hex_int_operations.c"
#include "operations/int_result/calc_oct_int_operations.c"
#include "operations/int_result/calc_bin_int_operations.c"

#include "operations/float_result/calc_hex_float_operations.c"
#include "operations/float_result/calc_oct_float_operations.c"
#include "operations/float_result/calc_bin_float_operations.c"


/** 
 *  hobdcalc for Hexdecimal Octal Binar Decimal Calculator
 * 
 *  Simply compil the file hobdcalc.c with type generic math linking, for function using in C codes.
 *  $ gcc hobdcalc.c -lm
 * 
 *  pyhobdcalc is based on the hobdcalc developpment function C functions collection:
 * 
 *  conversion/utils/conversion_utils.c contains bases converion utilities functions. 
 *  
 *  conversion/int_hex/int_hex.c   contains hexdecimal basis integer values conversion functions  
 *                                 (limited upto type long long (8 bytes) support signed values).
 *  conversion/int_bin/int_bin.c   contains binar basis integer values conversion functions.
 *                                 (limited upto type long long (8 bytes) support signed values).       
 *  conversion/int_oct/int_oct.c   contains octal basis integer values conversion functions.
 *                                 (limited upto type long long (8 bytes) support signed values).
 * 
 *  conversion/float_to_bin/float_bin.c contains binar basis floating-point conversion functions.
 *                                      (compute in type long double precision (19 digits after the '.' ) but is limited to the type double (15 digits precision after the '.') for exactly result).       
 *  conversion/float_to_oct/float_oct.c contains octal basis floating-point conversion functions.
 *                                      (compute in type long double precision (19 digits after the '.' ) but is limited to the type double (15 digits precision after the '.') for exactly result). 
 *  conversion/float_to_hex/float_hex.c contains hexdecimal basis floating-point conversion functions. 
 *                                      (compute in type long double precision (19 digits after the '.' ) but is limited to the type double (15 digits precision after the '.') for exactly result). 
 * 
 *  operations/int_result/calc_hex_int_operations.c contains integer hexadecimal operations (+,-,*,/) functions.
 *                                                  (limited upto type long long (8 bytes) support signed values). 
 *  operations/int_result/calc_oct_int_operations.c contains integer octal operations (+,-,*,/) functions.
 *                                                  (limited upto type long long (8 bytes) support signed values).
 *  operations/int_result/calc_bin_int_operations.c contains integer binar operations (+,-,*,/) functions
 *                                                  (limited upto type long long (8 bytes) support signed values).
 * 
 *  operations/float_result/calc_hex_float_operations.c contains floating-point hexadecimal operations (+,-,*,/) functions.
 *                                                      (compute in type long double precision (19 digits after the '.' ) but is limited to the type double (15 digits precision after the '.') for exactly result). 
 *  operations/float_result/calc_oct_float_operations.c contains floating-point octal operations (+,-,*,/) functions.
 *                                                      (compute in type long double precision (19 digits after the '.' ) but is limited to the type double (15 digits precision after the '.') for exactly result). 
 *  operations/float_result/calc_bin_float_operations.c contains floating-point binar operations (+,-,*,/) functions.
 *                                                      (compute in type long double precision (19 digits after the '.' ) but is limited to the type double (15 digits precision after the '.') for exactly result). 
 *  
 * You can use the functions from file: conversion/int_bin/int_bin.c
 * -) inttobin()
 * -) bintoint()
 * 
 * You can use the functions from file: conversion/int_oct/int_oct.c
 * -) inttooct()
 * -) octtoint()
 * 
 * You can use the functions from file: conversion/int_hex/int_hex.c
 * -) inttohex()
 * -) hextoint()
 * 
 * You can use the functions from file: conversion/float_to_bin/float_bin.c
 * -) binfloattofloat()
 * -) floattobinfloat()
 * 
 * You can use the functions from file: conversion/float_to_oct/float_oct.c
 * -) octfloattofloat()
 * -) floattooctfloat()
 *  
 * You can use the functions from file: conversion/float_to_hex/float_hex.c
 * -) hexfloattofloat()
 * -) floattohexfloat() 
 *  
 * You can use the functions from file: conversion/utils/conversion_utils.c
 * -) get_digit()
 * -) set_digit()
 * 
 * You can use the functions from file: operations/int_result/calc_bin_int_operations.c
 * -) binaddbin()
 * -) binsubbin()
 * -) binmultbin()
 * -) bindivbin()
 * 
 * You can use the functions from file: operations/int_result/calc_oct_int_operations.c
 * -) octaddoct()
 * -) octsuboct()
 * -) octmultoct()
 * -) octdivoct() 
 *
 * You can use the functions from file: operations/int_result/calc_hex_int_operations.c
 * -) hexaddhex()
 * -) hexsubhex()
 * -) hexmulthex()
 * -) hexdivhex() 
 * 
 * You can use the functions from file: operations/float_result/calc_bin_float_operations.c
 * -) binfloataddbinfloat()
 * -) binfloatsubbinfloat()
 * -) binfloatmultbinfloat()
 * -) binfloatdivbinfloat()
 * 
 * You can use the functions from file: operations/float_result/calc_oct_float_operations.c
 * -) octfloataddoctfloat()
 * -) octfloatsuboctfloat()
 * -) octfloatmultoctfloat()
 * -) octfloatdivoctfloat()
 * 
 * You can use the functions from file: operations/float_result/calc_hex_float_operations.c
 * -) hexfloataddhexfloat()
 * -) hexfloatsubhexfloat()
 * -) hexfloatmulthexfloat()
 * -) hexfloatdivhexfloat()
 * 
 *  You can compile and configure and run the assertions contains in file hobdcalc_assertions.c with:
 *  $ gcc hobdcalc_assertions.c -lm
 * 
 *********************************************************************************************************************************************************************************************************************/   

int main(int argc,char *argv[]) {
  return 0 ;
}
