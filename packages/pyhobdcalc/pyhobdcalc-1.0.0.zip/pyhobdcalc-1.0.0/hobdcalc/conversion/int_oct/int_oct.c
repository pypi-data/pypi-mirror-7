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

void inttooct(long long int_to_oct,char *oct_str) {
  unsigned int i=0 ;
  
  char *oct_str_saved=malloc(128) ;
  memset(oct_str_saved,'\0',128) ;  
  
  _Bool is_negativ=false ;
  
  if (int_to_oct == 0) {
    /** Case value to convert in octal string is null */
    strcpy(oct_str,"0") ;
    return ;
  }
  if (int_to_oct < 0) {
    /** Case value to convert in octal string is negativ */
    is_negativ=true ;
    int_to_oct=fabs(int_to_oct) ;
  }
  while (int_to_oct != 0) {
    oct_str[i]= set_digit(int_to_oct % 8) ; /** set the octal digit integer value */
    int_to_oct /= 8 ;
    i++ ;
  }
  
  /** reversing the result string */
  unsigned int ii ;
  oct_str[i]='\0' ;
  for (i=0,ii=strlen(oct_str)-1 ; i < strlen(oct_str) ; i++,ii--) {
    oct_str_saved[i]=oct_str[ii] ; 
  }
  
  oct_str_saved[i]='\0' ;
  
  /** Copy the result to pointer giving as argument ; */
  if (is_negativ) {
    strcpy(oct_str,"-") ;
    strcat(oct_str,oct_str_saved) ;
    return ;
  }
  else {
    strcpy(oct_str,oct_str_saved) ;
    return ;
  }
}



long long octtoint(const char *oct_str) {
  unsigned int c,i,pad ; /** c = exponent ; i = index ; (the string is reversed for pow(base,index)) */ 
  long long res ;
  _Bool is_negativ=false ;
  pad=0 ;
  if ( oct_str[0] == '-' ) {
    /** Case argument string is an negativ value we remember it for returning */ 
     is_negativ=true ;
     pad=1 ;
   }
  res=0 ;
  res=0 ;  
  for (c=0,i=strlen(oct_str)-1; c < strlen(oct_str)-pad ; c++,i--) {
    if ( ! c == 0 ) {
      res = res + (get_digit(oct_str[i])*powl(8,c)) ; /** get the hexadecimal value from char */
    }
    else {
      /** Case for first digit */
      res = get_digit(oct_str[i]) ; /** get the hexadecimal value from char */
    }
  }
  if (is_negativ) {
    return - res ;
  }
  else {
    return res ;
  }
}
