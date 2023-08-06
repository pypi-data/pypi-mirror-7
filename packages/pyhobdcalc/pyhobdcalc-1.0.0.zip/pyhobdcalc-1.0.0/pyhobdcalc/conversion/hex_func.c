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
 * -) hextoint: Convert an hexadecimal string (who can represent an integer signed value) to an integer.
 * 
 * -) hexfloattofloat: Convert an hexadecimal string (who can represent an float signed value) to an float.
 * 
 * -) floattohexfloat: Convert an float string (who can represent an float signed value) to an hexadecimal float string.
 *   
 ***********************************************************************************************************************/

static PyObject *
pyhobdcalc_hextoint(PyObject *self, PyObject *args) {
  /** Python function wrapper for convert an hexadecimal integer string into an integer string. **/
  
  char *hexintstring     ;  /** Variable for converting an python string into an C string. **/ 
  long long int retval   ;  /** Variable for result computing.                             **/
  _Bool is_negativ=false ;  /** Boolean value to check if the given argument is negativ.   **/
  
  int8_t change_argument_value=0  ;  /** Variable to check if the hexadecimal identifier "0x" is present. **/ 
  
  if (!PyArg_ParseTuple(args, "s", &hexintstring)) {
    /** Failing to convert the given python string into an C string. **/
    
    return NULL;
  }
  
  
  if (hexintstring[0] == '-' && hexintstring[1] == '0' && hexintstring[2] == 'x') {
    /** The hexdecimal string is negativ and start with the hexdecimal identifier prefix "0x". **/
    
    hexintstring[2]='-'     ;  /** We set the negativ sign to index 2.                    **/
    hexintstring += 2       ;  /** We increment the pointer to point on the negativ sign  
                                 * so that we get it at the string start.                 **/ 
    is_negativ=true         ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value=2 ;  /** Hexadecimal identifier detected with negativ sign.       **/  
    
  }
  else if (hexintstring[0] == '0' && hexintstring[1] == 'x') {
    /** The hexdecimal string start with the hexdecimal identifier prefix "0x". **/
    
    hexintstring += 2       ;  /** We increment the pointer to point on the data begin 
                                 * to ignore the hexdecimal identifier prefix "0x".       **/ 
                                 
    change_argument_value=1 ;  /** Hexadecimal identifier detected without negativ sign.    **/                          
  }
  else if (hexintstring[0] == '-') {
    /** The hexdecimal string is negativ. **/
    
    is_negativ=true    ;   /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(hexintstring) > 15 && (! is_negativ) ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/  
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string length: 15 characters.") ;
    return NULL ; 
  }
  else if (strlen(hexintstring) > 16 && is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/  
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string length: 15 characters.") ;
    return NULL ; 
  }
  
  
  if (! is_string_as_base_an_valid_entry(hexintstring,16) ) { 
    /** The given string is not an valid hexadecimal string.                                
      * So we raise an ValueError exception and abort the conversion function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an hexal string: in form [-][0x][0-9A-Fa-f].") ;
    return NULL ;
  }
  
  
  if ( is_string_float(hexintstring) ) {
    /** The given string is not an valid hexadecimal integer string, 
     *  but an hexadecimal float string.                                
     *  So we raise an ValueError exception and abort the conversion function.             **/ 
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an hexal integer string: in form [-][0x][0-9A-Fa-f].") ;
  }
  
  retval=hextoint(hexintstring)           ;  /** We convert the hexadecimal string into an long long int. **/
  
  if (change_argument_value == 2) {
    /** We reset the pointer of the given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.           **/
      
    hexintstring -= 2 ;
    hexintstring[2]='x' ;
  
  }
  else if (change_argument_value == 1) {
    /** We reset the pointer of the given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.           **/
    
    hexintstring -= 2 ;
  
  }
  
  char string_to_return[128]              ;  /** We need an string to return it                           **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bytes on '\0'.                               **/
   
  sprintf(string_to_return,"%lli",retval) ;  /** Copy the result value into an string.                    **/ 
  
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
  
  /** We return the conversion result as an string for module concision.                                   **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}

static PyObject *
pyhobdcalc_hexfloattofloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for convert an hexadecimal float string into an float string. **/
  
  char *hexfloatstring   ;  /** Variable for converting an python string into an C string. **/ 
  long double retval     ;  /** Variable for result computing.                             **/
  _Bool is_negativ=false ;  /** Boolean value to check if the given argument is negativ.   **/
  
  int8_t change_argument_value=0  ; /** Variable to check if the hexadecimal identifier "0x" is present. **/ 
  
  if (!PyArg_ParseTuple(args, "s", &hexfloatstring)) {
    /** Failing to convert the given python string into an C string. **/
    
    return NULL;
  }
  
  if (hexfloatstring[0] == '-' && hexfloatstring[1] == '0' && hexfloatstring[2] == 'x') {
    /** The hexdecimal string is negativ and start with the hexdecimal identifier prefix "0x". **/
    
    hexfloatstring[2]='-'   ;  /** We set the negativ sign to index 2.                    **/
    hexfloatstring += 2     ;  /** We increment the pointer to point on the negativ sign  
                                 * so that we get it at the string start.                 **/ 
    is_negativ=true         ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value=2 ;  /** Hexadecimal identifier detected with negativ sign.       **/  
    
  }
  else if (hexfloatstring[0] == '0' && hexfloatstring[1] == 'x') {
    /** The hexdecimal string start with the hexdecimal identifier prefix "0x". **/
    
    hexfloatstring += 2     ;  /** We increment the pointer to point on the data begin 
                                 * to ignore the hexdecimal identifier prefix "0x".       **/ 
                             
    change_argument_value=1 ;  /** Hexadecimal identifier detected without negativ sign.    **/                           
  }  
  else if (hexfloatstring[0] == '-') {
    /** The hexdecimal string is negativ. **/
    
    is_negativ=true    ;   /** We set the negativ boolean value on true.              **/     
  }
  
  if (strlen(hexfloatstring) > 64 && (! is_negativ) ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/  
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string length: 64 characters.") ;
    return NULL ; 
  }
  else if (strlen(hexfloatstring) > 65 && is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/  
    
    PyErr_SetString(PyExc_OverflowError,"Maximal hexadecimal string length: 64 characters.") ;
    return NULL ; 
  }
  
  if (! is_string_as_base_an_valid_entry(hexfloatstring,16) ) { 
    /** The given string is not an valid hexadecimal string.                                
      * So we raise an ValueError exception and abort the conversion function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an hexadecimal string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f].") ;
    return NULL ;
  }
  
  if (! is_string_float(hexfloatstring) ) {
    /** The given string is not an valid hexdecimal float string, 
     *  but an hexdecimal integer string.                                
     *  So we raise an ValueError exception and abort the conversion function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an hexdecimal float string: in form [-][0x][0-9A-Fa-f].[0-9A-Fa-f].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the integer part of the string. **/
  
  if ((ptr_point=strchr(hexfloatstring,'.')) != NULL ) {
    
    if (hexfloatstring[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      hexfloatstring++ ;
      is_negativ=true  ;
    }
    
    if ((ptr_point-hexfloatstring) > 16) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    if (is_negativ) {
      /** We reset the pointer on data begin. **/
      
      hexfloatstring-- ;
    }
    
  }
  
  retval=hexfloattofloat(hexfloatstring)     ; /** We convert the hexadecimal string into an long double.  **/
   
  if (change_argument_value == 2) {
    /** We reset the pointer of the given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.           **/
    
    hexfloatstring -= 2 ;
    hexfloatstring[2]='x' ;
  }
  else if (change_argument_value == 1) {
    /** We reset the pointer of the given argument for giving it correctly back. 
      * In case the user want to reuse the variable given as argument.           **/
    
    hexfloatstring -= 2 ;
  }
   
  char string_to_return[128]                 ;  /** We need an string to return it                         **/
  memset(string_to_return,'\0',128)          ;  /** Setting all bytes on '\0'.                             **/
  
  sprintf(string_to_return,"%.15Lf",retval)  ;  /** Copy the result value into an string.                  **/ 
  
  strip_zero(string_to_return)               ;  /** Stripping the uneeded zeros.                           **/ 
  
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
pyhobdcalc_floattohexfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for convert an float string into an hexadecimal float string. **/
  
  char *float_to_hexfloat  ; /** Variable for converting an python string into an C string. **/ 
  _Bool is_negativ=false   ; /** Boolean value to check if the given argument is negativ.   **/
  
  
  if (!PyArg_ParseTuple(args, "s", &float_to_hexfloat)) {
    /** Failing to convert the given python string into an C string. **/
    
    return NULL;
  }
  
  
  
  if (float_to_hexfloat[0] == '-') {
    /** The hexdecimal string is negativ. **/
    
    is_negativ=true    ;   /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(float_to_hexfloat) > 128 && ! is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal float string length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(float_to_hexfloat) > 129 && is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal float string length: 128 characters.") ;
    return NULL ; 
  }
  
  
  if (! is_string_as_base_an_valid_entry(float_to_hexfloat,10) ) {
    /** The given string is not an valid hexdecimal string.                                
      * So we raise an ValueError exception and abort the conversion function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an string representing an float.") ;
    return NULL ;
  }
  
  
  if (! is_string_float(float_to_hexfloat) ) {
    /** The given string is not an valid hexdecimal float string, 
     *  but an hexdecimal integer string.                                
     *  So we raise an ValueError exception and abort the conversion function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an string representing an float.") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the integer part of the string. **/
  
  if ((ptr_point=strchr(float_to_hexfloat,'.')) != NULL ) {
    
    if (float_to_hexfloat[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      float_to_hexfloat++ ;
      is_negativ=true     ;
    }
    
    if ((ptr_point-float_to_hexfloat) > 19) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 19 digits.") ;
      return NULL ;
    }
    if (is_negativ) {
      /** We reset the pointer on data begin. **/
      
      float_to_hexfloat-- ;
    }
    
  }
  
  char *result_string=calloc(128,sizeof(char)) ; /** String to perform the conversion into an hexadecimal float string. **/
  
  /** This is the heart of the work we store the conversion result in result_string. **/
  floattohexfloat(strtold(float_to_hexfloat,NULL),result_string) ;
  
  char string_to_return[132]        ;  /** String to return.          **/ 
  memset(string_to_return,'\0',132) ;  /** Setting all bytes on '\0'. **/ 
  
  if (result_string[0] == '-') {
    /** The result is negativ we format the function output: **/
    
    char *tmp=calloc(129,sizeof(char)) ;  /** Hexadecimal string part for formatting. **/ 
    int c,cc ;
    
    for (c=1,cc=0 ; result_string[c] != '\0' ; c++, cc++) {
      tmp[cc]=result_string[c] ;  /** Temporary copy of the hexadecimal string without sign and identifier. **/ 
    }
    
    sprintf(string_to_return,"-0x%s",tmp) ; /** We format the function output. **/
    
    free(tmp) ;
  }
  else {
    /** We format the function output. **/
    
    sprintf(string_to_return,"0x%s",result_string) ;
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
  
  /** We return the conversion result as an hexadecimal float string.                                      **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}
