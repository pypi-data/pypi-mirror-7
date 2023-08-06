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
 * This file contains python wrapper functions for binar integer computing utilities:
 * 
 * -) binaddbin: add two binar string with limitation of the C type long long int, 
 *               so you can compute with signed values.
 * 
 * -) binsubbin: substract two binar string with limitation of the C type long long int, 
 *               so you can compute with signed values.
 * 
 * -) binmultbin: multiply two binar string with limitation of the C type long long int, 
 *                so you can compute with signed values.
 * 
 * -) bindivbin: substract two binar string with limitation of the C type long long int, 
 *               for the integer part of the binar strings which return an string 
 *               with maximum 15 digits precision corrresponding to the C type double.
 * 
 *****************************************************************************************************************/

static PyObject *
pyhobdcalc_binaddbin(PyObject *self, PyObject *args) {
  /** Python function wrapper for adding two binar integer string and return the result as an integer string. **/
  
  char *binaddstr1       ;            /** variable for converting an python string into an C string.       **/
  char *binaddstr2       ;            /** variable for converting an python string into an C string.       **/
  
  long long int retval   ;            /** Variable for result computing.                                   **/
  
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
  
  
  if (strlen(binaddstr1) > 64 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binaddstr1) > 65 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(binaddstr2) > 63 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binaddstr2) > 64 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(binaddstr1,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the addition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar string: in form [-][0b][01].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(binaddstr2,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the addition function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar string: in form [-][0b][01].") ;
    return NULL ;
  
    
  }
  
  
  if ( is_string_float(binaddstr1) ) {
    /** The given string is not an valid binar integer string, 
     *  but an binar float string.                                
     *  So we raise an ValueError exception and abort the addition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar integer string: in form [-][0b][01].") ;
    return NULL ;
  }
  
  if ( is_string_float(binaddstr2) ) {
    /** The given string is not an valid binar integer string, 
     *  but an binar float string.                                
     *  So we raise an ValueError exception and abort the addition function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar integer string: in form [-][0b][01].") ;
    return NULL ;
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( bintoint(binaddstr1) > bintoint(binaddstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=false ;
    if ( llabs(bintoint(binaddstr2)) > llabs(bintoint(binaddstr1)) ) {
      is_result_negativ=true ;
    }
  }
  else if ( ( bintoint(binaddstr1) < bintoint(binaddstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  
  
  retval=binaddbin(binaddstr1,binaddstr2) ; /** We perform the addition and store the result in retval.  **/ 
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binaddstr1 -= 2 ;
    binaddstr1[2]='b' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binaddstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binaddstr2 -= 2 ;
    binaddstr2[2]='b' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binaddstr2 -= 2 ;
  }  
  
  char string_to_return[128]              ;  /** We need an string to return it        **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.             **/
   
  sprintf(string_to_return,"%lli",retval) ;  /** Copy the result value into an string. **/  
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The addtion result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the addition function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments summe value to great for addition.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The addtion result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the addition function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments summe value to great for addition.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long long int to python.     **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}


static PyObject *
pyhobdcalc_binsubbin(PyObject *self, PyObject *args) {
  /** Python function wrapper for subtracting two binar integer string and return the result as an integer string. **/
  
  char *binsubstr1         ;  /** variable for converting an python string into an C string.       **/
  char *binsubstr2         ;  /** variable for converting an python string into an C string.       **/
  
  long long int retval     ;  /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false ;  /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false ;  /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;  /** Boolean value to check if the result should be negativ.     **/
  
  int8_t change_argument_value1=0  ; /** Variable to check if the binar identifier "0b" is present
                                       * in the first given argument string.                       **/ 
  int8_t change_argument_value2=0  ; /** Variable to check if the binar identifier "0b" is present
                                       * in the second given argument string.                      **/ 
  
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
    
    change_argument_value1=2 ;  /** Binar identifier detected with negativ sign.           **/ 
    
  }
  else if (binsubstr1[0] == '0' && binsubstr1[1] == 'b') {
    /** The first argument binar string start with the binar identifier prefix "0b". **/
    
    binsubstr1 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/
                             
    change_argument_value1=1 ;  /** Binar identifier detected without negativ sign.        **/                            
  }
  else if (binsubstr1[0] == '-') {
    /** The first argument binar string is negativ. **/
    
    is_1_negativ=true    ;      /** We set the negativ boolean value on true.              **/     
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
    /** The first argument binar string is negativ. **/
    
    is_2_negativ=true        ;   /** We set the negativ boolean value on true.             **/     
  }
  
  
  if (strlen(binsubstr1) > 64 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binsubstr1) > 65 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(binsubstr2) > 64 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binsubstr2) > 65 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(binsubstr1,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the substraction function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar string: in form [-][0b][01].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(binsubstr2,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the substraction function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar string: in form [-][0b][01].") ;
    return NULL ;
  
    
  }
  
  
  if ( is_string_float(binsubstr1) ) {
    /** The given string is not an valid binar integer string, 
     *  but an binar float string.                                
     *  So we raise an ValueError exception and abort the substraction function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar integer string: in form [-][0b][01].") ;
    return NULL ;
  }
  
  if ( is_string_float(binsubstr2) ) {
    /** The given string is not an valid binar integer string, 
     *  but an binar float string.                                
     *  So we raise an ValueError exception and abort the substraction function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar integer string: in form [-][0b][01].") ;
    return NULL ;
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( bintoint(binsubstr1) > bintoint(binsubstr2) ) && (! is_1_negativ) &&  is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( ( bintoint(binsubstr1) > bintoint(binsubstr2) ) && is_1_negativ &&  is_2_negativ  ) {
    is_result_negativ=true ;
  }
  else if ( ( bintoint(binsubstr1) > bintoint(binsubstr2) ) && (! is_1_negativ) &&  (! is_2_negativ)  ) {
    is_result_negativ=false ;
  }
  else if ( ( bintoint(binsubstr1) < bintoint(binsubstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( bintoint(binsubstr1) < bintoint(binsubstr2) ) && is_1_negativ &&  is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( ( bintoint(binsubstr1) < bintoint(binsubstr2) ) && (! is_1_negativ) &&  (! is_2_negativ)  ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  
  retval=binsubbin(binsubstr1,binsubstr2) ; /** We perform the substraction and store the result in retval.  **/  
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binsubstr1 -= 2 ;
    binsubstr1[2]='b' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binsubstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binsubstr2 -= 2 ;
    binsubstr2[2]='b' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binsubstr2 -= 2 ;
  }  
  
  
  char string_to_return[128]              ;  /** We need an string to return it         **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.              **/
   
  sprintf(string_to_return,"%lli",retval) ;  /** Copy the result value into an string.  **/  
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The substraction result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the substraction function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments substract to great for substraction.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The substraction result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the substraction function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments substract to great for substraction.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long long int to python.     **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}



static PyObject *
pyhobdcalc_binmultbin(PyObject *self, PyObject *args) {
  /** Python function wrapper for multiplying two binar integer string and return the result as an integer string. **/
  
  char *binmultstr1        ;  /** variable for converting an python string into an C string.      **/ 
  char *binmultstr2        ;  /** variable for converting an python string into an C string.      **/
  
  long long int retval     ;  /** Variable for result computing.                                  **/
  
  _Bool is_1_negativ=false ;  /** Boolean value to check if the given first argument is negativ.  **/
  _Bool is_2_negativ=false ;  /** Boolean value to check if the given second argument is negativ. **/
  
  _Bool is_result_negativ=false ; /** Boolean value to check if the result should be negativ.     **/
  
  int8_t change_argument_value1=0 ; /** Variable to check if the binar identifier "0b" is present
                                      * in the first given argument string.                       **/
  int8_t change_argument_value2=0 ; /** Variable to check if the binar identifier "0b" is present
                                      * in the second given argument string.                      **/ 
  
  if (!PyArg_ParseTuple(args, "ss", &binmultstr1,&binmultstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (binmultstr1[0] == '-' && binmultstr1[1] == '0' && binmultstr1[2] == 'b') {
    /** The first argument binar string is negativ and start with the binar identifier prefix "0b". **/
    
    binmultstr1[2]='-'       ;  /** We set the negativ sign to index 2.                    **/
    binmultstr1 += 2         ;  /** We increment the pointer to point on the negativ sign  
                                  * so that we get it at the string start.                 **/ 
    is_1_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value1=2 ;  /** Binar identifier detected with negativ sign.           **/ 
    
  }
  else if (binmultstr1[0] == '0' && binmultstr1[1] == 'b') {
    /** The first argument binar string start with the binar identifier prefix "0b". **/
    
    binmultstr1 += 2         ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/ 
                             
    change_argument_value1=1 ; /** Binar identifier detected without negativ sign.         **/                         
  }
  else if (binmultstr1[0] == '-') {
    /** The first argument binar string is negativ. **/
    
    is_1_negativ=true    ;   /** We set the negativ boolean value on true.                 **/     
  }
  
  
  if (binmultstr2[0] == '-' && binmultstr2[1] == '0' && binmultstr2[2] == 'b') {
    /** The second argument binar string is negativ and start with the binar identifier prefix "0b". **/
    
    binmultstr2[2]='-'       ;  /** We set the negativ sign to index 2.                    **/
    binmultstr2 += 2         ;  /** We increment the pointer to point on the negativ sign   
                                 * so that we get it at the string start.                  **/ 
    is_2_negativ=true        ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=2 ;  /** Binar identifier detected with negativ sign.           **/ 
    
  }
  else if (binmultstr2[0] == '0' && binmultstr2[1] == 'b') {
    /** The second argument binar string start with the binar identifier prefix "0b". **/
    
    binmultstr2 += 2         ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".             **/ 
    
    change_argument_value2=1 ;  /** Binar identifier detected without negativ sign.         **/                          
  }
  else if (binmultstr2[0] == '-') {
    /** The second argument binar string is negativ. **/
    
    is_2_negativ=true    ;   /** We set the negativ boolean value on true.                  **/     
  }
  
  
  if (strlen(binmultstr1) > 64 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binmultstr1) > 65 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multiplication function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(binmultstr2) > 63 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binmultstr2) > 64 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multiplication function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(binmultstr1,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the multiplication function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar string: in form [-][0b][01].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(binmultstr2,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the multiplication function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar string: in form [-][0b][01].") ;
    return NULL ;
  
    
  }
  
  
  if ( is_string_float(binmultstr1) ) {
    /** The given string is not an valid binar integer string, 
     *  but an binar float string.                                
     *  So we raise an ValueError exception and abort the multiplication function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar integer string: in form [-][0b][01].") ;
    return NULL ;
  }
  
  if ( is_string_float(binmultstr2) ) {
    /** The given string is not an valid binar integer string, 
     *  but an binar float string.                                
     *  So we raise an ValueError exception and abort the multiplication function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar integer string: in form [-][0b][01].") ;
    return NULL ;
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( bintoint(binmultstr1) > bintoint(binmultstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( bintoint(binmultstr1) < bintoint(binmultstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  
  retval=binmultbin(binmultstr1,binmultstr2) ; /** We perform the multiplication and store the result in retval.  **/   
  
  if (change_argument_value1 == 2) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binmultstr1 -= 2 ;
    binmultstr1[2]='b' ;
  }
  else if (change_argument_value1 == 1) {
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binmultstr1 -= 2 ;
  }
    
  if (change_argument_value2 == 2) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binmultstr2 -= 2 ;
    binmultstr2[2]='b' ;
  }
  else if (change_argument_value2 == 1) {
    /** We reset the pointer of the second given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    binmultstr2 -= 2 ;
  }  
  
  char string_to_return[128]              ;  /** We need an string to return it        **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.             **/
   
  sprintf(string_to_return,"%lli",retval) ;  /** Copy the result value into an string. **/  
  
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
     *  So we raise an OverflowError exception an abort the multiplication function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments product value to great for multiplication.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long long int to python.    **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}



static PyObject *
pyhobdcalc_bindivbin(PyObject *self, PyObject *args) {
  /** Python function wrapper for dividing two binar integer string and return the result as an float string. **/
  
  char *bindivstr1         ;  /** variable for converting an python string into an C string.      **/ 
  char *bindivstr2         ;  /** variable for converting an python string into an C string.      **/ 
  
  long double retval       ;  /** Variable for result computing.                                  **/
  
  _Bool is_1_negativ=false ;  /** Boolean value to check if the given first argument is negativ.  **/
  _Bool is_2_negativ=false ;  /** Boolean value to check if the given second argument is negativ. **/
  
  _Bool is_result_negativ=false ;  /** Boolean value to check if the result should be negativ.    **/
  
  int8_t change_argument_value1=0  ; /** Variable to check if the binar identifier "0b" is present
                                      * in the first given argument string.                       **/
  int8_t change_argument_value2=0  ; /** Variable to check if the binar identifier "0b" is present
                                      * in the second given argument string.                      **/
  
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
    
    change_argument_value1=2 ;  /** Binar identifier detected with negativ sign.           **/ 
    
  }
  else if (bindivstr1[0] == '0' && bindivstr1[1] == 'b') {
    /** The first argument binar string start with the binar identifier prefix "0b". **/
    
    bindivstr1 += 2          ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".            **/ 
    
    change_argument_value1=1 ;  /** Binar identifier detected without negativ sign.        **/ 
  }
  else if (bindivstr1[0] == '-') {
    /** The first argument binar string is negativ. **/
    
    is_1_negativ=true        ;  /** We set the negativ boolean value on true.              **/     
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
   
    change_argument_value2=1 ;  /** Binar identifier detected with negativ sign.           **/ 
  }
  else if (bindivstr2[0] == '-') {
    /** The second argument binar string is negativ. **/
    
    is_2_negativ=true        ;   /** We set the negativ boolean value on true.             **/     
  }
  
  
  if (strlen(bindivstr1) > 64 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(bindivstr1) > 65 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the division function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 1 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(bindivstr2) > 63 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  
  else if (strlen(bindivstr2) > 64 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the division function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string argument 2 length: 64 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(bindivstr1,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the division function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar string: in form [-][0b][01].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(bindivstr2,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the division function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar string: in form [-][0b][01].") ;
    return NULL ;
  
    
  }
  
  
  if ( is_string_float(bindivstr1) ) {
    /** The given string is not an valid binar integer string, 
     *  but an binar float string.                                
     *  So we raise an ValueError exception and abort the division function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an binar integer string: in form [-][0b][01].") ;
    return NULL ;
  }
  
  if ( is_string_float(bindivstr2) ) {
    /** The given string is not an valid binar integer string, 
     *  but an binar float string.                                
     *  So we raise an ValueError exception and abort the division function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an binar integer string: in form [-][0b][01].") ;
    return NULL ;
  }
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( bintoint(bindivstr1) > bintoint(bindivstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( bintoint(bindivstr1) < bintoint(bindivstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  
  retval=bindivbin(bindivstr1,bindivstr2) ;  /** We perform the division and store the result in retval.  **/
  
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
  
  
  char string_to_return[128]                 ;  /** We need an string to return it         **/
  memset(string_to_return,'\0',128)          ;  /** Setting all bits on '\0'.              **/
   
  sprintf(string_to_return,"%.15Lf",retval)  ;  /** Copy the result value into an string.  **/  
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.           **/ 
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The input string is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the division function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments quotient value to great for division.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The input string is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the division function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments quotient value to great for division.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string for module concision.                                    **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/

}
