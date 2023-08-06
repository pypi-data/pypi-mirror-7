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


void round_hex_string(char *hex_str,int index) {
  /** Unused function */
  int idx=index-1 ;
  if ( get_digit(hex_str[idx]) > 7 ) {
      idx-- ;
      if (get_digit(hex_str[idx]) == 15) {
	;
      }
      else {
        hex_str[idx]=set_digit(get_digit(hex_str[idx])+1) ;
      }
    }
    
  hex_str[index-1]='\0' ;
  return ;
}

long double hexfloattofloatintpart(const char *hex_str) {
  unsigned int c,i,pad ; /** c = exponent ; i = index ; (the string is reversed for pow(base,index)) */ 
  long double res ;
  pad=0 ;
  if ( hex_str[0] == '-' ) {
    /** Case argument string is an negativ value we remember it for returning */ 
     pad=1 ;
   }
  res=0.0 ;
  
  for (c=0,i=strlen(hex_str)-1; c < strlen(hex_str)-pad ; c++,i--) {
    if ( ! c == 0 ) {
      res = res + (get_digit(hex_str[i])*powl(16,c)) ; /** get the hexadecimal value from char */
    }
    else {
      /** Case for first digit */
      res = get_digit(hex_str[i]) ; /** get the hexadecimal value from char */
    }
  }
  
  
  return res ;
  
}

void inttohexfloatpart(long double float_to_hex,char *hex_str,int precision) {
  /* Set the float part value in an hexadecimal string stored in the given pointer ;
   *********************************************************************************/
  
  /** temporary final result container variable used for computing */
  char *hex_str_saved=malloc(96) ;
  memset(hex_str_saved,'\0',96) ;
  
  int c=0 ;
  if (float_to_hex < 0) {
    /** value needed for computing */
    float_to_hex=fabs(float_to_hex) ;
  }
  
  while (c < (precision)) {
    /** loop for computing until precision is reach */
    char *to_hex=malloc(32) ;
    memset(to_hex,'\0',32) ;
    
    long double res_int ;
    long double res_float ;
    
    res_float = modfl(float_to_hex * 16.0,&res_int) ; /** modulo float */
    
    inttohex((long long) res_int,to_hex) ; /** getting the hexadecimal string of the integer to add to float part */
    strcat(hex_str_saved,to_hex) ;          

    if ( res_float == 0.0 ) {
      break ; /** reach end of hexadecimal string computing */
    }
    
    float_to_hex=res_float ; /** updating value */
    c++ ;
  }
  
  snprintf(hex_str,(size_t) precision,"%s",hex_str_saved) ;
  free(hex_str_saved) ;
  hex_str[++c]='\0' ;
}

long double hexfloattofloat(char *hex_float_str) {
  /* Convert an hexadecimal string from the given pointer in an float value ;
   **************************************************************************/
  
  if ( strchr(hex_float_str,'.') == NULL) {
    /** Case argument string is not a float, return integer value (long double) cast */ 
    return hexfloattofloatintpart(hex_float_str) ;
  }
  char *hex_float_str_saved=malloc(64) ;
  _Bool is_negativ=false ;
  if ( hex_float_str[0] == '-' ) {
    /** Case argument string is an negativ value we remember it for returning */ 
     is_negativ=true ;
     int i,c ;
     for (i=1,c=0 ; i < (int) strlen(hex_float_str) ; i++,c++) {
       hex_float_str_saved[c]=hex_float_str[i] ;
     }
     hex_float_str_saved[c]='\0' ;  
   }
   else {
     hex_float_str_saved=strdup(hex_float_str) ;
   }
   
  /** variables for splitting in integer and float part */ 
  
  char *hex_int_part=malloc(64) ;
  char *hex_float_part=malloc(64) ;
  memset(hex_int_part,'\0',64) ;
  memset(hex_float_part,'\0',64) ;
  
  /** Perform splitting for getting float part we are interest */
  splitter(hex_float_str_saved,hex_int_part,hex_float_part) ;
  
  
  long double res_int = hexfloattofloatintpart(hex_int_part) ; /** value to return for the integer part */
  
  unsigned int c  ;            /** float part index */
  int cc ;                     /** float exponent value */
  long double res_float=0.0 ;  /** variable for computing float part */

  for(c=0 ,cc=-1 ; c < strlen(hex_float_part) ; c++,cc--) {
    res_float += (long double) get_digit(hex_float_part[c]) * powl(16,cc) ;
  }
  
  free(hex_int_part) ;
  free(hex_float_part) ;
  free(hex_float_str_saved) ;
  
  long double result= res_int + res_float ;
  
  //check_error_overflow() ;
  
  if ( is_negativ ) {
     return -result ;
   }
   else {
     return result ;
   }
} 

void floattohexfloat(long double int_to_hex,char *hex_str) {
  /* Convert an float value in an hexadecimal string stored in the given pointer;
   ******************************************************************************/
  long double int_part=0.0 ;
  long double float_part=0.0 ;
  _Bool is_negativ = false ;
  if (int_to_hex < 0) {
    int_to_hex=fabs(int_to_hex) ;
    is_negativ=true ;
  }
  
  float_part=modfl(int_to_hex,&int_part) ; /** modulo float */
  
  /** variables for splitting in integer and float part */
  char *int_part_str_hex=malloc(129) ;
  char *float_part_str_hex=malloc(129) ;
  memset(int_part_str_hex,'\0',129) ;
  memset(float_part_str_hex,'\0',129) ;
  
  /** Perform splitting in integer and float part */
  inttohex((long long) int_part,int_part_str_hex) ;
  inttohexfloatpart(float_part,float_part_str_hex,128) ;

  /** result binar string variable (pointer given as argument) */
  memset(hex_str,'\0',129) ;
  
  if ((is_negativ) && (int_part_str_hex[0] != '-')) {
    /** Case value to convert in binfloat string is negativ */
    strcpy(hex_str,"-") ;
  }
  
  /** Assemble final binar string */
  strcat(hex_str,int_part_str_hex) ;
  strcat(hex_str,".") ;
  strcat(hex_str,float_part_str_hex) ;
  
}

