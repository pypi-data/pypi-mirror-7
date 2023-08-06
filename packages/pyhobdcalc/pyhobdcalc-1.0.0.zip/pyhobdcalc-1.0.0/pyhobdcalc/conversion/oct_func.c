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
 * This file contains python wrapper functions for conversion utilities:
 * 
 * -) octtoint: Convert an octal string (who can represent an integer signed value) to an integer.
 * 
 * -) octfloattofloat: Convert an octal string (who can represent an float signed value) to an float.
 * 
 * -) floattooctfloat: Convert an float string (who can represent an float signed value) to an octal float string.
 *   
 *****************************************************************************************************************/

static PyObject *
pyhobdcalc_octtoint(PyObject *self, PyObject *args) {
  /** Python function wrapper for convert an octal integer string into an integer string. **/
  
  char *octintstring     ;  /** Variable for converting an python string into an C string. **/ 
  long long int retval   ;  /** Variable for result computing.                             **/
  _Bool is_negativ=false ;  /** Boolean value to check if the given argument is negativ.   **/
  
  _Bool change_argument_value=false  ; /** Variable to check if the octal identifier "0" is present. **/
  
  if (!PyArg_ParseTuple(args, "s", &octintstring)) {
    /** Failing to convert the given python string into an C string. **/
    
    return NULL;
  }
  
  
  if (octintstring[0] == '-' && octintstring[1] == '0') {
    /** The octal string is negativ and start with the octal identifier prefix "0".         **/
    octintstring[1]='-'        ; /** We set the negativ sign to index 1.                    **/
    octintstring++             ; /** We increment the pointer to point on the negativ sign  
                                   * so that we get it at the string start.                 **/ 
    is_negativ=true            ; /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value=true ; /** Octal identifier detected.                             **/  
  }
  else if (octintstring[0] == '0') {
    /** The octal string start with the octal identifier prefix "0". **/
    
    octintstring++ ; /** We increment the pointer to point on the data begin 
                       * to ignore the octal identifier prefix "0".           **/ 
                       
    change_argument_value=true ; /** Octal identifier detected.               **/                     
  }
  else if (octintstring[0] == '-') {
    /** The octal string is negativ. **/
    
    is_negativ=true ; /** We set the negativ boolean value on true.           **/ 
  }
  
  
  if (strlen(octintstring) > 21 && (! is_negativ) ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/   
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string length: 21 characters.") ;
    return NULL ; 
  }
  else if (strlen(octintstring) > 22 && is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/   
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string length: 21 characters.") ;
    return NULL ; 
  }
  
  
  if (! is_string_as_base_an_valid_entry(octintstring,8) ) { 
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the conversion function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an octal string: in form [-][0][0-7].") ;
    return NULL ;
  }
  
  
  if ( is_string_float(octintstring) ) {
    /** The given string is not an valid octal integer string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the conversion function.             **/ 
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an octal integer string: in form [-][0][0-7].") ;
    return NULL ;
  }
  
  retval=octtoint(octintstring)            ; /** We convert the octal string into an long long int. **/
  
  if (change_argument_value && is_negativ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octintstring--      ; 
    octintstring[1]='0' ; 
  }
  else if (change_argument_value && (! is_negativ) ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octintstring--      ;
  }
  
  char string_to_return[128]               ;  /** We need an string to return it                    **/
  memset(string_to_return,'\0',128)        ;  /** Setting all bytes on '\0'.                        **/
  
  sprintf(string_to_return,"%lli",retval)  ;  /** Copy the result value into an string.             **/ 
  
  if ( (string_to_return[0] == '-') && ( ! is_negativ) ) {
    /** The input string is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the conversion function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: input string value to great for conversion.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && ( is_negativ) ) {
    /** The input string is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the conversion function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: input string value to great for conversion.") ;
    return NULL ;
  }
  
  /** We return the conversion result as an string for module concision.                                   **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}

static PyObject *
pyhobdcalc_octfloattofloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for convert an octal float string into an float string. **/
  
  char *octfloatstring   ;  /** Variable for converting an python string into an C string. **/ 
  long double retval     ;  /** Variable for result computing.                             **/
  _Bool is_negativ=false ;  /** Boolean value to check if the given argument is negativ.   **/
  
  _Bool change_argument_value=false  ;  /** Variable to check if the octal identifier "0" is present. **/
  
  if (!PyArg_ParseTuple(args, "s", &octfloatstring)) {
    /** Failing to convert the given python string into an C string. **/
    
    return NULL;
  }
  
  
  if (octfloatstring[0] == '-' && octfloatstring[1] == '0') {
    /** The octal string is negativ and start with the octal identifier prefix "0".          **/
    octfloatstring[1]='-'      ;  /** We set the negativ sign to index 1.                    **/
    octfloatstring++           ;  /** We increment the pointer to point on the negativ sign  
                                    * so that we get it at the string start.                 **/ 
    is_negativ=true            ;  /** We set the negativ boolean value on true.              **/
    
    change_argument_value=true ;  /** Octal identifier detected.                             **/
  }
  
  if (octfloatstring[0] == '0') {
    /** The octal string start with the octal identifier prefix "0". **/
    
    octfloatstring++ ; /** We increment the pointer to point on the data begin 
                       * to ignore the octal identifier prefix "0".           **/ 
    
    change_argument_value=true ; 
  }
  else if (octfloatstring[0] == '-') {
    /** The octal string is negativ. **/
    
    is_negativ=true ; /** We set the negativ boolean value on true.           **/ 
  }
    
  if (strlen(octfloatstring) > 96 && (! is_negativ) ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/   
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string length: 96 characters.") ;
    return NULL ; 
  }
  else if (strlen(octfloatstring) > 97 && is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/   
    
    PyErr_SetString(PyExc_OverflowError,"Maximal octal string length: 96 characters.") ;
    return NULL ; 
  }
  
  if (! is_string_as_base_an_valid_entry(octfloatstring,8) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the conversion function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an octal string: in form [-][0][0-7][.][0-7].") ;
    return NULL ;
  }
  
  if (! is_string_float(octfloatstring) ) {
    /** The given string is not an valid octal float string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the conversion function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an octal float string: in form [-][0b][01][.][01].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the integer part of the string. **/
  
  if ((ptr_point=strchr(octfloatstring,'.')) != NULL ) {
    
    if (octfloatstring[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      octfloatstring++ ;
      is_negativ=true ;
    }
    
    if ((ptr_point-octfloatstring) > 24) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    if (is_negativ) {
      /** We reset the pointer on data begin. **/
      
      octfloatstring-- ;
    }
    
  }

  
  retval=octfloattofloat(octfloatstring)    ;  /** We convert the octal string into an long double.   **/
  
  if (change_argument_value && is_negativ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octfloatstring--      ; 
    octfloatstring[1]='0' ; 
  }
  else if (change_argument_value && (! is_negativ) ) { 
    /** We reset the pointer of the first given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.                 **/
    
    octfloatstring--      ;
  }
   
  char string_to_return[128]                 ;  /** We need an string to return it                    **/
  memset(string_to_return,'\0',128)          ;  /** Setting all bytes on '\0'.                        **/
  
  sprintf(string_to_return,"%.15Lf",retval)  ;  /** Copy the result value into an string.             **/ 
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.                      **/ 
  
  if ( (string_to_return[0] == '-') && ! is_negativ ) {
    /** The input string is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the conversion function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: input string value to great for conversion.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_negativ ) {
    /** The input string is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the conversion function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: input string value to great for conversion.") ;
    return NULL ;
  }
  
  /** We return the conversion result as an string because we cannot return an long double to python.      **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/ 
}

static PyObject *
pyhobdcalc_floattooctfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for convert an float string into an octal float string. **/
  
  char *float_to_octfloat ;  /** Variable for converting an python string into an C string. **/  
  _Bool is_negativ=false  ;  /** Boolean value to check if the given argument is negativ.   **/
  
  
  if (!PyArg_ParseTuple(args, "s", &float_to_octfloat)) {
    /** Failing to convert the given python string into an C string. **/
    
    return NULL;
  }
  
  
  
  if (float_to_octfloat[0] == '-') {
    /** The octal string is negativ. **/
    
    is_negativ=true    ;   /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(float_to_octfloat) > 128 && ! is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal float string length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(float_to_octfloat) > 129 && is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal float string length: 128 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(float_to_octfloat,10) ) {
    /** The given string is not an valid octal string.                                
      * So we raise an ValueError exception and abort the conversion function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an string representing an float.") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(float_to_octfloat) ) {
    /** The given string is not an valid octal integer string, 
     *  but an octal float string.                                
     *  So we raise an ValueError exception and abort the conversion function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an string representing an float.") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the integer part of the string. **/
  
  if ((ptr_point=strchr(float_to_octfloat,'.')) != NULL ) {
    
    if (float_to_octfloat[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      float_to_octfloat++ ;
      is_negativ=true ;
    }
    
    if ((ptr_point-float_to_octfloat) > 19) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 19 digits.") ;
      return NULL ;
    }
    if (is_negativ) {
      /** We reset the pointer on data begin. **/
      
      float_to_octfloat-- ;
    }
    
  }
  
  char *result_string=calloc(128,sizeof(char)) ; /** String to perform the conversion into an Octal float string. **/
  
  /** This is the heart of the work we store the conversion result in result_string. **/
  floattooctfloat(strtold(float_to_octfloat,NULL),result_string) ;
  
  char string_to_return[132]        ; /** String to return.          **/ 
  memset(string_to_return,'\0',132) ; /** Setting all bytes on '\0'. **/ 
  
  if (result_string[0] == '-') {
    /** The result is negativ we format the function output: **/
    
    char *tmp=calloc(129,sizeof(char)) ; /** Octal string part for formatting. **/ 
    int c,cc ;
    
    for (c=1,cc=0 ; result_string[c] != '\0' ; c++, cc++) {
      tmp[cc]=result_string[c] ; /** Temporary copy of the hexadecimal string without sign and identifier. **/ 
    }
    
    sprintf(string_to_return,"-0%s",tmp) ; /** We format the function output. **/
    
    free(tmp) ;
  }
  else {
    /** We format the function output. **/
    
    sprintf(string_to_return,"0%s",result_string) ;
  }
      
  free(result_string) ;
  
  if ( (string_to_return[0] == '-') && ! is_negativ ) {
    /** The input string is positiv and the result string is negativ.
     *  This come from an value overflow.
     *  So we raise an Overflow exception an abort the conversion function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: input string value to great for conversion.") ;
    return NULL ;
  }
  else if ( (! string_to_return[0] == '-') && is_negativ ) {
    /** The input string is negativ and the result string is positiv.
     *  This come from an value overflow.
     *  So we raise an OverflowError exception an abort the conversion function. **/
    
    PyErr_SetString(PyExc_OverflowError,"Value overflow: input string value to great for conversion.") ;
    return NULL ;
  }
  
  /** We return the conversion result as an octal float string.                                            **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}
