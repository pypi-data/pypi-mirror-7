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
 * This file contains python wrapper functions for octal floats computing utilities:
 * 
 * -) octfloataddoctfloat: add two octal string with limitation of 8 bytes for the integer part,  
 *                         and 128 bits (16 bytes) for the entire octal string 
 *                         (without sign or octal identifier "0"). 
 *                         This function return an string with maximum 15 digits precision 
 *                         corrresponding to the C type double but pyhobdcalc compute internally 
 *                         with the type long long double to give you an exact double value back. 
 * 
 * -) octfloatsuboctfloat: substract two octal string with limitation of 8 bytes for the integer part,  
 *                         and 128 bits (16 bytes) for the entire octal string 
 *                         (without sign or octal identifier "0"). 
 *                         This function return an string with maximum 15 digits precision 
 *                         corrresponding to the C type double but pyhobdcalc compute internally 
 *                         with the type long long double to give you an exact value back. 
 * 
 * -) octfloatmultoctfloat: multiply two octal string with limitation of 8 bytes for the integer part,  
 *                          and 128 bits (16 bytes) for the entire octal string 
 *                          (without sign or octal identifier "0"). 
 *                          This function return an string with maximum 15 digits precision 
 *                          corrresponding to the C type double but pyhobdcalc compute internally 
 *                          with the type long long double to give you an exact value back. 
 * 
 * -) octfloatdivoctfloat: divide two octal string with limitation of 8 bytes for the integer part,  
 *                         and 128 bits (16 bytes) for the entire octal string 
 *                         (without sign or octal identifier "0"). 
 *                         This function return an string with maximum 15 digits precision 
 *                         corrresponding to the C type double but pyhobdcalc compute internally 
 *                         with the type long long double to give you an exact value back. 
 * 
 *****************************************************************************************************************/


static PyObject *
pyhobdcalc_octfloataddoctfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for adding two octal floats string and return the result as an float string. **/
  
  char *octaddstr1       ;            /** variable for converting an python string into an C string.       **/
  char *octaddstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  _Bool change_argument_value1=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the first given argument string.                             **/ 
                                        
  _Bool change_argument_value2=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &octaddstr1,&octaddstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (octaddstr1[0] == '-' && octaddstr1[1] == '0') {
    /** The first argument octal string is negativ and start with the octal identifier prefix "0". **/
    
    octaddstr1[1]='-'           ;  /** We set the negativ sign to index 1.                    **/
    octaddstr1++                ;  /** We increment the pointer to point on the negativ sign  
                                     * so that we get it at the string start.                 **/ 
    is_1_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
    change_argument_value1=true ;  /** Octal identifier detected with negativ sign.           **/ 
    
  }
  else if (octaddstr1[0] == '0') {
    /** The first argument start with the octal identifier prefix "0". **/
    
    octaddstr1++                ;  /** We increment the pointer to point on the data begin 
                                     * to ignore the octal identifier prefix "0".             **/ 
                       
    change_argument_value1=true ;  /** Octal identifier detected without negativ sign.        **/                    
  }
  else if (octaddstr1[0] == '-') {
    /** The first argument octal string is negativ. **/
    
    is_1_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
  }
  
  
  if (octaddstr2[0] == '-' && octaddstr2[1] == '0') {
    /** The second argument octal string is negativ and start with the octal identifier prefix "0". **/
    
    octaddstr2[1]='-'           ;  /** We set the negativ sign to index 1.                    **/
    octaddstr2++                ;  /** We increment the pointer to point on the negativ sign  
                                     * so that we get it at the string start.                 **/ 
    is_2_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=true ;  /** Octal identifier detected with negativ sign.           **/  
    
  }
  else if (octaddstr2[0] == '0') {
    /** The second argument octal string start with the octal identifier prefix "0". **/
    
    octaddstr2++                ;  /** We increment the pointer to point on the data begin 
                                     * to ignore the octal identifier prefix "0".             **/ 
    
    change_argument_value2=true ;  /** Octal identifier detected without negativ sign.        **/  
  }
  else if (octaddstr2[0] == '-') {
   /** The second argument octal string is negativ. **/
    
    is_2_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
  }
  
  
  if (strlen(octaddstr1) > 49 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octaddstr1) > 50 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(octaddstr2) > 49 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octaddstr2) > 50 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(octaddstr1,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the addition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(octaddstr2,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the addition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(octaddstr1) ) {
    /** The given string is not an valid octal float string, 
     *  but an octal integer string.                                
     *  So we raise an ValueError exception and abort the addition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal float string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  }
  
  if (! is_string_float(octaddstr2) ) {
    /** The given string is not an valid octal float string, 
     *  but an octal integer string.                                
     *  So we raise an ValueError exception and abort the addition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal float string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the integer part of the string. **/
  
  if ((ptr_point=strchr(octaddstr1,'.')) != NULL ) {
    
    if (octaddstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      octaddstr1++ ;
      is_1_negativ=true ;
    }
    
    if ((ptr_point-octaddstr1) > 24) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 21 digits.") ;
      return NULL ;
    }
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      octaddstr1-- ;
    }
    
  }
  
  if ((ptr_point=strchr(octaddstr2,'.')) != NULL ) {
    
    if (octaddstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      octaddstr2++ ;
      is_2_negativ=true ;
    }
    
    if ((ptr_point-octaddstr2) > 24) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 21 digits.") ;
      return NULL ;
    }
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      octaddstr2-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( octfloattofloat(octaddstr1) > octfloattofloat(octaddstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=false ;
    if ( fabsl(octfloattofloat(octaddstr2)) > fabsl(octfloattofloat(octaddstr1)) ) {
      is_result_negativ=true ;
    }
  }
  else if ( ( octfloattofloat(octaddstr1) < octfloattofloat(octaddstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }

  
  retval=octfloataddoctfloat(octaddstr1,octaddstr2) ;  /** We perform the addition and store the result in retval.  **/
  
  if (change_argument_value1 && is_1_negativ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octaddstr1--      ; 
    octaddstr1[1]='0' ; 
  }
  else if (change_argument_value1 && (! is_1_negativ) ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octaddstr1--      ;
  }
  
  if (change_argument_value2 && is_2_negativ) { 
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octaddstr2--      ; 
    octaddstr2[1]='0' ; 
  }
  else if (change_argument_value2 && (! is_2_negativ) ) { 
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octaddstr2--      ;
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
pyhobdcalc_octfloatsuboctfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for substracting two octal floats string and return the result as an float string. **/
  
  char *octsubstr1       ;            /** variable for converting an python string into an C string.       **/
  char *octsubstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  _Bool change_argument_value1=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the first given argument string.                             **/ 
                                        
  _Bool change_argument_value2=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &octsubstr1,&octsubstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (octsubstr1[0] == '-' && octsubstr1[1] == '0') {
    /** The first argument octal string is negativ and start with the octal identifier prefix "0". **/
    
    octsubstr1[1]='-'           ;  /** We set the negativ sign to index 1.                    **/
    octsubstr1++                ;  /** We increment the pointer to point on the negativ sign  
                                     * so that we get it at the string start.                 **/ 
    is_1_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
    change_argument_value1=true ;  /** Octal identifier detected with negativ sign.           **/ 
    
  }
  else if (octsubstr1[0] == '0') {
    /** The first argument start with the octal identifier prefix "0". **/
    
    octsubstr1++                ;  /** We increment the pointer to point on the data begin 
                                     * to ignore the octal identifier prefix "0".             **/ 
                       
    change_argument_value1=true ;  /** Octal identifier detected without negativ sign.        **/                    
  }
  else if (octsubstr1[0] == '-') {
    /** The first argument octal string is negativ. **/
    
    is_1_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
  }
  
  
  if (octsubstr2[0] == '-' && octsubstr2[1] == '0') {
    /** The second argument octal string is negativ and start with the octal identifier prefix "0". **/
    
    octsubstr2[1]='-'           ;  /** We set the negativ sign to index 1.                    **/
    octsubstr2++                ;  /** We increment the pointer to point on the negativ sign  
                                     * so that we get it at the string start.                 **/ 
    is_2_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=true ;  /** Octal identifier detected with negativ sign.           **/  
    
  }
  else if (octsubstr2[0] == '0') {
    /** The second argument octal string start with the octal identifier prefix "0". **/
    
    octsubstr2++                ;  /** We increment the pointer to point on the data begin 
                                     * to ignore the octal identifier prefix "0".             **/ 
    
    change_argument_value2=true ;  /** Octal identifier detected without negativ sign.        **/  
  }
  else if (octsubstr2[0] == '-') {
   /** The second argument octal string is negativ. **/
    
    is_2_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
  }
  
  
  if (strlen(octsubstr1) > 49 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octsubstr1) > 50 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(octsubstr2) > 49 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octsubstr2) > 50 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(octsubstr1,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the substraction function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(octsubstr2,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the substraction function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(octsubstr1) ) {
    /** The given string is not an valid octal float string, 
     *  but an octal integer string.                                
     *  So we raise an ValueError exception and abort the substraction function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal float string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  }
  
  if (! is_string_float(octsubstr2) ) {
    /** The given string is not an valid octal float string, 
     *  but an octal integer string.                                
     *  So we raise an ValueError exception and abort the substraction function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal float string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the integer part of the string. **/
  
  if ((ptr_point=strchr(octsubstr1,'.')) != NULL ) {
    
    if (octsubstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      octsubstr1++ ;
      is_1_negativ=true ;
    }
    
    if ((ptr_point-octsubstr1) > 24) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 21 digits.") ;
      return NULL ;
    }
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      octsubstr1-- ;
    }
    
  }
  
  
  if ((ptr_point=strchr(octsubstr2,'.')) != NULL ) {
    
    if (octsubstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      octsubstr2++ ;
      is_2_negativ=true ;
    }
    
    if ((ptr_point-octsubstr2) > 24) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 21 digits.") ;
      return NULL ;
    }
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      octsubstr2-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( octfloattofloat(octsubstr1) > octfloattofloat(octsubstr2) ) && (! is_1_negativ) &&  is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( ( octfloattofloat(octsubstr1) > octfloattofloat(octsubstr2) ) && is_1_negativ &&  is_2_negativ  ) {
    is_result_negativ=true ;
  }
  else if ( ( octfloattofloat(octsubstr1) > octfloattofloat(octsubstr2) ) && (! is_1_negativ) &&  (! is_2_negativ)  ) {
    is_result_negativ=false ;
  }
  else if ( ( octfloattofloat(octsubstr1) < octfloattofloat(octsubstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( octfloattofloat(octsubstr1) < octfloattofloat(octsubstr2) ) && is_1_negativ &&  is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( ( octfloattofloat(octsubstr1) < octfloattofloat(octsubstr2) ) && (! is_1_negativ) &&  (! is_2_negativ)  ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  
  retval=octfloatsuboctfloat(octsubstr1,octsubstr2) ;  /** We perform the substraction and store the result in retval.  **/
  
  if (change_argument_value1 && is_1_negativ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octsubstr1--      ; 
    octsubstr1[1]='0' ; 
  }
  else if (change_argument_value1 && (! is_1_negativ) ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octsubstr1--      ;
  }
  
  if (change_argument_value2 && is_2_negativ) { 
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octsubstr2--      ; 
    octsubstr2[1]='0' ; 
  }
  else if (change_argument_value2 && (! is_2_negativ) ) { 
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octsubstr2--      ;
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
pyhobdcalc_octfloatmultoctfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for multiplying two octal floats string and return the result as an float string. **/
  
  char *octmultstr1       ;            /** variable for converting an python string into an C string.       **/
  char *octmultstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  _Bool change_argument_value1=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the first given argument string.                             **/ 
                                        
  _Bool change_argument_value2=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &octmultstr1,&octmultstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (octmultstr1[0] == '-' && octmultstr1[1] == '0') {
    /** The first argument octal string is negativ and start with the octal identifier prefix "0". **/
    
    octmultstr1[1]='-'           ;  /** We set the negativ sign to index 1.                    **/
    octmultstr1++                ;  /** We increment the pointer to point on the negativ sign  
                                     * so that we get it at the string start.                 **/ 
    is_1_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
    change_argument_value1=true ;  /** Octal identifier detected with negativ sign.           **/ 
    
  }
  else if (octmultstr1[0] == '0') {
    /** The first argument start with the octal identifier prefix "0". **/
    
    octmultstr1++                ;  /** We increment the pointer to point on the data begin 
                                     * to ignore the octal identifier prefix "0".             **/ 
                       
    change_argument_value1=true ;  /** Octal identifier detected without negativ sign.        **/                    
  }
  else if (octmultstr1[0] == '-') {
    /** The first argument octal string is negativ. **/
    
    is_1_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
  }
  
  
  if (octmultstr2[0] == '-' && octmultstr2[1] == '0') {
    /** The second argument octal string is negativ and start with the octal identifier prefix "0". **/
    
    octmultstr2[1]='-'           ;  /** We set the negativ sign to index 1.                    **/
    octmultstr2++                ;  /** We increment the pointer to point on the negativ sign  
                                     * so that we get it at the string start.                 **/ 
    is_2_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=true ;  /** Octal identifier detected with negativ sign.           **/  
    
  }
  else if (octmultstr2[0] == '0') {
    /** The second argument octal string start with the octal identifier prefix "0". **/
    
    octmultstr2++                ;  /** We increment the pointer to point on the data begin 
                                     * to ignore the octal identifier prefix "0".             **/ 
    
    change_argument_value2=true ;  /** Octal identifier detected without negativ sign.        **/  
  }
  else if (octmultstr2[0] == '-') {
   /** The second argument octal string is negativ. **/
    
    is_2_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
  }
  
  
  if (strlen(octmultstr1) > 49 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octmultstr1) > 50 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multiplication function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(octmultstr2) > 49 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octmultstr2) > 50 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multiplication function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(octmultstr1,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the multiplication function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(octmultstr2,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the multiplication function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(octmultstr1) ) {
    /** The given string is not an valid octal float string, 
     *  but an octal integer string.                                
     *  So we raise an ValueError exception and abort the multiplication function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal float string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  }
  
  if (! is_string_float(octmultstr2) ) {
    /** The given string is not an valid octal float string, 
     *  but an octal integer string.                                
     *  So we raise an ValueError exception and abort the multiplication function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal float string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the integer part of the string. **/
  
  if ((ptr_point=strchr(octmultstr1,'.')) != NULL ) {
    
    if (octmultstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      octmultstr1++ ;
      is_1_negativ=true ;
    }
    
    if ((ptr_point-octmultstr1) > 24) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 21 digits.") ;
      return NULL ;
    }
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      octmultstr1-- ;
    }
    
  }
  
    
  if ((ptr_point=strchr(octmultstr2,'.')) != NULL ) {
    
    if (octmultstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      octmultstr2++ ;
      is_2_negativ=true ;
    }
    
    if ((ptr_point-octmultstr2) > 24) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 21 digits.") ;
      return NULL ;
    }
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      octmultstr2-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( octfloattofloat(octmultstr1) > octfloattofloat(octmultstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( octfloattofloat(octmultstr1) < octfloattofloat(octmultstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  
  retval=octfloatmultoctfloat(octmultstr1,octmultstr2) ;  /** We perform the multiplication and store the result in retval.  **/
  
  if (change_argument_value1 && is_1_negativ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octmultstr1--      ; 
    octmultstr1[1]='0' ; 
  }
  else if (change_argument_value1 && (! is_1_negativ) ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octmultstr1--      ;
  }
  
  if (change_argument_value2 && is_2_negativ) { 
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octmultstr2--      ; 
    octmultstr2[1]='0' ; 
  }
  else if (change_argument_value2 && (! is_2_negativ) ) { 
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octmultstr2--      ;
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
pyhobdcalc_octfloatdivoctfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for dividing two octal floats string and return the result as an float string. **/
  
  char *octdivstr1       ;            /** variable for converting an python string into an C string.       **/
  char *octdivstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  _Bool change_argument_value1=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the first given argument string.                             **/ 
                                        
  _Bool change_argument_value2=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &octdivstr1,&octdivstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (octdivstr1[0] == '-' && octdivstr1[1] == '0') {
    /** The first argument octal string is negativ and start with the octal identifier prefix "0". **/
    
    octdivstr1[1]='-'           ;  /** We set the negativ sign to index 1.                    **/
    octdivstr1++                ;  /** We increment the pointer to point on the negativ sign  
                                     * so that we get it at the string start.                 **/ 
    is_1_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
    change_argument_value1=true ;  /** Octal identifier detected with negativ sign.           **/ 
    
  }
  else if (octdivstr1[0] == '0') {
    /** The first argument start with the octal identifier prefix "0". **/
    
    octdivstr1++                ;  /** We increment the pointer to point on the data begin 
                                     * to ignore the octal identifier prefix "0".             **/ 
                       
    change_argument_value1=true ;  /** Octal identifier detected without negativ sign.        **/                    
  }
  else if (octdivstr1[0] == '-') {
    /** The first argument octal string is negativ. **/
    
    is_1_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
  }
  
  
  if (octdivstr2[0] == '-' && octdivstr2[1] == '0') {
    /** The second argument octal string is negativ and start with the octal identifier prefix "0". **/
    
    octdivstr2[1]='-'           ;  /** We set the negativ sign to index 1.                    **/
    octdivstr2++                ;  /** We increment the pointer to point on the negativ sign  
                                     * so that we get it at the string start.                 **/ 
    is_2_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=true ;  /** Octal identifier detected with negativ sign.           **/  
    
  }
  else if (octdivstr2[0] == '0') {
    /** The second argument octal string start with the octal identifier prefix "0". **/
    
    octdivstr2++                ;  /** We increment the pointer to point on the data begin 
                                     * to ignore the octal identifier prefix "0".             **/ 
    
    change_argument_value2=true ;  /** Octal identifier detected without negativ sign.        **/  
  }
  else if (octdivstr2[0] == '-') {
   /** The second argument octal string is negativ. **/
    
    is_2_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
  }
  
  
  if (strlen(octdivstr1) > 49 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octdivstr1) > 50 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the division function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(octdivstr2) > 49 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octdivstr2) > 50 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the division function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 48 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(octdivstr1,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the division function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(octdivstr2,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the division function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(octdivstr1) ) {
    /** The given string is not an valid octal float string, 
     *  but an octal integer string.                                
     *  So we raise an ValueError exception and abort the division function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal float string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  }
  
  if (! is_string_float(octdivstr2) ) {
    /** The given string is not an valid octal float string, 
     *  but an octal integer string.                                
     *  So we raise an ValueError exception and abort the division function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal float string: in form [-][0][0-7].[0-7].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the integer part of the string. **/
  
  if ((ptr_point=strchr(octdivstr1,'.')) != NULL ) {
    
    if (octdivstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      octdivstr1++ ;
      is_1_negativ=true ;
    }
    
    if ((ptr_point-octdivstr1) > 24) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 21 digits.") ;
      return NULL ;
    }
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      octdivstr1-- ;
    }
    
  }
  
    
  if ((ptr_point=strchr(octdivstr2,'.')) != NULL ) {
    
    if (octdivstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      octdivstr2++ ;
      is_2_negativ=true ;
    }
    
    if ((ptr_point-octdivstr2) > 24) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 21 digits.") ;
      return NULL ;
    }
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      octdivstr2-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( octfloattofloat(octdivstr1) > octfloattofloat(octdivstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( octfloattofloat(octdivstr1) < octfloattofloat(octdivstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  
  retval=octfloatdivoctfloat(octdivstr1,octdivstr2) ;  /** We perform the division and store the result in retval.  **/
  
  if (change_argument_value1 && is_1_negativ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octdivstr1--      ; 
    octdivstr1[1]='0' ; 
  }
  else if (change_argument_value1 && (! is_1_negativ) ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octdivstr1--      ;
  }
  
  if (change_argument_value2 && is_2_negativ) { 
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octdivstr2--      ; 
    octdivstr2[1]='0' ; 
  }
  else if (change_argument_value2 && (! is_2_negativ) ) { 
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octdivstr2--      ;
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
