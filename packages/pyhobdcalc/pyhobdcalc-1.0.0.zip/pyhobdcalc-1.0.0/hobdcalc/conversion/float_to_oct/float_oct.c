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

long double octfloattofloattintpart(const char *oct_str) {
  unsigned int c,i,pad ; /** c = exponent ; i = index ; (the string is reversed for pow(base,index)) */ 
  long double res ;
  pad=0 ;
  if ( oct_str[0] == '-' ) {
    /** Case argument string is an negativ value we remember it for returning */ 
     pad=1 ;
   }
  res=0.0 ;
  
  for (c=0,i=strlen(oct_str)-1; c < strlen(oct_str)-pad ; c++,i--) {
    if ( ! c == 0 ) {
      res = res + (get_digit(oct_str[i])*powl(8,c)) ; /** get the hexadecimal value from char */
    }
    else {
      /** Case for first digit */
      res = get_digit(oct_str[i]) ; /** get the hexadecimal value from char */
    }
  }
  
  
  return res ;
  
}


void inttooctfloatpart(long double int_to_oct,char *oct_str,int precision) {
  /* Set the float part value in an octal string stored in the given pointer ;
   ***************************************************************************/
  
  /** temporary final result container variable used for computing */
  char *oct_str_saved=malloc(96) ;
  memset(oct_str_saved,'\0',96) ;

  int c=0 ;
  if (int_to_oct < 0) {
    /** value needed for computing */
    int_to_oct=fabs(int_to_oct) ;
  }
  while (c < (precision)) {
    /** loop for computing until precision is reach */
    
    char *to_oct=malloc(32) ;
    memset(to_oct,'\0',32) ;
    
    long double res_int ;
    long double res_float ;
    
    res_float=modfl(int_to_oct* 8.0,&res_int) ; /** modulo float */
    
    inttooct(res_int,to_oct) ;  /** getting the octal string of the integer to add to float part */
    
    strcat(oct_str_saved,to_oct) ;
    if ( res_float == 0.0 ) {
      break ; /** reach end of octal string computing */
    }
    
    int_to_oct=res_float ; /** updating value */
    c++ ;
  }
  
  sprintf(oct_str,"%s",oct_str_saved) ;
  free(oct_str_saved) ;
  
}

long double octfloattofloat(char *oct_float_str) {
  /* Convert an octal string from the given pointer in an float value ;
   ********************************************************************/
  
  if ( strchr(oct_float_str,'.') == NULL) {
    /** Case argument string is not a float, return integer value (long double) cast */ 
    return octfloattofloattintpart(oct_float_str) ;
  }
  char *oct_float_str_saved=strdup(oct_float_str) ;
  _Bool is_negativ=false ;
  if ( oct_float_str[0] == '-' ) {
    /** Case argument string is an negativ value we remember it for returning */ 
    is_negativ=true ;
    int i,c ;
     for (i=1,c=0 ; i < (int) strlen(oct_float_str) ; i++,c++) {
       oct_float_str_saved[c]=oct_float_str[i] ;
     }
     oct_float_str_saved[c]='\0' ;
  }
  else {
    oct_float_str_saved=strdup(oct_float_str) ;
  }
  
  /** variables for splitting in integer and float part */ 
  
  char *oct_int_part=malloc(64) ;
  char *oct_float_part=malloc(64) ;
  memset(oct_int_part,'\0',64) ;
  memset(oct_float_part,'\0',64) ;
  
  /** Perform splitting for getting float part we are interest */
  splitter(oct_float_str_saved,oct_int_part,oct_float_part) ;
  
  long double res_int = octfloattofloattintpart(oct_int_part) ; /** value to return for the integer part */
  
  unsigned int c  ;           /** float part index */
  int cc ;                    /** float exponent value */
  long double res_float=0.0 ; /** variable for computing float part */
  
  for(c=0 ,cc=-1 ; c < strlen(oct_float_part) ; c++,cc--) {
    res_float += (long double) get_digit(oct_float_part[c]) * powl(8,cc) ;
  }
  
  free(oct_int_part) ;
  free(oct_float_part) ;
  free(oct_float_str_saved) ;
  
  long double result= res_int + res_float ;
  
  if ( is_negativ ) {
     return -result  ;
   }
   else {
     return result ;
   }
} 

void floattooctfloat(long double int_to_oct,char *oct_str) {
  /* Convert an float value in an octal string stored in the given pointer;
   ************************************************************************/
  
  long double int_part=0.0 ;
  long double float_part=0.0 ;
 
  float_part=modfl(int_to_oct,&int_part) ; /** modulo float */
  
  /** variables for splitting in integer and float part */
  char *int_part_str_oct=malloc(129) ;
  char *float_part_str_oct=malloc(129) ;
  memset(int_part_str_oct,'\0',129) ;
  memset(float_part_str_oct,'\0',129) ;
  
  /** Perform splitting in integer and float part */
  inttooct(int_part,int_part_str_oct) ;
  inttooctfloatpart(float_part,float_part_str_oct,128) ;

  /** result octal string variable (pointer given as argument) */
  memset(oct_str,'\0',129) ;
  
  if ( (int_to_oct  < 0) && (int_part_str_oct[0] != '-') ) {
    /** Case value to convert in binfloat string is negativ */
    strcpy(oct_str,"-") ;
  }
  
  /** Assemble final binar string */
  strcat(oct_str,int_part_str_oct) ;
  strcat(oct_str,".") ;
  strcat(oct_str,float_part_str_oct) ;
  
}

