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

void inttohex(long long int_to_hex,char *hex_str) {
  unsigned int i=0 ;
  
  char *hex_str_saved=malloc(128) ;
  memset(hex_str_saved,'\0',128) ;
  
  _Bool is_negativ=false ;
  
  if (int_to_hex == 0) {
    /** Case value to convert in hexadecimal string is null */
    strcpy(hex_str,"0") ;
    return ;
  }
  
  if (int_to_hex < 0) {
    /** Case value to convert in hexadecimal string is negativ */
    is_negativ=true ;
    int_to_hex=fabs(int_to_hex) ;
  }
  
  
  while (int_to_hex != 0) {
    hex_str[i]=set_digit((int_to_hex % 16)) ; /** set the hexadecimal digit integer value */
    int_to_hex /= 16 ;
    i++ ;
  }
  
  /** reversing the result string */
  unsigned int ii ;
  hex_str[i]='\0' ;
  for (i=0,ii=strlen(hex_str)-1 ; i < strlen(hex_str) ; i++,ii--) {
    hex_str_saved[i]=hex_str[ii] ;
  }
  hex_str_saved[i]='\0' ;
  
  /** Copy the result to pointer giving as argument ; */
  if (is_negativ) {
    strcpy(hex_str,"-") ;
    strcat(hex_str,hex_str_saved) ;
  return ;
  
    
  }
  else {
    strcpy(hex_str,hex_str_saved) ;
    return ;
  }
}




long long hextoint(const char *hex_str) {
  unsigned int c,i,pad ; /** c = exponent ; i = index ; (the string is reversed for pow(base,index)) */ 
  long long res ;
  _Bool is_negativ=false ;
  pad=0 ;
  if ( hex_str[0] == '-' ) {
    /** Case argument string is an negativ value we remember it for returning */ 
     is_negativ=true ;
     pad=1 ;
   }
   
  res=0 ;  
  for (c=0,i=strlen(hex_str)-1; c < strlen(hex_str)-pad ; c++,i--) {
    if ( ! c == 0 ) {
      res = res + (get_digit(hex_str[i])*powl(16,c)) ; /** get the hexadecimal value from char */
    }
    else {
      /** Case for first digit */
      res = get_digit(hex_str[i]) ; /** get the hexadecimal value from char */
    }
  }
  if (is_negativ) {
    return - res ;
  }
  else {
    return res ;
  }
  
}


