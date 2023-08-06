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

#include "/usr/include/python2.7/Python.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <inttypes.h>
#include <tgmath.h>

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
 *  You can compile and configure and run the assertions contains in file hobdcalc_assertions.c with:
 *  $ gcc hobdcalc_assertions.c -lm
 * 
 *********************************************************************************************************************************************************************************************************************/   


#include "hobdcalc/conversion/utils/conversion_utils.c"

#include "hobdcalc/conversion/int_bin/int_bin.c"
#include "hobdcalc/conversion/int_oct/int_oct.c"
#include "hobdcalc/conversion/int_hex/int_hex.c"

#include "hobdcalc/conversion/float_to_bin/float_bin.c"
#include "hobdcalc/conversion/float_to_oct/float_oct.c"
#include "hobdcalc/conversion/float_to_hex/float_hex.c"

#include "hobdcalc/operations/int_result/calc_bin_int_operations.c"
#include "hobdcalc/operations/int_result/calc_oct_int_operations.c"
#include "hobdcalc/operations/int_result/calc_hex_int_operations.c"

#include "hobdcalc/operations/float_result/calc_bin_float_operations.c"
#include "hobdcalc/operations/float_result/calc_oct_float_operations.c"
#include "hobdcalc/operations/float_result/calc_hex_float_operations.c"

/**
 * Following C functions sets are wrapper for python functions, to construct an python module, written in C.
 * 
 * -) Conversion functions.
 * -) Integer computing functions.
 * -) Floats computing functions.
 * 
 * ***********************************************************************************************************/

#include "pyhobdcalc/utils/string_utils.c"

#include "pyhobdcalc/conversion/bin_func.c"
#include "pyhobdcalc/conversion/oct_func.c"
#include "pyhobdcalc/conversion/hex_func.c"

#include "pyhobdcalc/operations/integer/bin_func.c"
#include "pyhobdcalc/operations/integer/oct_func.c"
#include "pyhobdcalc/operations/integer/hex_func.c"

#include "pyhobdcalc/operations/float/bin_func.c"
#include "pyhobdcalc/operations/float/oct_func.c"
#include "pyhobdcalc/operations/float/hex_func.c"




static PyMethodDef pyhobdcalcMethods[] = {
  
      /** This table register all the functions, written in C, for construct an python module function set.
       * 
       * Every item is following constructed:
       * 
       *  { "function_name", function_link, arguments_constant, 
       *    "Docstring from the function."}
       * 
       * **************************************************************************************************/
      
    
      /** Register octar conversion functions.           **/
      {"bintoint",  pyhobdcalc_bintoint, METH_VARARGS,
       "Take a binar integer string as argument and\nreturn the converted value as an integer string.\nThe binar string must be in form: [-][0b][01]\n(the \"0b\" identifier is optional).\nMaximal value:  9223372036854775807.\tMinimal value: -9223372036854775808."},
     
     {"binfloattofloat",  pyhobdcalc_binfloattofloat, METH_VARARGS,
      "Take a binar float string as argument and\nreturn the converted value as an float string.\nThe binar string must be in form: [-][0b][01][.][01]\n(the \"0b\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
     
     {"floattobinfloat",  pyhobdcalc_floattobinfloat, METH_VARARGS,
      "Take an float string as argument and\nreturn the converted value as an binar float string.\nThe integer part of the given argument must have an maximal length from 19 digits,\nand the input string support 64 characters."},
     
     
     /** Register binar integer computing functions.     **/
     {"binaddbin",  pyhobdcalc_binaddbin, METH_VARARGS,
      "Take 2 binar integer string as input return the summe as an integer string.\nThe binar strings must be in form: [-][0b][01]\n(the \"0b\" identifier is optional).\nAddition maximal result value: 9223372036854775807.\nAddition minimal result value: -9223372036854775808."},
     
     {"binsubbin",  pyhobdcalc_binsubbin, METH_VARARGS,
      "Take 2 binar integer string as input return the subtract as an integer string.\nThe binar strings must be in form: [-][0b][01]\n(the \"0b\" identifier is optional).\nSubstraction maximal result value: 9223372036854775807.\nSubstraction minimal result value: -9223372036854775808."},
     
     
     {"binmultbin",  pyhobdcalc_binmultbin, METH_VARARGS,
      "Take 2 binar integer string as input return the product as an integer string.\nThe binar strings must be in form: [-][0b][01]\n(the \"0b\" identifier is optional).\nMultiplication maximal result value: 9223372036854775807.\nMultiplication minimal result value: -9223372036854775808."},
     
     {"bindivbin",  pyhobdcalc_bindivbin, METH_VARARGS,
      "Take 2 binar integer string as input return the quotient as an float string.\nThe binar strings must be in form: [-][0b][01][.][01]\n(the \"0b\" identifier is optional).\nThe given binar strings arguments must have an maximal length from 64 characters.\nThe returned result is limited to the C type double: 15 digits precision."},
     
     
     /** Register binar float computing functions.       **/
     {"binfloataddbinfloat",  pyhobdcalc_binfloataddbinfloat, METH_VARARGS,
      "Take 2 binar float string as input return the summe as an float string.\nThe binar strings must be in form: [-][0b][01].[01]\n(the \"0b\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
     
     {"binfloatsubbinfloat",  pyhobdcalc_binfloatsubbinfloat, METH_VARARGS,
      "Take 2 binar float string as input return the subtract as an float string.\nThe binar strings must be in form: [-][0b][01].[01]\n(the \"0b\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
   
     {"binfloatmultbinfloat",  pyhobdcalc_binfloatmultbinfloat, METH_VARARGS,
      "Take 2 binar float string as input return the product as an float string.\nThe binar strings must be in form: [-][0b][01].[01]\n(the \"0b\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
     
     {"binfloatdivbinfloat",  pyhobdcalc_binfloatdivbinfloat, METH_VARARGS,
      "Take 2 binar float string as input return the quotient as an float string.\nThe binar strings must be in form: [-][0b][01].[01]\n(the \"0b\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
  
     /**---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------**/
     
     /** Register octal conversion functions.            **/
     {"octtoint",  pyhobdcalc_octtoint, METH_VARARGS,
      "Take a octal integer string as argument and\nreturn the converted value as an integer string.\nThe octal string must be in form: [-][0][0-7]\n(the \"0\" identifier is optional).\nMaximal value:  9223372036854775807.\tMinimal value: -9223372036854775808."},
     
     {"octfloattofloat",  pyhobdcalc_octfloattofloat, METH_VARARGS,
      "Take a octal float string as argument and\nreturn the converted value as an float string.\nThe octal string must be in form: [-][0][0-7][.][0-7]\n(the \"0\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
     
     {"floattooctfloat",  pyhobdcalc_floattooctfloat, METH_VARARGS,
      "Take an float string as argument and\nreturn the converted value as an octal float string.\nThe integer part of the given argument must have an maximal length from 19 digits,\nand the input string support 64 characters."},
     
     /** Register octal computing functions.             **/
     {"octaddoct",  pyhobdcalc_octaddoct, METH_VARARGS,
      "Take 2 octal integer string as input return the summe as an integer string.\nThe octal strings must be in form: [-][0][0-7]\n(the \"0\" identifier is optional).\nAddition maximal result value: 9223372036854775807.\nAddition minimal result value: -9223372036854775808."},
     
     {"octsuboct",  pyhobdcalc_octsuboct, METH_VARARGS,
      "Take 2 octal integer string as input return the subtract as an integer string.\nThe octal strings must be in form: [-][0][0-7]\n(the \"0\" identifier is optional).\nSubstraction maximal result value: 9223372036854775807.\nSubstraction minimal result value: -9223372036854775808."},
     
     {"octmultoct",  pyhobdcalc_octmultoct, METH_VARARGS,
      "Take 2 octal integer string as input return the product as an integer string.\nThe octal strings must be in form: [-][0][0-7]\n(the \"0\" identifier is optional).\nMultiplication maximal result value: 9223372036854775807.\nMultiplication minimal result value: -9223372036854775808."},
     
     {"octdivoct",  pyhobdcalc_octdivoct, METH_VARARGS,
      "Take 2 octal integer string as input return the quotient as an float string.\nThe octal strings must be in form: [-][0][0-7][.][0-7]\n(the \"0\" identifier is optional).\nThe arguments must have an maximal length from maximal 21 characters.\nThe result is limited to the C type double: 15 digits precision."},
     
     /** Register octal float computing functions.       **/
     {"octfloataddoctfloat",  pyhobdcalc_octfloataddoctfloat, METH_VARARGS,
      "Take 2 octal float string as input return the summe as an float string.\nThe octal strings must be in form: [-][0][0-7].[0-7]\n(the \"0\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
     
     {"octfloatsuboctfloat",  pyhobdcalc_octfloatsuboctfloat, METH_VARARGS,
      "Take 2 octal float string as input return the subtract as an float string.\nThe octal strings must be in form: [-][0][0-7].[0-7]\n(the \"0\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
   
     {"octfloatmultoctfloat",  pyhobdcalc_octfloatmultoctfloat, METH_VARARGS,
      "Take 2 octal float string as input return the product as an float string.\nThe octal strings must be in form: [-][0][0-7].[0-7]\n(the \"0\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
     
     {"octfloatdivoctfloat",  pyhobdcalc_octfloatdivoctfloat, METH_VARARGS,
      "Take 2 octal float string as input return the quotient as an float string.\nThe octal strings must be in form: [-][0][0-7].[0-7]\n(the \"0\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
 
     /**-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------**/
    
     /** Register hexdecimal conversion functions.       **/
     {"hextoint",  pyhobdcalc_hextoint, METH_VARARGS,
      "Take an hexdecimal integer string as argument and\nreturn the converted value as an integer string.\nThe hexdecimal string must be in form: [-][0x][0-9A-Fa-f]\n(the \"0x\" identifier is optional).\nMaximal value:  9223372036854775807.\tMinimal value: -9223372036854775808."},
     
     {"hexfloattofloat",  pyhobdcalc_hexfloattofloat, METH_VARARGS,
      "Take a hexdecimal float string as argument and\nreturn the converted value as an float string.\nThe hexadecimal string must be in form: [-][0x][0-9A-Fa-f][.][0-9A-Fa-f]\n(the \"0x\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision, for exactly results."},
     
     {"floattohexfloat",  pyhobdcalc_floattohexfloat, METH_VARARGS,
      "Take an float string as argument and\nreturn the converted value as an hexadecimal float string.\nThe integer part of the given argument must have an maximal length from 19 digits,\nand the input string support 64 characters."},
     
     /** Register hexadecimal computing functions.       **/
     {"hexaddhex",  pyhobdcalc_hexaddhex, METH_VARARGS,
      "Take 2 hexadecimal integer string as input return the summe as an integer string.\nThe hexadecimal strings must be in form: [-][0x][0-9A-Fa-f]\n(the \"0x\" identifier is optional).\nAddition maximal result value: 9223372036854775807.\nAddition minimal result value: -9223372036854775808."},
     
     {"hexsubhex",  pyhobdcalc_hexsubhex, METH_VARARGS,
      "Take 2 hexadecimal integer string as input return the subtract as an integer string.\nThe hexadecimal strings must be in form: [-][0x][0-9A-Fa-f]\n(the \"0x\" identifier is optional).\nSubstraction maximal result value: 9223372036854775807.\nSubstraction minimal result value: -9223372036854775808."},
     
     {"hexmulthex",  pyhobdcalc_hexmulthex, METH_VARARGS,
      "Take 2 hexadecimal integer string as input return the product as an integer string.\nThe hexadecimal strings must be in form: [-][0x][0-9A-Fa-f]\n(the \"0x\" identifier is optional).\nMultiplication maximal result value: 9223372036854775807.\nMultiplication minimal result value: -9223372036854775808."},
     
     {"hexdivhex",  pyhobdcalc_hexdivhex, METH_VARARGS,
      "Take 2 hexadecimal integer string as input return the quotient as an float string.\nThe hexadecimal strings must be in form: [-][0x][0-9A-Fa-f]\n(the \"0x\" identifier is optional).\nThe arguments must have an maximal length from maximal 16 characters.\nThe result is limited to the C type double: 15 digits precision."},
     
     /** Register hexdecimal float computing functions.  **/
     {"hexfloataddhexfloat",  pyhobdcalc_hexfloataddhexfloat, METH_VARARGS,
      "Take 2 hexdecimal float string as input return the summe as an float string.\nThe hexdecimal strings must be in form: [-][0x][0-9A-Fa-f][.][0-9A-Fa-f]\n(the \"0x\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
     
     {"hexfloatsubhexfloat",  pyhobdcalc_hexfloatsubhexfloat, METH_VARARGS,
      "Take 2 hexdecimal float string as input return the subtract as an float string.\nThe hexdecimal strings must be in form: [-][0x][0-9A-Fa-f][.][0-9A-Fa-f]\n(the \"0x\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
   
     {"hexfloatmulthexfloat",  pyhobdcalc_hexfloatmulthexfloat, METH_VARARGS,
      "Take 2 hexdecimal float string as input return the product as an float string.\nThe hexdecimal strings must be in form: [-][0x][0-9A-Fa-f][.][0-9A-Fa-f]\n(the \"0x\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
     
     {"hexfloatdivhexfloat",  pyhobdcalc_hexfloatdivhexfloat, METH_VARARGS,
      "Take 2 hexdecimal float string as input return the quotient as an float string.\nThe hexdecimal strings must be in form: [-][0x][0-9A-Fa-f][.][0-9A-Fa-f]\n(the \"0x\" identifier is optional).\nThe returned result is limited to the C type double: 15 digits precision."},
     
     /**-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------**/
   
     
     {NULL, NULL, 0, NULL}        /* Sentinel */
};





PyMODINIT_FUNC
initpyhobdcalc(void)
{  
    PyObject *m;

    m = Py_InitModule("pyhobdcalc", pyhobdcalcMethods);
    if (m == NULL) {
        return ;
    }
}
