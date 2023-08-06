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
 * This file contains python wrapper functions for binar floats computing utilities:
 * 
 * -) binfloataddbinfloat: add two binar string with limitation of 8 bytes for the integer part,  
 *                         and 128 bits (16 bytes) for the entire binar string 
 *                         (without sign or binar identifier "0b"). 
 *                         This function return an string with maximum 15 digits precision 
 *                         corrresponding to the C type double but pyhobdcalc compute internally 
 *                         with the type long long double to give you an exact double value back. 
 * 
 * -) binfloatsubbinfloat: substract two binar string with limitation of 8 bytes for the integer part,  
 *                         and 128 bits (16 bytes) for the entire binar string 
 *                         (without sign or binar identifier "0b"). 
 *                         This function return an string with maximum 15 digits precision 
 *                         corrresponding to the C type double but pyhobdcalc compute internally 
 *                         with the type long long double to give you an exact value back. 
 * 
 * -) binfloatmultbinfloat: multiply two binar string with limitation of 8 bytes for the integer part,  
 *                          and 128 bits (16 bytes) for the entire binar string 
 *                          (without sign or binar identifier "0b"). 
 *                          This function return an string with maximum 15 digits precision 
 *                          corrresponding to the C type double but pyhobdcalc compute internally 
 *                          with the type long long double to give you an exact value back. 
 * 
 * -) binfloatdivbinfloat: divide two binar string with limitation of 8 bytes for the integer part,  
 *                         and 128 bits (16 bytes) for the entire binar string 
 *                         (without sign or binar identifier "0b"). 
 *                         This function return an string with maximum 15 digits precision 
 *                         corrresponding to the C type double but pyhobdcalc compute internally 
 *                         with the type long long double to give you an exact value back. 
 * 
 *****************************************************************************************************************/

static PyObject *
pyhobdcalc_binfloataddbinfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for adding two binar floats string and return the result as an float string. **/
  
  char *binaddstr1       ;            /** variable for converting an python string into an C string.       **/
  char *binaddstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  int8_t change_argument_value1=0  ;  /** Variable to check if the binar identifier "0b" is present
                                        * in the first given argument string.                              **/ 
  int8_t change_argument_value2=0  ;  /** Variable to check if the binar identifier "0b" is present
                                        * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &binaddstr1,&binaddstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (binaddstr1[0] == '-' && binaddstr1[1] == '0' && binaddstr1[2] == 'b') {
    /** The first argument binar string is negativ and start with the binar identifier prefix "0b". **/
    
    binaddstr1[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    binaddstr1 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_1_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value1=2 ; /** Binar identifier detected with negativ sign.            **/ 
  }
  else if (binaddstr1[0] == '0' && binaddstr1[1] == 'b') {
    /** The first argument binar string start with the binar identifier prefix "0b". **/
    
    binaddstr1 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/ 
                             
    change_argument_value1=1 ; /** Binar identifier detected without negativ sign.         **/                         
  }
  else if (binaddstr1[0] == '-') {
    /** The first argument binar string is negativ. **/
    
    is_1_negativ=true    ;   /** We set the first argument negativ boolean value on true.  **/     
  }
  
  
  if (binaddstr2[0] == '-' && binaddstr2[1] == '0' && binaddstr2[2] == 'b') {
    /** The second argument binar string is negativ and start with the binar identifier prefix "0b". **/
    
    binaddstr2[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    binaddstr2 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=2 ;  /** Binar identifier detected with negativ sign.           **/ 
    
  }
  else if (binaddstr2[0] == '0' && binaddstr2[1] == 'b') {
    /** The second argument binar string start with the binar identifier prefix "0b". **/
    
    binaddstr2 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/
                                  
    change_argument_value2=1 ;  /** Binar identifier detected without negativ sign.        **/                                                 
  }
  else if (binaddstr2[0] == '-') {
    /** The second argument binar string is negativ. **/
    
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(binaddstr1) > 129 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binaddstr1) > 130 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(binaddstr2) > 129 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binaddstr2) > 130 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(binaddstr1,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the addition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar string: in form [-][0b][01].[01].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(binaddstr2,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the addition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar string: in form [-][0b][01].[01].") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(binaddstr1) ) {
    /** The given string is not an valid binar float string, 
     *  but an binar integer string.                                
     *  So we raise an ValueError exception and abort the addition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar float string: in form [-][0b][01].[01].") ;
    return NULL ;
  }
  
  if (! is_string_float(binaddstr2) ) {
    /** The given string is not an valid binar float string, 
     *  but an binar integer string.                                
     *  So we raise an ValueError exception and abort the addition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar float string: in form [-][0b][01].[01].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the float part of the string. **/
  
  if ((ptr_point=strchr(binaddstr1,'.')) != NULL ) {
    
    if (binaddstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pointer for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      binaddstr1++ ;
      is_1_negativ=true  ;
    }
    
    if ((ptr_point-binaddstr1) > 64) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      binaddstr1-- ;
    }
    
  }
  
  
  if ((ptr_point=strchr(binaddstr2,'.')) != NULL ) {
    
    if (binaddstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      binaddstr1++ ;
      is_2_negativ=true  ;
    }
    
    if ((ptr_point-binaddstr2) > 64) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      binaddstr1-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( binfloattofloat(binaddstr1) > binfloattofloat(binaddstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=false ;
    if ( fabsl(binfloattofloat(binaddstr2)) > fabsl(binfloattofloat(binaddstr1)) ) {
      is_result_negativ=true ;
    }
  }
  else if ( ( binfloattofloat(binaddstr1) < binfloattofloat(binaddstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  retval=binfloataddbinfloat(binaddstr1,binaddstr2) ;  /** We perform the division and store the result in retval.  **/
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binaddstr1 -= 2 ;
    binaddstr1[2]='b' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binaddstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binaddstr2 -= 2 ;
    binaddstr2[2]='b' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binaddstr2 -= 2 ;
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
  
  /** We return the operation result as an string because we cannot return an long long int to python.     **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}







static PyObject *
pyhobdcalc_binfloatsubbinfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for subing two binar floats string and return the result as an float string. **/
  
  char *binsubstr1       ;            /** variable for converting an python string into an C string.       **/
  char *binsubstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  int8_t change_argument_value1=0  ;  /** Variable to check if the binar identifier "0b" is present
                                        * in the first given argument string.                              **/ 
  int8_t change_argument_value2=0  ;  /** Variable to check if the binar identifier "0b" is present
                                        * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &binsubstr1,&binsubstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (binsubstr1[0] == '-' && binsubstr1[1] == '0' && binsubstr1[2] == 'b') {
    /** The first argument binar string is negativ and start with the binar identifier prefix "0b". **/
    
    binsubstr1[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    binsubstr1 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_1_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value1=2 ; /** Binar identifier detected with negativ sign.            **/ 
  }
  else if (binsubstr1[0] == '0' && binsubstr1[1] == 'b') {
    /** The first argument binar string start with the binar identifier prefix "0b". **/
    
    binsubstr1 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/ 
                             
    change_argument_value1=1 ; /** Binar identifier detected without negativ sign.         **/                         
  }
  else if (binsubstr1[0] == '-') {
    /** The first argument binar string is negativ. **/
    
    is_1_negativ=true    ;   /** We set the first argument negativ boolean value on true.  **/     
  }
  
  
  if (binsubstr2[0] == '-' && binsubstr2[1] == '0' && binsubstr2[2] == 'b') {
    /** The second argument binar string is negativ and start with the binar identifier prefix "0b". **/
    
    binsubstr2[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    binsubstr2 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=2 ;  /** Binar identifier detected with negativ sign.           **/ 
    
  }
  else if (binsubstr2[0] == '0' && binsubstr2[1] == 'b') {
    /** The second argument binar string start with the binar identifier prefix "0b". **/
    
    binsubstr2 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/
                                  
    change_argument_value2=1 ;  /** Binar identifier detected without negativ sign.        **/                                                 
  }
  else if (binsubstr2[0] == '-') {
    /** The second argument binar string is negativ. **/
    
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(binsubstr1) > 129 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binsubstr1) > 130 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(binsubstr2) > 129 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binsubstr2) > 130 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(binsubstr1,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the substraction function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar string: in form [-][0b][01].[01].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(binsubstr2,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the substraction function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar string: in form [-][0b][01].[01].") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(binsubstr1) ) {
    /** The given string is not an valid binar float string, 
     *  but an binar integer string.                                
     *  So we raise an ValueError exception and abort the substraction function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar float string: in form [-][0b][01].[01].") ;
    return NULL ;
  }
  
  if (! is_string_float(binsubstr2) ) {
    /** The given string is not an valid binar float string, 
     *  but an binar integer string.                                
     *  So we raise an ValueError exception and abort the substraction function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar float string: in form [-][0b][01].[01].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the float part of the string. **/
  
  if ((ptr_point=strchr(binsubstr1,'.')) != NULL ) {
    
    if (binsubstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pointer for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      binsubstr1++ ;
      is_1_negativ=true  ;
    }
    
    if ((ptr_point-binsubstr1) > 64) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      binsubstr1-- ;
    }
    
  }
  
  
  if ((ptr_point=strchr(binsubstr2,'.')) != NULL ) {
    
    if (binsubstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      binsubstr1++ ;
      is_2_negativ=true  ;
    }
    
    if ((ptr_point-binsubstr2) > 64) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      binsubstr1-- ;
    }
    
  }
  
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( binfloattofloat(binsubstr1) > binfloattofloat(binsubstr2) ) && (! is_1_negativ) &&  is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( ( binfloattofloat(binsubstr1) > binfloattofloat(binsubstr2) ) && is_1_negativ &&  is_2_negativ  ) {
    is_result_negativ=true ;
  }
  else if ( ( binfloattofloat(binsubstr1) > binfloattofloat(binsubstr2) ) && (! is_1_negativ) &&  (! is_2_negativ)  ) {
    is_result_negativ=false ;
  }
  else if ( ( binfloattofloat(binsubstr1) < binfloattofloat(binsubstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( binfloattofloat(binsubstr1) < binfloattofloat(binsubstr2) ) && is_1_negativ &&  is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( ( binfloattofloat(binsubstr1) < binfloattofloat(binsubstr2) ) && (! is_1_negativ) &&  (! is_2_negativ)  ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  retval=binfloatsubbinfloat(binsubstr1,binsubstr2) ;  /** We perform the division and store the result in retval.  **/
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binsubstr1 -= 2 ;
    binsubstr1[2]='b' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binsubstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binsubstr2 -= 2 ;
    binsubstr2[2]='b' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binsubstr2 -= 2 ;
  }  
  
  
  char string_to_return[128]              ;  /** We need an string to return it            **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.                 **/
   
  sprintf(string_to_return,"%.15Lf",retval) ;  /** Copy the result value into an string.   **/  
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.                      **/ 
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The subtion result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the substraction function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments substract value to great for substraction.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The subtion result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the substraction function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments substract value to great for substraction.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long long int to python.     **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}





static PyObject *
pyhobdcalc_binfloatmultbinfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for multing two binar floats string and return the result as an float string. **/
  
  char *binmultstr1       ;            /** variable for converting an python string into an C string.       **/
  char *binmultstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  int8_t change_argument_value1=0  ;  /** Variable to check if the binar identifier "0b" is present
                                        * in the first given argument string.                              **/ 
  int8_t change_argument_value2=0  ;  /** Variable to check if the binar identifier "0b" is present
                                        * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &binmultstr1,&binmultstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (binmultstr1[0] == '-' && binmultstr1[1] == '0' && binmultstr1[2] == 'b') {
    /** The first argument binar string is negativ and start with the binar identifier prefix "0b". **/
    
    binmultstr1[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    binmultstr1 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_1_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value1=2 ; /** Binar identifier detected with negativ sign.            **/ 
  }
  else if (binmultstr1[0] == '0' && binmultstr1[1] == 'b') {
    /** The first argument binar string start with the binar identifier prefix "0b". **/
    
    binmultstr1 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/ 
                             
    change_argument_value1=1 ; /** Binar identifier detected without negativ sign.         **/                         
  }
  else if (binmultstr1[0] == '-') {
    /** The first argument binar string is negativ. **/
    
    is_1_negativ=true    ;   /** We set the first argument negativ boolean value on true.  **/     
  }
  
  
  if (binmultstr2[0] == '-' && binmultstr2[1] == '0' && binmultstr2[2] == 'b') {
    /** The second argument binar string is negativ and start with the binar identifier prefix "0b". **/
    
    binmultstr2[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    binmultstr2 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=2 ;  /** Binar identifier detected with negativ sign.           **/ 
    
  }
  else if (binmultstr2[0] == '0' && binmultstr2[1] == 'b') {
    /** The second argument binar string start with the binar identifier prefix "0b". **/
    
    binmultstr2 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/
                                  
    change_argument_value2=1 ;  /** Binar identifier detected without negativ sign.        **/                                                 
  }
  else if (binmultstr2[0] == '-') {
    /** The second argument binar string is negativ. **/
    
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(binmultstr1) > 129 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binmultstr1) > 130 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(binmultstr2) > 129 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binmultstr2) > 130 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(binmultstr1,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the multition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar string: in form [-][0b][01].[01].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(binmultstr2,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the multition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar string: in form [-][0b][01].[01].") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(binmultstr1) ) {
    /** The given string is not an valid binar float string, 
     *  but an binar integer string.                                
     *  So we raise an ValueError exception and abort the multition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar float string: in form [-][0b][01].[01].") ;
    return NULL ;
  }
  
  if (! is_string_float(binmultstr2) ) {
    /** The given string is not an valid binar float string, 
     *  but an binar integer string.                                
     *  So we raise an ValueError exception and abort the multition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar float string: in form [-][0b][01].[01].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the float part of the string. **/
  
  if ((ptr_point=strchr(binmultstr1,'.')) != NULL ) {
    
    if (binmultstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pointer for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      binmultstr1++ ;
      is_1_negativ=true  ;
    }
    
    if ((ptr_point-binmultstr1) > 64) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      binmultstr1-- ;
    }
    
  }
  
  
  if ((ptr_point=strchr(binmultstr2,'.')) != NULL ) {
    
    if (binmultstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      binmultstr1++ ;
      is_2_negativ=true  ;
    }
    
    if ((ptr_point-binmultstr2) > 64) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      binmultstr1-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( binfloattofloat(binmultstr1) > binfloattofloat(binmultstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( binfloattofloat(binmultstr1) < binfloattofloat(binmultstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  retval=binfloatmultbinfloat(binmultstr1,binmultstr2) ;  /** We perform the division and store the result in retval.  **/
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binmultstr1 -= 2 ;
    binmultstr1[2]='b' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binmultstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binmultstr2 -= 2 ;
    binmultstr2[2]='b' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    binmultstr2 -= 2 ;
  }  
  
  
  char string_to_return[128]              ;  /** We need an string to return it            **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.                 **/
   
  sprintf(string_to_return,"%.15Lf",retval) ;  /** Copy the result value into an string.   **/  
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.                      **/ 
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The multtion result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the multition function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments product value to great for multition.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The multtion result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the multition function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments product value to great for multition.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long long int to python.     **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}




static PyObject *
pyhobdcalc_binfloatdivbinfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for diving two binar floats string and return the result as an float string. **/
  
  char *bindivstr1       ;            /** variable for converting an python string into an C string.       **/
  char *bindivstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long double retval     ;            /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false      ;     /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false      ;     /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;     /** Boolean value to check if the result should be negativ.          **/
  
  int8_t change_argument_value1=0  ;  /** Variable to check if the binar identifier "0b" is present
                                        * in the first given argument string.                              **/ 
  int8_t change_argument_value2=0  ;  /** Variable to check if the binar identifier "0b" is present
                                        * in the second given argument string.                             **/ 

  if (!PyArg_ParseTuple(args, "ss", &bindivstr1,&bindivstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (bindivstr1[0] == '-' && bindivstr1[1] == '0' && bindivstr1[2] == 'b') {
    /** The first argument binar string is negativ and start with the binar identifier prefix "0b". **/
    
    bindivstr1[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    bindivstr1 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_1_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value1=2 ; /** Binar identifier detected with negativ sign.            **/ 
  }
  else if (bindivstr1[0] == '0' && bindivstr1[1] == 'b') {
    /** The first argument binar string start with the binar identifier prefix "0b". **/
    
    bindivstr1 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/ 
                             
    change_argument_value1=1 ; /** Binar identifier detected without negativ sign.         **/                         
  }
  else if (bindivstr1[0] == '-') {
    /** The first argument binar string is negativ. **/
    
    is_1_negativ=true    ;   /** We set the first argument negativ boolean value on true.  **/     
  }
  
  
  if (bindivstr2[0] == '-' && bindivstr2[1] == '0' && bindivstr2[2] == 'b') {
    /** The second argument binar string is negativ and start with the binar identifier prefix "0b". **/
    
    bindivstr2[2]='-'        ;  /** We set the negativ sign to index 2.                    **/
    bindivstr2 += 2          ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=2 ;  /** Binar identifier detected with negativ sign.           **/ 
    
  }
  else if (bindivstr2[0] == '0' && bindivstr2[1] == 'b') {
    /** The second argument binar string start with the binar identifier prefix "0b". **/
    
    bindivstr2 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/
                                  
    change_argument_value2=1 ;  /** Binar identifier detected without negativ sign.        **/                                                 
  }
  else if (bindivstr2[0] == '-') {
    /** The second argument binar string is negativ. **/
    
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(bindivstr1) > 129 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(bindivstr1) > 130 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the divition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(bindivstr2) > 129 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(bindivstr2) > 130 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the divition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 128 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(bindivstr1,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the divition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar string: in form [-][0b][01].[01].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(bindivstr2,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the divition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar string: in form [-][0b][01].[01].") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(bindivstr1) ) {
    /** The given string is not an valid binar float string, 
     *  but an binar integer string.                                
     *  So we raise an ValueError exception and abort the divition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar float string: in form [-][0b][01].[01].") ;
    return NULL ;
  }
  
  if (! is_string_float(bindivstr2) ) {
    /** The given string is not an valid binar float string, 
     *  but an binar integer string.                                
     *  So we raise an ValueError exception and abort the divition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar float string: in form [-][0b][01].[01].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the float part of the string. **/
  
  if ((ptr_point=strchr(bindivstr1,'.')) != NULL ) {
    
    if (bindivstr1[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pointer for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      bindivstr1++ ;
      is_1_negativ=true  ;
    }
    
    if ((ptr_point-bindivstr1) > 64) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_1_negativ) {
      /** We reset the pointer on data begin. **/
      
      bindivstr1-- ;
    }
    
  }
  
  
  if ((ptr_point=strchr(bindivstr2,'.')) != NULL ) {
    
    if (bindivstr2[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      bindivstr1++ ;
      is_2_negativ=true  ;
    }
    
    if ((ptr_point-bindivstr2) > 64) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_2_negativ) {
      /** We reset the pointer on data begin. **/
      
      bindivstr1-- ;
    }
    
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( binfloattofloat(bindivstr1) > binfloattofloat(bindivstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( binfloattofloat(bindivstr1) < binfloattofloat(bindivstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  retval=binfloatdivbinfloat(bindivstr1,bindivstr2) ;  /** We perform the division and store the result in retval.  **/
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    bindivstr1 -= 2 ;
    bindivstr1[2]='b' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    bindivstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    bindivstr2 -= 2 ;
    bindivstr2[2]='b' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                     **/
    
    bindivstr2 -= 2 ;
  }  
  
  
  char string_to_return[128]              ;  /** We need an string to return it            **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.                 **/
   
  sprintf(string_to_return,"%.15Lf",retval) ;  /** Copy the result value into an string.   **/  
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.                      **/ 
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The divtion result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the divition function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments quotient value to great for divition.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The divtion result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the divition function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments quotient value to great for divition.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long long int to python.     **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}
