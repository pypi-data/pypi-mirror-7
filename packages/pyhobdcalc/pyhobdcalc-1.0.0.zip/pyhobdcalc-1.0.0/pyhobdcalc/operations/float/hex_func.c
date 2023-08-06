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


/**
 * 
 * This file contains python wrapper functions for hexadecimal floats computing utilities:
 * 
 * -) octfloataddoctfloat: add two hexadecimal string with limitation of 8 bytes for the integer part,  
 *                         and 128 bits (16 bytes) for the entire hexadecimal string 
 *                         (without sign or hexadecimal identifier "0x"). 
 *                         This function return an string with maximum 15 digits precision 
 *                         corrresponding to the C type double but pyhobdcalc compute internally 
 *                         with the type long long double to give you an exact double value back. 
 * 
 * -) octfloatsuboctfloat: substract two hexadecimal string with limitation of 8 bytes for the integer part,  
 *                         and 128 bits (16 bytes) for the entire hexadecimal string 
 *                         (without sign or hexadecimal identifier "0x"). 
 *                         This function return an string with maximum 15 digits precision 
 *                         corrresponding to the C type double but pyhobdcalc compute internally 
 *                         with the type long long double to give you an exact value back. 
 * 
 * -) octfloatmultoctfloat: multiply two hexadecimal string with limitation of 8 bytes for the integer part,  
 *                          and 128 bits (16 bytes) for the entire hexadecimal string 
 *                          (without sign or hexadecimal identifier "0x"). 
 *                          This function return an string with maximum 15 digits precision 
 *                          corrresponding to the C type double but pyhobdcalc compute internally 
 *                          with the type long long double to give you an exact value back. 
 * 
 * -) octfloatdivoctfloat: divide two hexadecimal string with limitation of 8 bytes for the integer part,  
 *                         and 128 bits (16 bytes) for the entire hexadecimal string 
 *                         (without sign or hexadecimal identifier "0x"). 
 *                         This function return an string with maximum 15 digits precision 
 *                         corrresponding to the C type double but pyhobdcalc compute internally 
 *                         with the type long long double to give you an exact value back. 
 * 
 *****************************************************************************************************************/

static PyObject *
pyhobdcalc_hexfloataddhexfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for adding two hexadecimal floats string and return the result as an float string. **/
  
  char *hexaddstr1       ;            /** variable for converting an python string into an C string.       **/
  char *hexaddstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  int8_t change_argument_value1=0  ;  /** Variable to check if the hexadecimal identifier "0x" is present
                                        * in the first given argument string.                              **/ 
  int8_t change_argument_value2=0  ;  /** Variable to check if the hexadecimal identifier "0x" is present
                                        * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &hexaddstr1,&hexaddstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (hexaddstr1[0] == '-' && hexaddstr1[1] == '0' && hexaddstr1[2] == 'x') {
    /** The first argument hexadecimal string is negativ and start with the hexadecimal identifier prefix "0x". **/
    
    hexaddstr1[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    hexaddstr1 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_1_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value1=2 ; /** Hexadecimal identifier detected with negativ sign.            **/ 
  }
  else if (hexaddstr1[0] == '0' && hexaddstr1[1] == 'x') {
    /** The first argument hexadecimal string start with the hexadecimal identifier prefix "0x". **/
    
    hexaddstr1 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the hexadecimal identifier prefix "0x".            **/ 
                             
    change_argument_value1=1 ; /** Hexadecimal identifier detected without negativ sign.         **/                         
  }
  else if (hexaddstr1[0] == '-') {
    /** The first argument hexadecimal string is negativ. **/
    
    is_1_negativ=true    ;   /** We set the first argument negativ boolean value on true.  **/     
  }
  
  
  if (hexaddstr2[0] == '-' && hexaddstr2[1] == '0' && hexaddstr2[2] == 'x') {
    /** The second argument hexadecimal string is negativ and start with the hexadecimal identifier prefix "0x". **/
    
    hexaddstr2[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    hexaddstr2 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=2 ;  /** Hexadecimal identifier detected with negativ sign.           **/ 
    
  }
  else if (hexaddstr2[0] == '0' && hexaddstr2[1] == 'x') {
    /** The second argument hexadecimal string start with the hexadecimal identifier prefix "0x". **/
    
    hexaddstr2 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the hexadecimal identifier prefix "0x".            **/
                                  
    change_argument_value2=1 ;  /** Hexadecimal identifier detected without negativ sign.        **/                                                 
  }
  else if (hexaddstr2[0] == '-') {
    /** The second argument hexadecimal string is negativ. **/
    
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(hexaddstr1) > 17 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 1 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(hexaddstr1) > 18 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 1 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(hexaddstr2) > 17 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 2 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(hexaddstr2) > 18 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 2 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(hexaddstr1,16) ) {
    /** The given string is not an valid hexadecimal string.                                
      * So we raise an ValueError exception and abort the addition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an hexadecimal string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(hexaddstr2,16) ) {
    /** The given string is not an valid hexadecimal string.                                
      * So we raise an ValueError exception and abort the addition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an hexadecimal string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(hexaddstr1) ) {
    /** The given string is not an valid hexadecimal float string, 
     *  but an hexadecimal integer string.                                
     *  So we raise an ValueError exception and abort the addition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an hexadecimal float string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  }
  
  if (! is_string_float(hexaddstr2) ) {
    /** The given string is not an valid hexadecimal float string, 
     *  but an hexadecimal integer string.                                
     *  So we raise an ValueError exception and abort the addition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an hexadecimal float string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the float part of the string. **/
  
  if ((ptr_point=strchr(hexaddstr1,'.')) != NULL ) {
    
    if (hexaddstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pointer for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      hexaddstr1++ ;
      is_1_negativ=true  ;
    }
    
    if ((ptr_point-hexaddstr1) > 16) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      hexaddstr1-- ;
    }
    
  }
  
  
  if ((ptr_point=strchr(hexaddstr2,'.')) != NULL ) {
    
    if (hexaddstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      hexaddstr1++ ;
      is_2_negativ=true  ;
    }
    
    if ((ptr_point-hexaddstr2) > 16) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      hexaddstr1-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( hexfloattofloat(hexaddstr1) > hexfloattofloat(hexaddstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=false ;
    if ( fabsl(hexfloattofloat(hexaddstr2)) > fabsl(hexfloattofloat(hexaddstr1)) ) {
      is_result_negativ=true ;
    }
  }
  else if ( ( hexfloattofloat(hexaddstr1) < hexfloattofloat(hexaddstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  retval=hexfloataddhexfloat(hexaddstr1,hexaddstr2) ;  /** We perform the division and store the result in retval.  **/
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexaddstr1 -= 2 ;
    hexaddstr1[2]='x' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexaddstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexaddstr2 -= 2 ;
    hexaddstr2[2]='x' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexaddstr2 -= 2 ;
  }  
  
  
  char string_to_return[128]              ;  /** We need an string to return it            **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.                 **/
   
  sprintf(string_to_return,"%.15Lf",retval) ;  /** Copy the result value into an string.   **/  
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.                      **/ 
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The addition result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the addition function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments summe value to great for addition.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The addition result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the addition function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments summe value to great for addition.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long double to python.       **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}


static PyObject *
pyhobdcalc_hexfloatsubhexfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for substracting two hexadecimal floats string and return the result as an float string. **/
  
  char *hexsubstr1       ;            /** variable for converting an python string into an C string.       **/
  char *hexsubstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  int8_t change_argument_value1=0  ;  /** Variable to check if the hexadecimal identifier "0x" is present
                                        * in the first given argument string.                              **/ 
  int8_t change_argument_value2=0  ;  /** Variable to check if the hexadecimal identifier "0x" is present
                                        * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &hexsubstr1,&hexsubstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (hexsubstr1[0] == '-' && hexsubstr1[1] == '0' && hexsubstr1[2] == 'x') {
    /** The first argument hexadecimal string is negativ and start with the hexadecimal identifier prefix "0x". **/
    
    hexsubstr1[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    hexsubstr1 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_1_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value1=2 ; /** Hexadecimal identifier detected with negativ sign.            **/ 
  }
  else if (hexsubstr1[0] == '0' && hexsubstr1[1] == 'x') {
    /** The first argument hexadecimal string start with the hexadecimal identifier prefix "0x". **/
    
    hexsubstr1 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the hexadecimal identifier prefix "0x".            **/ 
                             
    change_argument_value1=1 ; /** Hexadecimal identifier detected without negativ sign.         **/                         
  }
  else if (hexsubstr1[0] == '-') {
    /** The first argument hexadecimal string is negativ. **/
    
    is_1_negativ=true    ;   /** We set the first argument negativ boolean value on true.  **/     
  }
  
  
  if (hexsubstr2[0] == '-' && hexsubstr2[1] == '0' && hexsubstr2[2] == 'x') {
    /** The second argument hexadecimal string is negativ and start with the hexadecimal identifier prefix "0x". **/
    
    hexsubstr2[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    hexsubstr2 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=2 ;  /** Hexadecimal identifier detected with negativ sign.           **/ 
    
  }
  else if (hexsubstr2[0] == '0' && hexsubstr2[1] == 'x') {
    /** The second argument hexadecimal string start with the hexadecimal identifier prefix "0x". **/
    
    hexsubstr2 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the hexadecimal identifier prefix "0x".            **/
                                  
    change_argument_value2=1 ;  /** Hexadecimal identifier detected without negativ sign.        **/                                                 
  }
  else if (hexsubstr2[0] == '-') {
    /** The second argument hexadecimal string is negativ. **/
    
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(hexsubstr1) > 17 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 1 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(hexsubstr1) > 18 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 1 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(hexsubstr2) > 17 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 2 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(hexsubstr2) > 18 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 2 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(hexsubstr1,16) ) {
    /** The given string is not an valid hexadecimal string.                                
      * So we raise an ValueError exception and abort the substraction function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an hexadecimal string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(hexsubstr2,16) ) {
    /** The given string is not an valid hexadecimal string.                                
      * So we raise an ValueError exception and abort the substraction function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an hexadecimal string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(hexsubstr1) ) {
    /** The given string is not an valid hexadecimal float string, 
     *  but an hexadecimal integer string.                                
     *  So we raise an ValueError exception and abort the substraction function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an hexadecimal float string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  }
  
  if (! is_string_float(hexsubstr2) ) {
    /** The given string is not an valid hexadecimal float string, 
     *  but an hexadecimal integer string.                                
     *  So we raise an ValueError exception and abort the substraction function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an hexadecimal float string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the float part of the string. **/
  
  if ((ptr_point=strchr(hexsubstr1,'.')) != NULL ) {
    
    if (hexsubstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pointer for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      hexsubstr1++ ;
      is_1_negativ=true  ;
    }
    
    if ((ptr_point-hexsubstr1) > 16) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      hexsubstr1-- ;
    }
    
  }
  
  
  if ((ptr_point=strchr(hexsubstr2,'.')) != NULL ) {
    
    if (hexsubstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      hexsubstr1++ ;
      is_2_negativ=true  ;
    }
    
    if ((ptr_point-hexsubstr2) > 16) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      hexsubstr1-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( hexfloattofloat(hexsubstr1) > hexfloattofloat(hexsubstr2) ) && (! is_1_negativ) &&  is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( ( hexfloattofloat(hexsubstr1) > hexfloattofloat(hexsubstr2) ) && is_1_negativ &&  is_2_negativ  ) {
    is_result_negativ=true ;
  }
  else if ( ( hexfloattofloat(hexsubstr1) > hexfloattofloat(hexsubstr2) ) && (! is_1_negativ) &&  (! is_2_negativ)  ) {
    is_result_negativ=false ;
  }
  else if ( ( hexfloattofloat(hexsubstr1) < hexfloattofloat(hexsubstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( hexfloattofloat(hexsubstr1) < hexfloattofloat(hexsubstr2) ) && is_1_negativ &&  is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( ( hexfloattofloat(hexsubstr1) < hexfloattofloat(hexsubstr2) ) && (! is_1_negativ) &&  (! is_2_negativ)  ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  retval=hexfloatsubhexfloat(hexsubstr1,hexsubstr2) ;  /** We perform the division and store the result in retval.  **/
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexsubstr1 -= 2 ;
    hexsubstr1[2]='x' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexsubstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexsubstr2 -= 2 ;
    hexsubstr2[2]='x' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexsubstr2 -= 2 ;
  }  
  
  
  char string_to_return[128]              ;  /** We need an string to return it            **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.                 **/
   
  sprintf(string_to_return,"%.15Lf",retval) ;  /** Copy the result value into an string.   **/  
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.                      **/ 
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The substraction result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the substraction function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments substract value to great for substraction.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The substraction result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the substraction function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments substract value to great for substraction.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long double to python.       **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}



static PyObject *
pyhobdcalc_hexfloatmulthexfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for multiplying two hexadecimal floats string and return the result as an float string. **/
  
  char *hexmultstr1       ;            /** variable for converting an python string into an C string.       **/
  char *hexmultstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  int8_t change_argument_value1=0  ;  /** Variable to check if the hexadecimal identifier "0x" is present
                                        * in the first given argument string.                              **/ 
  int8_t change_argument_value2=0  ;  /** Variable to check if the hexadecimal identifier "0x" is present
                                        * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &hexmultstr1,&hexmultstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (hexmultstr1[0] == '-' && hexmultstr1[1] == '0' && hexmultstr1[2] == 'x') {
    /** The first argument hexadecimal string is negativ and start with the hexadecimal identifier prefix "0x". **/
    
    hexmultstr1[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    hexmultstr1 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_1_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value1=2 ; /** Hexadecimal identifier detected with negativ sign.            **/ 
  }
  else if (hexmultstr1[0] == '0' && hexmultstr1[1] == 'x') {
    /** The first argument hexadecimal string start with the hexadecimal identifier prefix "0x". **/
    
    hexmultstr1 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the hexadecimal identifier prefix "0x".            **/ 
                             
    change_argument_value1=1 ; /** Hexadecimal identifier detected without negativ sign.         **/                         
  }
  else if (hexmultstr1[0] == '-') {
    /** The first argument hexadecimal string is negativ. **/
    
    is_1_negativ=true    ;   /** We set the first argument negativ boolean value on true.  **/     
  }
  
  
  if (hexmultstr2[0] == '-' && hexmultstr2[1] == '0' && hexmultstr2[2] == 'x') {
    /** The second argument hexadecimal string is negativ and start with the hexadecimal identifier prefix "0x". **/
    
    hexmultstr2[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    hexmultstr2 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=2 ;  /** Hexadecimal identifier detected with negativ sign.           **/ 
    
  }
  else if (hexmultstr2[0] == '0' && hexmultstr2[1] == 'x') {
    /** The second argument hexadecimal string start with the hexadecimal identifier prefix "0x". **/
    
    hexmultstr2 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the hexadecimal identifier prefix "0x".            **/
                                  
    change_argument_value2=1 ;  /** Hexadecimal identifier detected without negativ sign.        **/                                                 
  }
  else if (hexmultstr2[0] == '-') {
    /** The second argument hexadecimal string is negativ. **/
    
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(hexmultstr1) > 17 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 1 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(hexmultstr1) > 18 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multiplication function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 1 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(hexmultstr2) > 17 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 2 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(hexmultstr2) > 18 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multiplication function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 2 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(hexmultstr1,16) ) {
    /** The given string is not an valid hexadecimal string.                                
      * So we raise an ValueError exception and abort the multiplication function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an hexadecimal string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(hexmultstr2,16) ) {
    /** The given string is not an valid hexadecimal string.                                
      * So we raise an ValueError exception and abort the multiplication function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an hexadecimal string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(hexmultstr1) ) {
    /** The given string is not an valid hexadecimal float string, 
     *  but an hexadecimal integer string.                                
     *  So we raise an ValueError exception and abort the multiplication function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an hexadecimal float string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  }
  
  if (! is_string_float(hexmultstr2) ) {
    /** The given string is not an valid hexadecimal float string, 
     *  but an hexadecimal integer string.                                
     *  So we raise an ValueError exception and abort the multiplication function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an hexadecimal float string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the float part of the string. **/
  
  if ((ptr_point=strchr(hexmultstr1,'.')) != NULL ) {
    
    if (hexmultstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pointer for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      hexmultstr1++ ;
      is_1_negativ=true  ;
    }
    
    if ((ptr_point-hexmultstr1) > 16) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      hexmultstr1-- ;
    }
    
  }
  
  
  if ((ptr_point=strchr(hexmultstr2,'.')) != NULL ) {
    
    if (hexmultstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      hexmultstr1++ ;
      is_2_negativ=true  ;
    }
    
    if ((ptr_point-hexmultstr2) > 16) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      hexmultstr1-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( hexfloattofloat(hexmultstr1) > hexfloattofloat(hexmultstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( hexfloattofloat(hexmultstr1) < hexfloattofloat(hexmultstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  retval=hexfloatmulthexfloat(hexmultstr1,hexmultstr2) ;  /** We perform the division and store the result in retval.  **/
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexmultstr1 -= 2 ;
    hexmultstr1[2]='x' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexmultstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexmultstr2 -= 2 ;
    hexmultstr2[2]='x' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexmultstr2 -= 2 ;
  }  
  
  
  char string_to_return[128]              ;  /** We need an string to return it            **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.                 **/
   
  sprintf(string_to_return,"%.15Lf",retval) ;  /** Copy the result value into an string.   **/  
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.                      **/ 
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The multiplication result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the multiplication function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments product value to great for multiplication.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The multiplication result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the multiplication function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments product value to great for multiplication.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long double to python.       **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}




static PyObject *
pyhobdcalc_hexfloatdivhexfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for dividing two hexadecimal floats string and return the result as an float string. **/
  
  char *hexdivstr1       ;            /** variable for converting an python string into an C string.       **/
  char *hexdivstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  int8_t change_argument_value1=0  ;  /** Variable to check if the hexadecimal identifier "0x" is present
                                        * in the first given argument string.                              **/ 
  int8_t change_argument_value2=0  ;  /** Variable to check if the hexadecimal identifier "0x" is present
                                        * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &hexdivstr1,&hexdivstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (hexdivstr1[0] == '-' && hexdivstr1[1] == '0' && hexdivstr1[2] == 'x') {
    /** The first argument hexadecimal string is negativ and start with the hexadecimal identifier prefix "0x". **/
    
    hexdivstr1[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    hexdivstr1 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_1_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value1=2 ; /** Hexadecimal identifier detected with negativ sign.            **/ 
  }
  else if (hexdivstr1[0] == '0' && hexdivstr1[1] == 'x') {
    /** The first argument hexadecimal string start with the hexadecimal identifier prefix "0x". **/
    
    hexdivstr1 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the hexadecimal identifier prefix "0x".            **/ 
                             
    change_argument_value1=1 ; /** Hexadecimal identifier detected without negativ sign.         **/                         
  }
  else if (hexdivstr1[0] == '-') {
    /** The first argument hexadecimal string is negativ. **/
    
    is_1_negativ=true    ;   /** We set the first argument negativ boolean value on true.  **/     
  }
  
  
  if (hexdivstr2[0] == '-' && hexdivstr2[1] == '0' && hexdivstr2[2] == 'x') {
    /** The second argument hexadecimal string is negativ and start with the hexadecimal identifier prefix "0x". **/
    
    hexdivstr2[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    hexdivstr2 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=2 ;  /** Hexadecimal identifier detected with negativ sign.           **/ 
    
  }
  else if (hexdivstr2[0] == '0' && hexdivstr2[1] == 'x') {
    /** The second argument hexadecimal string start with the hexadecimal identifier prefix "0x". **/
    
    hexdivstr2 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the hexadecimal identifier prefix "0x".            **/
                                  
    change_argument_value2=1 ;  /** Hexadecimal identifier detected without negativ sign.        **/                                                 
  }
  else if (hexdivstr2[0] == '-') {
    /** The second argument hexadecimal string is negativ. **/
    
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(hexdivstr1) > 17 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 1 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(hexdivstr1) > 18 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the division function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 1 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(hexdivstr2) > 17 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 2 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(hexdivstr2) > 18 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the division function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string argument 2 length: 16 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(hexdivstr1,16) ) {
    /** The given string is not an valid hexadecimal string.                                
      * So we raise an ValueError exception and abort the division function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an hexadecimal string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(hexdivstr2,16) ) {
    /** The given string is not an valid hexadecimal string.                                
      * So we raise an ValueError exception and abort the division function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an hexadecimal string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(hexdivstr1) ) {
    /** The given string is not an valid hexadecimal float string, 
     *  but an hexadecimal integer string.                                
     *  So we raise an ValueError exception and abort the division function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an hexadecimal float string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  }
  
  if (! is_string_float(hexdivstr2) ) {
    /** The given string is not an valid hexadecimal float string, 
     *  but an hexadecimal integer string.                                
     *  So we raise an ValueError exception and abort the division function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an hexadecimal float string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f]") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the float part of the string. **/
  
  if ((ptr_point=strchr(hexdivstr1,'.')) != NULL ) {
    
    if (hexdivstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pointer for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      hexdivstr1++ ;
      is_1_negativ=true  ;
    }
    
    if ((ptr_point-hexdivstr1) > 16) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      hexdivstr1-- ;
    }
    
  }
  
  
  if ((ptr_point=strchr(hexdivstr2,'.')) != NULL ) {
    
    if (hexdivstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      hexdivstr1++ ;
      is_2_negativ=true  ;
    }
    
    if ((ptr_point-hexdivstr2) > 16) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      hexdivstr1-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( hexfloattofloat(hexdivstr1) > hexfloattofloat(hexdivstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( hexfloattofloat(hexdivstr1) < hexfloattofloat(hexdivstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  retval=hexfloatdivhexfloat(hexdivstr1,hexdivstr2) ;  /** We perform the division and store the result in retval.  **/
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexdivstr1 -= 2 ;
    hexdivstr1[2]='x' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexdivstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexdivstr2 -= 2 ;
    hexdivstr2[2]='x' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    hexdivstr2 -= 2 ;
  }  
  
  
  char string_to_return[128]              ;  /** We need an string to return it            **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.                 **/
   
  sprintf(string_to_return,"%.15Lf",retval) ;  /** Copy the result value into an string.   **/  
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.                      **/ 
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The division result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the division function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments quotient value to great for division.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The division result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the division function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments quotient value to great for division.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long double to python.       **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}
