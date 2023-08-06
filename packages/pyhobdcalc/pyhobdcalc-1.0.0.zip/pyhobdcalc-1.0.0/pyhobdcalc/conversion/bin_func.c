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
 * -) bintoint: Convert an binar string (who can represent an integer signed value) to an integer.
 * 
 * -) binfloattofloat: Convert an binar string (who can represent an float signed value) to an float.
 * 
 * -) floattobinfloat: Convert an float string (who can represent an float signed value) to an binar float string.
 *   
 *****************************************************************************************************************/

static PyObject *
pyhobdcalc_bintoint(PyObject *self, PyObject *args) {
  /** Python function wrapper for convert an binar integer string into an integer string. **/
  
  char *binintstring     ;  /** variable for converting an python string into an C string. **/ 
  long long int retval   ;  /** Variable for result computing.                             **/
  _Bool is_negativ=false ;  /** Boolean value to check if the given argument is negativ.   **/
  
  int8_t change_argument_value=0  ; /** Variable to check if the binar identifier "0b" is present. **/ 
  
  if (!PyArg_ParseTuple(args, "s", &binintstring)) {
    /** Failing to convert the given python string into an C string. **/
      
    return NULL;
  }
  
  
  if (binintstring[0] == '-' && binintstring[1] == '0' && binintstring[2] == 'b') {
    /** The binar string is negativ and start with the binar identifier prefix "0b". **/
    
    binintstring[2]='-'     ;  /** We set the negativ sign to index 2.                    **/
    binintstring += 2       ;  /** We increment the pointer to point on the negativ sign  
                                 * so that we get it at the string start.                 **/ 
    is_negativ=true         ;  /** We set the negativ boolean value on true.              **/ 
    
    change_argument_value=2 ;  /** Binar identifier detected with negativ sign.           **/ 
    
  }
  else if (binintstring[0] == '0' && binintstring[1] == 'b') {
    /** The binar string start with the binar identifier prefix "0b". **/
    
    binintstring += 2       ;  /** We increment the pointer to point on the data begin 
                                 * to ignore the binar identifier prefix "0b".            **/ 
                            
    change_argument_value=1 ;  /** Binar identifier detected without negativ sign.        **/                        
  }
  else if (binintstring[0] == '-') {
    /** The binar string is negativ. **/
    
    is_negativ=true    ;   /** We set the negativ boolean value on true.              **/     
  }
  
  
  if (strlen(binintstring) > 63 && ! is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string length: 63 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(binintstring) > 64 && is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string length: 63 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(binintstring,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the conversion function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an binar string: in form [-][0b][01].") ;
    return NULL ;
  
    
  }
  
  
  if ( is_string_float(binintstring) ) {
    /** The given string is not an valid binar integer string, 
     *  but an binar float string.                                
     *  So we raise an ValueError exception and abort the conversion function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an binar integer string: in form [-][0b][01].") ;
    return NULL ;
  }
  
  retval=bintoint(binintstring)           ;  /** We convert the binar string into an long long int. **/
  
  if (change_argument_value == 2) {
    /** We reset the pointer of the given argument for giving it correctly back. 
        * In case the user want to reuse the variable given as argument.           **/
    
    binintstring -= 2 ;
    binintstring[2]='b' ;
      
  }
  else if (change_argument_value == 1) {
    /** We reset the pointer of the given argument for giving it correctly back. 
        * In case the user want to reuse the variable given as argument.           **/
    
    binintstring -= 2 ;
  }
  
  char string_to_return[128]              ;  /** We need an string to return it                     **/
  memset(string_to_return,'\0',128)       ;  /** Setting all bits on '\0'.                         **/
   
  sprintf(string_to_return,"%lli",retval) ;  /** Copy the result value into an string.              **/  
  
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
pyhobdcalc_binfloattofloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for convert an binar float string into an float string. **/
  
  char *binfloatstring   ;  /** Variable for converting an python string into an C string. **/ 
  long double retval     ;  /** Variable for result computing.                             **/
  _Bool is_negativ=false ;  /** Boolean value to check if the given argument is negativ.   **/
  
  int8_t change_argument_value=0  ;  /** Variable to check if the binar identifier "0b" is present. **/ 
  
  if (!PyArg_ParseTuple(args, "s", &binfloatstring)) {
    /** Failing to convert the given python string into an C string. **/
    
    return NULL;
  }
  
  
  if (binfloatstring[0] == '-' && binfloatstring[1] == '0' && binfloatstring[2] == 'b') {
    /** The binar string is negativ and start with the binar identifier prefix "0b". **/
    
    binfloatstring[2]='-'   ;  /** We set the negativ sign to index 2.                    **/
    binfloatstring += 2     ;  /** We increment the pointer to point on the negativ sign  
                                   so that we get it at the string start.                 **/ 
    is_negativ=true         ;  /** We set the negativ boolean value on true.              **/ 
     
    change_argument_value=2 ;  /** Binar identifier detected with negativ sign.           **/ 
  }
  else if (binfloatstring[0] == '0' && binfloatstring[1] == 'b') {
    /** The binar string start with the binar identifier prefix "0b". **/
    
    binfloatstring += 2      ;  /** We increment the pointer to point on the data begin 
                                  * to ignore the binar identifier prefix "0b".              **/
                                  
    change_argument_value=1 ;   /** Binar identifier detected without negativ sign.          **/                       
  }
  else if (binfloatstring[0] == '-') {
    /** The binar string is negativ. **/
    
    is_negativ=true ; /** We set the negativ boolean value on true.                    **/  
  }
  
  
  if (strlen(binfloatstring) > 128 && (! is_negativ) ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string length: 128 characters.") ;
    return NULL ; 
  }
  else if (strlen(binfloatstring) > 129 && is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/        
    
    PyErr_SetString(PyExc_OverflowError,"Maximal binar string length: 128 characters.") ;
    return NULL ; 
  }
  
  
  if (! is_string_as_base_an_valid_entry(binfloatstring,2) ) {
    /** The given string is not an valid binar string.                                
      * So we raise an ValueError exception and abort the conversion function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an binar string: in form [-][0b][01][.][01].") ;
    return NULL ;
  }
  
  if (! is_string_float(binfloatstring) ) {
    /** The given string is not an valid binar float string, 
     *  but an binar integer string.                                
     *  So we raise an ValueError exception and abort the conversion function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an binar float string: in form [-][0b][01][.][01].") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the float part of the string. **/
  
  if ((ptr_point=strchr(binfloatstring,'.')) != NULL ) {
    
    if (binfloatstring[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for float part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      binfloatstring++ ;
      is_negativ=true  ;
    }
    
    if ((ptr_point-binfloatstring) > 64) {
      /** The float part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_OverflowError,"Integer part maximal value must be 8 bytes length.") ;
      return NULL ;
    }
    
    if (is_negativ) {
      /** We reset the pointer on data begin. **/
      
      binfloatstring-- ;
    }
    
  }
  
  
  retval=binfloattofloat(binfloatstring)     ;  /** We convert the binar string into an long double.  **/
  
  if (change_argument_value == 2) {
      /** We reset the pointer of the given argument for giving it correctly back. 
        * In case the user want to reuse the variable given as argument.           **/
      
      binfloatstring -= 2 ;
      binfloatstring[2]='b' ;
  }
  else if (change_argument_value == 1) {
      /** We reset the pointer of the given argument for giving it correctly back. 
        * In case the user want to reuse the variable given as argument.           **/
      
      binfloatstring -= 2 ;
  }
  
  char string_to_return[128]                 ;  /** We need an string to return it                    **/
  memset(string_to_return,'\0',128)          ;  /** Setting all bits on '\0'.                        **/
  
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
pyhobdcalc_floattobinfloat(PyObject *self, PyObject *args) {
  /** Python function wrapper for convert an float string into an binar float string. **/
  
  char *float_to_binfloat    ; /** Variable for converting an python string into an C string. **/ 
  _Bool is_negativ=false     ; /** Boolean value to check if the given argument is negativ.   **/
  
  
  if (!PyArg_ParseTuple(args, "s", &float_to_binfloat)) {
    return NULL;
  }
  
  
  
  if (float_to_binfloat[0] == '-') {
    /** The binar string is negativ. **/
    
    is_negativ=true    ;   /** We set the negativ boolean value on true. **/     
  }
  
  
  if (strlen(float_to_binfloat) > 128 && ! is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the function. **/ 
    
    PyErr_SetString(PyExc_OverflowError,"Maximal float string length: 128 characters.") ;
    return NULL ; 
  
    
  }
  else if (strlen(float_to_binfloat) > 129 && is_negativ ) {
    /** The string is too length for the conversion peforming.                        
      * So we raise an OverflowError exception an abort the conversion function. **/                     
    
    PyErr_SetString(PyExc_OverflowError,"Maximal float string length: 128 characters.") ;
    return NULL ; 
  
    
  }
  
  
  if (! is_string_as_base_an_valid_entry(float_to_binfloat,10) ) {
    /** The given string is not an valid decimal string.                                
      * So we raise an ValueError exception and abort the conversion function. **/
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an string representing an float.") ;
    return NULL ;
  
    
  }
  
  
  if (! is_string_float(float_to_binfloat) ) {
    /** The given string is not an valid decimal float string, 
     *  but an integer string.                                
     *  So we raise an ValueError exception and abort the conversion function.             **/  
    
    PyErr_SetString(PyExc_ValueError,"Argument must be an string representing an float.") ;
    return NULL ;
  }
  
  char *ptr_point ;  /** Pointer for checking the length of the integer part of the string. **/
  
  if ((ptr_point=strchr(float_to_binfloat,'.')) != NULL ) {
    
    if (float_to_binfloat[0] == '-') {
      /** The given argument is negativ, 
       *  we temporary increment the pionter for integer part length checking. 
       *  And we set the negativ boolean value on true.                          **/
      
      float_to_binfloat++ ;
      is_negativ=true ;
    }
    
    if ((ptr_point-float_to_binfloat) > 19) {
      /** The integer part is to length for conversion performing.
       *  So we raise an ValueError exception and abort the conversion function. **/
      
      PyErr_SetString(PyExc_ValueError,"Integer part maximal length 19 digits.") ;
      return NULL ;
    }
    
    if (is_negativ) {
      /** We reset the pointer on data begin. **/
      
      float_to_binfloat-- ;
    }
    
  }
  
  char *result_string=calloc(128,sizeof(char)) ; /** String to perform the conversion into an binar float string. **/
  
  /** This is the heart of the work we store the conversion result in result_string. **/
  floattobinfloat(strtold(float_to_binfloat,NULL),result_string) ;
  
  char string_to_return[132]          ;  /** String to return.          **/
  memset(string_to_return,'\0',132)   ;  /** Setting all bytes on '\0'. **/ 
  
  if (result_string[0] == '-') {
    /** The result is negativ we format the function output: **/
    
    char *tmp=calloc(129,sizeof(char)) ; /** binar string part for formatting. **/ 
    int c,cc ;
    
    for (c=1,cc=0 ; result_string[c] != '\0' ; c++, cc++) {
      tmp[cc]=result_string[c]        ;  /** Temporary copy of the binar string without sign and identifier. **/ 
    }
    
    sprintf(string_to_return,"-0b%s",tmp) ;  /** We format the function output. **/
    
    free(tmp) ;
  }
  else {
    /** We format the function output. **/
    
    sprintf(string_to_return,"0b%s",result_string) ;
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
  
  /** We return the conversion result as an binar float string.                                            **/
  return Py_BuildValue("s",string_to_return); /** Convert an C string into an python string and return it. **/
}
