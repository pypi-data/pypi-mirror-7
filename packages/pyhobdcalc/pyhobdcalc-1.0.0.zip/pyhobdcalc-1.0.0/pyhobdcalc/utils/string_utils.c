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

void strip_zero(char *input) {
  /** Strip unwanted zeros upto the floating-point in case he is reach, he is removed and the result is convert to an integer 
   *  and a true value is returned marking the conversion take place. 
   * *************************************************************************************************************************/
  unsigned int c ;
  for (c=strlen(input)-1 ; input[c] == '0' ; c-- ) {
    input[c]='\0' ;
  }
  if (input[c] == '.' ) {
    input[c]='\0' ;
  }
}

_Bool is_entry_allowed(char digit,int8_t base) {
  /** Check if the given character is valid in relationship to the current selected base,
   *  and return false if it is the case.
   * ************************************************************************************/
  char base_08[8]  = {'0','1','2','3','4','5','6','7'} ;
  char base_10[13] = {'0','1','2','3','4','5','6','7','8','9','e','+','-'} ; 
  char base_16[22] = {'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','A','B','C','D','E','F'} ;
  int8_t c ;
  switch (base) {
    case 2 :
      if ((digit == '1') || (digit == '0')) {
	return true ;
      }
      else {
	return false ;
      }
    case 8 :
      for (c=0; c < 8 ; c++) {
	if (digit == base_08[c]) {
	  return true ;
	}
      }
      return false ;
    case 10 :
      for (c=0 ; c < 13 ; c++) {
	if (digit == base_10[c]) {
	  return true ;
	}
      }
      return false ;
    case 16 :
      for (c=0 ; c < 22 ; c++) {
	if (digit == base_16[c]) {
	  return true ;
	}
      }
      return false ;  
  }
  return false ;
}

_Bool is_string_as_base_an_valid_entry(char *entry,int8_t base) {
  /** Check if the given string is valid in relationship to the current selected base,
   *  and return false if it is the case.
   * ************************************************************************************/
  int16_t c=0 ;
  int comma_counter=0 ;  /** floating-point character counter in case of many occurence from it */
  if (entry[c] == '-') {
    c=1 ;
  }
  for ( ; c < (int) strlen(entry) ; c++) {
    if (comma_counter > 1) {
      return false ;
    }
    if ( ! is_entry_allowed(entry[c],base) && entry[c] != '.') {
      return  false ;
     }
    if (entry[c] == '.') {
      comma_counter++ ;
    }
  }
  return true ;
}

_Bool is_string_float(const char *string) {
  /** Return if the given string represent an float value.
   * *****************************************************/
  if (strchr(string,'.') != NULL) {
    return true ;
  }
  else {
    return false ;
  }
}