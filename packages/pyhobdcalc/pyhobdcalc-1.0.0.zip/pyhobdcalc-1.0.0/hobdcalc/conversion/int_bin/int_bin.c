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

void inttobin(long long int_to_bin,char *bin_str) {
  
  unsigned int i=0 ;
  
  char *bin_str_saved=malloc(128) ;
  memset(bin_str_saved,'\0',128) ;
  
  _Bool is_negativ=false ;
   
  if (int_to_bin == 0) {
    /** Case value to convert in binar string is null */
    strcpy(bin_str,"0") ;
    return ;
  }
  
  if (int_to_bin < 0) {
    /** Case value to convert in binar string is negativ */
    is_negativ=true ;
    int_to_bin=fabs(int_to_bin) ;
  }
  
  while (int_to_bin != 0) {
    bin_str[i]= set_digit(int_to_bin % 2) ; /** set the binar digit */
    int_to_bin /= 2 ;
    i++ ;
  }
  
  /** reversing the result string */
  unsigned int ii ;
  bin_str[i]='\0' ;
  for (i=0,ii=strlen(bin_str)-1 ; i < strlen(bin_str) ; i++,ii--) {
    bin_str_saved[i]=bin_str[ii] ;
  }
  bin_str_saved[i]='\0' ;
  
  /** Copy the result to pointer giving as argument ; */
  if (is_negativ) {
    strcpy(bin_str,"-") ;
    strcat(bin_str,bin_str_saved) ;
  }
  else {
    strcpy(bin_str,bin_str_saved) ;
  }
  
  
  return ;
}



long long bintoint(const char *bin_str) {
  unsigned int c,i ; /** c = exponent ; i = index ; (the string is reversed for pow(base,index)) */ 
  long long res= 0 ;
  _Bool is_negativ=false ;
  if ( bin_str[0] == '-' ) {
    /** Case argument string is an negativ value we remember it for returning */ 
     is_negativ=true ;
   }
    
  for (c=0,i=strlen(bin_str)-1 ; c < strlen(bin_str) ; c++,i--) {
    if (bin_str[i] == '1') {
      res += (long long) powl(2,c) ; /** get the octal digit integer value from char */
    }
  }
  
  if (is_negativ) {
    return - res ;
  }
  else {
    return res ;
  }
}
