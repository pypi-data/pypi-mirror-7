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

long double binfloattofloatintpart(const char *bin_str) {
  unsigned int c,i ; /** c = exponent ; i = index ; (the string is reversed for pow(base,index)) */ 
  long double res= 0.0 ;
  for (c=0,i=strlen(bin_str)-1 ; c < strlen(bin_str) ; c++,i--) {
    if (bin_str[i] == '1') {
      res += (long long) powl(2,c) ; /** get the octal digit integer value from char */
    }
  }
 
  return res ;
 
}

void inttobinfloatpart(long double int_to_bin,char *bin_str,int precision) {
  /* Set the float part value in an binar string stored in the given pointer ;
   ***************************************************************************/
  
  /** temporary final result container variable used for computing */
  char *bin_str_saved=malloc(96) ;
  memset(bin_str_saved,'\0',96) ;
  
  int c=0 ;
  if (int_to_bin < 0) {
    /** value needed for computing */
    int_to_bin=fabs(int_to_bin) ;
  }
  while (c < precision) {
    /** loop for computing until precision is reach */
    
    long double res_int ;
    long double res_float ;
    
    res_float=modfl(int_to_bin * 2.0,&res_int) ; /** modulo float */
    
    
    if ( res_int  == 0) {
      strcat(bin_str_saved,"0") ; /** getting the binar string component as the integer to add to float part */
    }
    else if ( res_int  == 1 ) {
      strcat(bin_str_saved,"1") ; /** getting the binar string component as the integer to add to float part */
    }
    else {
      return ;
    }
    
    if ( res_float == 0.0 ) {
      break ; /** reach end of binar float string computing */
    } 
    
    int_to_bin=res_float ;
    
    c++ ;
  }
  
  sprintf(bin_str,"%s",bin_str_saved) ;
  free(bin_str_saved) ;
}

long double binfloattofloat(char *bin_float_str) {
  /* Convert an binar string from the given pointer in an float value ;
   *******************************************************************/
  
  if ( strchr(bin_float_str,'.') == NULL) {
    /** Case argument string is not a float, return integer value (long double) cast */ 
    return binfloattofloatintpart(bin_float_str) ;
  }
  
  _Bool is_negativ=false ;
  if ( bin_float_str[0] == '-' ) {
     /** Case argument string is an negativ value we remember it for returning */ 
     is_negativ=true ;
   }
  
  /** variables for splitting in integer and float part */
  char *bin_float_str_saved=strdup(bin_float_str) ;
  char *bin_int_part=malloc(65) ;
  char *bin_float_part=malloc(65) ;
  memset(bin_int_part,'\0',65) ;
  memset(bin_float_part,'\0',65) ;
  
  /** Perform splitting for getting float part we are interest */
  splitter(bin_float_str_saved,bin_int_part,bin_float_part) ;
  
  long double res_int = binfloattofloatintpart(bin_int_part) ; /** value to return for the integer part */
  
  
  unsigned int c ;        /** float part index */
  int cc ;                /** float exponent value */
  long double res_float=0.0 ;  /** variable for computing float part */
  
  for(c=0 ,cc=-1 ; c < strlen(bin_float_part) ; c++,cc--) {
    res_float += (long double) (((int) bin_float_part[c]-'0') * powl(2,cc)) ;
  }
  
  free(bin_int_part) ;
  free(bin_float_part) ;
  free(bin_float_str_saved) ;
  
  long double result= res_int + res_float ;
  
  //check_error_overflow() ;
  
  if ( is_negativ ) {
    return -result ;
   }
   else {
     return result ;
   }

}  



void floattobinfloat(long double int_to_bin,char *bin_str) {
  /* Convert an float value in an binar string stored in the given pointer;
   ************************************************************************/
  
  long double int_part=0.0 ;
  long double float_part=0.0 ;
  
  float_part=modfl(int_to_bin,&int_part) ; /** modulo float */
  
  /** variables for splitting in integer and float part */
  char *int_part_str_bin=malloc(129) ;
  char *float_part_str_bin=malloc(129) ;
  memset(int_part_str_bin,'\0',129) ;
  memset(float_part_str_bin,'\0',129) ;
  
  /** Perform splitting in integer and float part */
  inttobin((long long) int_part,int_part_str_bin) ;
  inttobinfloatpart(float_part,float_part_str_bin,128) ;
  
  /** result binar string variable (pointer given as argument) */
  memset(bin_str,'\0',129) ;
  if ( ( int_to_bin  < 0) && (int_part_str_bin[0] != '-') ) {
    /** Case value to convert in binfloat string is negativ */
    strcpy(bin_str,"-") ;
  }
  
  /** Assemble final binar string */
  strcat(bin_str,int_part_str_bin) ;
  strcat(bin_str,".") ;
  strcat(bin_str,float_part_str_bin) ;
  
}




