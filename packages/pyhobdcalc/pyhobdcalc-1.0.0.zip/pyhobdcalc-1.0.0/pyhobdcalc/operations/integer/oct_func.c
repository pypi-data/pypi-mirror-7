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
 * This file contains python wrapper functions for octal integer computing utilities:
 * 
 * -) octaddoct: add two octal string with limitation of the C type long long int, 
 *               so you can compute with signed values.
 * 
 * -) octsuboct: substract two octal string with limitation of the C type long long int, 
 *               so you can compute with signed values.
 * 
 * -) octmultoct: multiply two octal string with limitation of the C type long long int, 
 *                so you can compute with signed values.
 * 
 * -) octdivoct: substract two octal string with limitation of the C type long long int, 
 *               for the integer part of the octal strings which return an string 
 *               with maximum 15 digits precision corrresponding to the C type double.
 * 
 *****************************************************************************************************************/

static PyObject *
pyhobdcalc_octaddoct(PyObject *self, PyObject *args) {
  /** Python function wrapper for adding two octal integer string and return the result as an integer string. **/
  
  char *octaddstr1       ;              /** variable for converting an python string into an C string.       **/
  char *octaddstr2       ;              /** variable for converting an python string into an C string.       **/
  
  long long int retval   ;              /** Variable for result computing.                                   **/
  
  _Bool is_1_negativ=false ;            /** Boolean value to check if the given first argument is negativ.   **/
  _Bool is_2_negativ=false ;            /** Boolean value to check if the given second argument is negativ.  **/
  
  _Bool is_result_negativ=false ;       /** Boolean value to check if the result should be negativ.          **/ 
  
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
  
  
  if (strlen(octaddstr1) > 24 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octaddstr1) > 25 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(octaddstr2) > 24 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octaddstr2) > 25 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the addition function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(octaddstr1,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the addition function.  **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal string: in form [-][0][0-7].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(octaddstr2,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the addition function.  **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal string: in form [-][0][0-7].") ;
    return NULL ;
  
    
  }
  
  
  if ( is_string_float(octaddstr1) ) {
    /** The given string is not an valid octal integer string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the addition function.  **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal integer string: in form [-][0][0-7].") ;
    return NULL ;
  }
  
  if ( is_string_float(octaddstr2) ) {
    /** The given string is not an valid octal integer string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the addition function.  **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal integer string: in form [-][0][0-7].") ;
    return NULL ;
  }
  
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( octtoint(octaddstr1) > octtoint(octaddstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=false ;
    if ( llabs(octtoint(octaddstr2)) > llabs(octtoint(octaddstr1)) ) {
      is_result_negativ=true ;
    }
  }
  else if ( ( octtoint(octaddstr1) < octtoint(octaddstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  
  retval=octaddoct(octaddstr1,octaddstr2) ;  /** We perform the addition and store the result in retval.  **/   
  
  
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
    
    
  char string_to_return[128]              ;  /** We need an string to return it        **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.             **/
   
  sprintf(string_to_return,"%lli",retval) ;  /** Copy the result value into an string. **/  
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The addition result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the operation function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments summe value to great for operation.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The addition result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the operation function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments summe value to great for operation.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long long int to python.    **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}


static PyObject *
pyhobdcalc_octsuboct(PyObject *self, PyObject *args) {
  /** Python function wrapper for substracting two octal integer string and return the result as an integer string. **/
  
  char *octsubstr1       ;  /** variable for converting an python string into an C string.               **/
  char *octsubstr2       ;  /** variable for converting an python string into an C string.               **/
  
  long long int retval   ;  /** Variable for result computing.                                           **/
  
  _Bool is_1_negativ=false      ;  /** Boolean value to check if the given first argument is negativ.    **/
  _Bool is_2_negativ=false      ;  /** Boolean value to check if the given second argument is negativ.   **/
  
  _Bool is_result_negativ=false ;  /** Boolean value to check if the result should be negativ.           **/
  
  _Bool change_argument_value1=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the first given argument string.                         **/
  _Bool change_argument_value2=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the first given argument string.                         **/
  
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
    /** The octal string start with the octal identifier prefix "0". **/
    
    octsubstr1++ ; /** We increment the pointer to point on the data begin 
                       * to ignore the octal identifier prefix "0".           **/ 
                       
    change_argument_value1=true ;                   
  }
  else if (octsubstr1[0] == '-') {
    /** The octal string is negativ. **/
    
    is_1_negativ=true ; /** We set the negativ boolean value on true.         **/ 
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
    
    is_2_negativ=true ; /** We set the negativ boolean value on true.           **/ 
  }
  
  
  
  if (strlen(octsubstr1) > 24 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octsubstr1) > 25 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(octsubstr2) > 24 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octsubstr2) > 25 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the substraction function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(octsubstr1,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the substraction function.   **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal string: in form [-][0][0-7].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(octsubstr2,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the substraction function.   **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal string: in form [-][0][0-7].") ;
    return NULL ;
  
    
  }
  
  
  if ( is_string_float(octsubstr1) ) {
    /** The given string is not an valid octal integer string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the substraction function.   **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal integer string: in form [-][0][0-7].") ;
    return NULL ;
  }
  
  if ( is_string_float(octsubstr2) ) {
    /** The given string is not an valid octal integer string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the substraction function.   **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal integer string: in form [-][0][0-7].") ;
    return NULL ;
  }
  
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( octtoint(octsubstr1) > octtoint(octsubstr2) ) && (! is_1_negativ) &&  is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( ( octtoint(octsubstr1) > octtoint(octsubstr2) ) && is_1_negativ &&  is_2_negativ  ) {
    is_result_negativ=true ;
  }
  else if ( ( octtoint(octsubstr1) > octtoint(octsubstr2) ) && (! is_1_negativ) &&  (! is_2_negativ)  ) {
    is_result_negativ=false ;
  }
  else if ( ( octtoint(octsubstr1) < octtoint(octsubstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( octtoint(octsubstr1) < octtoint(octsubstr2) ) && is_1_negativ &&  is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( ( octtoint(octsubstr1) < octtoint(octsubstr2) ) && (! is_1_negativ) &&  (! is_2_negativ)  ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  
  retval=octsuboct(octsubstr1,octsubstr2) ; /** We perform the substraction and store the result in retval.  **/      
  
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
  
  char string_to_return[128]              ;  /** We need an string to return it        **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.             **/
   
  sprintf(string_to_return,"%lli",retval) ;  /** Copy the result value into an string. **/  
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The substraction result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the operation function.      **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments substract value to great for operation.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The substraction result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the operation function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments substract value to great for operation.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long long int to python.     **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}



static PyObject *
pyhobdcalc_octmultoct(PyObject *self, PyObject *args) {
  /** Python function wrapper for multiply two octal integer string and return the result as an integer string. **/
  
  char *octmultstr1      ;  /** variable for converting an python string into an C string.               **/
  char *octmultstr2      ;  /** variable for converting an python string into an C string.               **/
  
  long long int retval   ;  /** Variable for result computing.                                           **/
  
  _Bool is_1_negativ=false      ;  /** Boolean value to check if the given first argument is negativ.    **/
  _Bool is_2_negativ=false      ;  /** Boolean value to check if the given second argument is negativ.   **/
  
  _Bool is_result_negativ=false ;  /** Boolean value to check if the result should be negativ.           **/
  
  _Bool change_argument_value1=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the first given argument string.                         **/
  _Bool change_argument_value2=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the second given argument string.                        **/
  
  if (!PyArg_ParseTuple(args, "ss", &octmultstr1,&octmultstr2)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  if (octmultstr1[0] == '-' && octmultstr1[1] == '0') {
    /** The first argument octal string is negativ and start with the octal identifier prefix "0". **/
    
    octmultstr1[1]='-'          ;  /** We set the negativ sign to index 1.                    **/
    octmultstr1++               ;  /** We increment the pointer to point on the negativ sign  
                                    * so that we get it at the string start.                  **/ 
    is_1_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value1=true ;  /** Octal identifier detected with negativ sign.           **/    
    
  }
  else if (octmultstr1[0] == '0') {
    /** The first argument octal string start with the octal identifier prefix "0". **/
    
    octmultstr1++               ;  /** We increment the pointer to point on the data begin 
                                     * to ignore the octal identifier prefix "0".             **/ 
                       
    change_argument_value1=true ;  /** Octal identifier detected without negativ sign.        **/                       
  }
  else if (octmultstr1[0] == '-') {
    /** The first argument octal string is negativ. **/
    
    is_1_negativ=true           ; /** We set the negativ boolean value on true.               **/ 
  }
  
  
  if (octmultstr2[0] == '-' && octmultstr2[1] == '0') {
    /** The second argument octal string is negativ and start with the octal identifier prefix "0". **/
    
    octmultstr2[1]='-'          ;  /** We set the negativ sign to index 1.                    **/
    octmultstr2++               ;  /** We increment the pointer to point on the negativ sign  
                                     * so that we get it at the string start.                 **/ 
    is_2_negativ=true           ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value2=true ;  /** Octal identifier detected with negativ sign.           **/     
    
  }
  else if (octmultstr2[0] == '0') {
    /** The second argument octal string start with the octal identifier prefix "0". **/
    
    octmultstr2++               ;  /** We increment the pointer to point on the data begin 
                                     * to ignore the octal identifier prefix "0".             **/ 
    
    change_argument_value2=true ;  /** Octal identifier detected without negativ sign.        **/ 
  }
  else if (octmultstr2[0] == '-') {
    /** The second argument octal string is negativ. **/
    
    is_2_negativ=true           ; /** We set the negativ boolean value on true.               **/ 
  }
  
  
  if (strlen(octmultstr1) > 24 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multiplication function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octmultstr1) > 25 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multiplication function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(octmultstr2) > 24 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multiplication function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octmultstr2) > 25 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the multiplication function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(octmultstr1,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the multiplication function.   **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal string: in form [-][0][0-7].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(octmultstr2,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the multiplication function.   **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal string: in form [-][0][0-7].") ;
    return NULL ;
  
    
  }
  
  
  if ( is_string_float(octmultstr1) ) {
    /** The given string is not an valid octal integer string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the multiplication function.   **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal integer string: in form [-][0][0-7].") ;
    return NULL ;
  }
  
  if ( is_string_float(octmultstr2) ) {
    /** The given string is not an valid octal integer string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the multiplication function.   **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal integer string: in form [-][0][0-7].") ;
    return NULL ;
  }
  
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( octtoint(octmultstr1) > octtoint(octmultstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( octtoint(octmultstr1) < octtoint(octmultstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=true ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  retval=octmultoct(octmultstr1,octmultstr2) ;  /** We perform the division and store the result in retval.  **/  
  
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
  
  char string_to_return[128]              ;  /** We need an string to return it        **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.             **/
   
  sprintf(string_to_return,"%lli",retval) ;  /** Copy the result value into an string. **/  
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The multiplication result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the operation function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments product value to great for operation.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The multiplication result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the operation function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments product value to great for operation.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long long int to python.     **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}


static PyObject *
pyhobdcalc_octdivoct(PyObject *self, PyObject *args) {
  /** Python function wrapper for dividing two octal integer string and return the result as an float string. **/
  
  char *octdivstr1    ;  /** variable for converting an python string into an C string.                **/
  char *octdivstr2    ;  /** variable for converting an python string into an C string.                **/
  
  long double retval  ;  /** Variable for result computing.                                            **/
  
  _Bool is_1_negativ=false      ;  /** Boolean value to check if the given first argument is negativ.  **/
  _Bool is_2_negativ=false      ;  /** Boolean value to check if the given second argument is negativ. **/
  
  _Bool is_result_negativ=false ;  /** Boolean value to check if the result should be negativ.         **/
  
  _Bool change_argument_value1=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the first given argument string.                       **/
  _Bool change_argument_value2=false  ;  /** Variable to check if the octal identifier "0" is present
                                           * in the second given argument string.                      **/
  
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
    /** The first argument octal string start with the octal identifier prefix "0". **/
    
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
                                    * so that we get it at the string start.                  **/ 
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
  
  
  
  if (strlen(octdivstr1) > 24 && ! is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the division function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octdivstr1) > 25 && is_1_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the division function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 1 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  
  if (strlen(octdivstr2) > 24 && ! is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the division function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 21 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(octdivstr2) > 25 && is_2_negativ ) {
    /** The string is too length for the operation peforming.                        
      * So we raise an OverflowError exception an abort the division function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string argument 2 length: 12 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(octdivstr1,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the division function.   **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal string: in form [-][0][0-7].") ;
    return NULL ;
  
    
  }
  
  if (! is_string_as_base_an_valid_entry(octdivstr2,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the division function.   **/
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal string: in form [-][0][0-7].") ;
    return NULL ;
  
    
  }
  
  
  if ( is_string_float(octdivstr1) ) {
    /** The given string is not an valid octal integer string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the division function.   **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 1 must be an octal integer string: in form [-][0][0-7].") ;
    return NULL ;
  }
  
  if ( is_string_float(octdivstr2) ) {
    /** The given string is not an valid octal integer string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the division function.   **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument 2 must be an octal integer string: in form [-][0][0-7].") ;
    return NULL ;
  }
  
  
  /** We check if the result should be negativ or positiv. In relationship of the signs and values from the arguments. **/
  if ( ( octtoint(octdivstr1) > octtoint(octdivstr2) ) && (! is_1_negativ) && ( is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( ( octtoint(octdivstr1) < octtoint(octdivstr2) ) && is_1_negativ && (! is_2_negativ) ) {
    is_result_negativ=true ;
  }
  else if ( is_1_negativ && is_2_negativ ) {
    is_result_negativ=false ;
  }
  else if ( (! is_1_negativ) && (! is_2_negativ) ) {
    is_result_negativ=false ;
  }
  
  
  retval=octdivoct(octdivstr1,octdivstr2) ;  /** We perform the division and store the result in retval.  **/    
  
  
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
  
  char string_to_return[128]                 ;  /** We need an string to return it        **/
  memset(string_to_return,'\0',128)          ;  /** Setting all bits on '\0'.             **/
   
  sprintf(string_to_return,"%.15Lf",retval)  ;  /** Copy the result value into an string. **/
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.          **/ 
  
  if ( (string_to_return[0] == '-') && ! is_result_negativ ) {
    /** The division result is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the operation function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments quotient value to great for operation.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_result_negativ ) {
    /** The division result is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the operation function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: arguments quotient value to great for operation.") ;
    return NULL ;
  }
  
  /** We return the operation result as an string because we cannot return an long double to python.       **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}
