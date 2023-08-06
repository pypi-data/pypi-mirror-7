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

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <tgmath.h>
#include <ctype.h>
#include <limits.h>
#include <inttypes.h>
#include <stdbool.h>
#include <ctype.h>
#include <errno.h>
#include <sys/time.h>

#include "conversion/utils/conversion_utils.c"

#include "conversion/int_hex/int_hex.c"
#include "conversion/int_bin/int_bin.c"
#include "conversion/int_oct/int_oct.c" 


#include "conversion/float_to_bin/float_bin.c"
#include "conversion/float_to_oct/float_oct.c"
#include "conversion/float_to_hex/float_hex.c"

#include "operations/int_result/calc_hex_int_operations.c"
#include "operations/int_result/calc_oct_int_operations.c"
#include "operations/int_result/calc_bin_int_operations.c"

#include "operations/float_result/calc_hex_float_operations.c"
#include "operations/float_result/calc_oct_float_operations.c"
#include "operations/float_result/calc_bin_float_operations.c"


/** 
 * hobdcalc can compute in the 
 * -) binar
 * -) octal
 * -) hexadecimal
 * bases without problems.
 * 
 * Arithmetics functions take the 2 operand as string
 * 
 * whose you can get with the conversion functions who take as first argument an value 
 * and as second a pointer to a buffer for containing the result (size 128).
 * 
 * The reverse functions take a string as argument and return the [integer|float] result.
 * 
 * The limits values are for:
 * integer: long long [-9223372036854775808 - 9223372036854775807].
 * floats : long double 15 digits precision.
 * 
 * You must link the type generic math file with:
 * $ gcc hobdcalc.c -lm
 * to compil the code.
 * 
 * You can use the test function:
 * for understanding the code. 
 * 
 * Note: I don't care about strtold() or strtoll() and the %x %o %a placeholders, only raw computing, because i made
 *       bad experience with it during developpment and testing.
 * 
 *       I hope this little calculator functions will be usefull for you.     
 * ******************************************************************************************************************/

#define DEBUG 1

void float_operations_test(void) ;

void integer_operations_test(void) ;

int main() {
  //fprintf(stdout,"Uncomment and configure the following assertions function:\ninteger_operations_test() ; test integer operation assertion function\nfloat_operations_test()   ; test float operation assertion function\n") ;
  // integer_operations_test() ; /** test integer operation assertion function */
  float_operations_test()   ; /* test float operation assertion function   */
  return 0 ;
  
}

void float_operations_test(void) {
  long double op1,op2 ;
  struct timeval tv ;
  char *op1_str=malloc(128) ;
  char *op2_str=malloc(128) ;
  int c ;
  
  for (c=0 ; c < 10000 ; c++) {
    /** Loop for assertions for float operations */
    gettimeofday(&tv,NULL) ;   /** get an random seed */
    
    srand(tv.tv_usec / 4) ;    /** setting the first operand random seed */
    op1= - (double) (rand() % (9223372036854775807/2)) / ((rand() % (9223372036854775807/2))+1) ; /** We take a negativ value. */
    
    srand(tv.tv_usec / 3) ;   /** setting the second operand random seed */
    op2= (double) (rand() % (9223372036854775807/2)) / ((rand() % (9223372036854775807/2))+1) ;   /** We take a positiv value. */
    
    
    memset(op1_str,'\0',128) ;
    memset(op2_str,'\0',128) ;
    
    floattobinfloat(op1,op1_str) ; /** Convert the float op1 in an binar string op1_str */
    floattobinfloat(op2,op2_str) ; /** Convert the float op2 in an binar string op2_str */
    
    
    
    #ifdef DEBUG
    /** Check if the values are correct converted */
    printf("%.15Lf == %.15Lf\n",op1,binfloattofloat(op1_str)) ;
    printf("%.15Lf == %.15Lf\n",op2,binfloattofloat(op2_str)) ;
    #endif
    
    if (op1 + op2 != binfloataddbinfloat(op1_str,op2_str) ) {
      printf("assertion float bin add error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,binfloataddbinfloat(op1_str,op2_str)) ;
      break ;
    }
    if (op1 - op2 != binfloatsubbinfloat(op1_str,op2_str) ) {
      printf("assertion float bin sub error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,binfloataddbinfloat(op1_str,op2_str)) ;
      break ;
    }
    if (op1 * op2 != binfloatmultbinfloat(op1_str,op2_str) ) {
      printf("assertion float bin mult error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,binfloataddbinfloat(op1_str,op2_str)) ;
      break ;
    }
    if ( (long double) op1 / (long double) op2 != binfloatdivbinfloat(op1_str,op2_str) ) {
      printf("assertion float bin div error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,binfloataddbinfloat(op1_str,op2_str)) ;
      break ;
    }
    else {
      #ifdef DEBUG
      /** printing all computing results. */
      printf("  %s\n+ %s\n= %.15Lf\n\n  %s \n- %s\n= %.15Lf\n\n  %s \n* %s\n= %.15Lf\n\n  %s \n/ %s\n= %.15Lf\n\n",op1_str,op2_str,binfloataddbinfloat(op1_str,op2_str),op1_str,op2_str,binfloatsubbinfloat(op1_str,op2_str),op1_str,op2_str,binfloatmultbinfloat(op1_str,op2_str),op1_str,op2_str,binfloatdivbinfloat(op1_str,op2_str)) ;
      #endif 
    }
    memset(op1_str,'\0',128) ;
    memset(op2_str,'\0',128) ;
    floattooctfloat(op1,op1_str) ; /** Convert the float op1 in an octal string op1_str */
    floattooctfloat(op2,op2_str) ; /** Convert the float op2 in an octal string op2_str */
    
    #ifdef DEBUG
    /** Check if the values are correct converted */
    printf("%.15Lf == %.15Lf\n",op1,octfloattofloat(op1_str)) ;
    printf("%.15Lf == %.15Lf\n",op2,octfloattofloat(op2_str)) ;
    #endif
    
    if (op1 + op2 != octfloataddoctfloat(op1_str,op2_str) ) {
      printf("assertion float oct add error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,octfloataddoctfloat(op1_str,op2_str)) ;
      break ;
    }
    if (op1 - op2 != octfloatsuboctfloat(op1_str,op2_str) ) {
      printf("assertion float oct sub error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,octfloatsuboctfloat(op1_str,op2_str)) ;
      break ;
    }
    if (op1 * op2 != octfloatmultoctfloat(op1_str,op2_str) ) {
      printf("assertion float oct mult error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,octfloatmultoctfloat(op1_str,op2_str)) ;
      break ;
    }
    if ( (long double) op1 / (long double) op2 != octfloatdivoctfloat(op1_str,op2_str) ) {
      printf("assertion float oct div error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,octfloatdivoctfloat(op1_str,op2_str)) ;
      break ;
    }
    else {
      #ifdef DEBUG
      /** printing all computing results. */
      printf("  %s\n+ %s\n= %.15Lf\n\n  %s \n- %s\n= %.15Lf\n\n  %s \n* %s\n= %.15Lf\n\n  %s \n/ %s\n= %.15Lf\n\n",op1_str,op2_str,octfloataddoctfloat(op1_str,op2_str),op1_str,op2_str,octfloatsuboctfloat(op1_str,op2_str),op1_str,op2_str,octfloatmultoctfloat(op1_str,op2_str),op1_str,op2_str,octfloatdivoctfloat(op1_str,op2_str)) ;
      #endif 
    }
    
    
    memset(op1_str,'\0',128) ;
    memset(op2_str,'\0',128) ;
    floattohexfloat(op1,op1_str) ; /** Convert the float op1 in an hexadecimal string op1_str */
    floattohexfloat(op2,op2_str) ; /** Convert the float op2 in an hexadecimal string op2_str */
    op1_str[128]='\0' ;
    op2_str[128]='\0' ;
     
    
    #ifdef DEBUG
    /** Check if the values are correct converted */
    printf("%.15Lf == %.15Lf\n",op1,hexfloattofloat(op1_str)) ;
    printf("%.15Lf == %.15Lf\n",op2,hexfloattofloat(op2_str)) ;
    #endif
    
    if (op1 + op2 != hexfloataddhexfloat(op1_str,op2_str) ) {
      printf("assertion float hex add error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,hexfloataddhexfloat(op1_str,op2_str)) ;
      break ;
    }
    
    if (op1 - op2 != hexfloatsubhexfloat(op1_str,op2_str) ) {
      printf("assertion float hex sub error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,hexfloataddhexfloat(op1_str,op2_str)) ;
      break ;
    }
    
    if (op1 * op2 != hexfloatmulthexfloat(op1_str,op2_str) ) {
      printf("assertion float hex mult error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,hexfloataddhexfloat(op1_str,op2_str)) ;
      break ;
    }
    if ( (long double) op1 / (long double) op2 != hexfloatdivhexfloat(op1_str,op2_str) ) {
      printf("assertion float hex div error by iteration %d:\nop1: %.15Lf == %s\nop2: %.15Lf == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,op1+op2,hexfloataddhexfloat(op1_str,op2_str)) ;
      break ;
    }
    else {
      #ifdef DEBUG
      /** printing all computing results. */
      printf("  %s\n+ %s\n= %.15Lf\n\n  %s \n- %s\n= %.15Lf\n\n  %s \n* %s\n= %.15Lf\n\n  %s \n/ %s\n= %.15Lf\n\n",op1_str,op2_str,hexfloataddhexfloat(op1_str,op2_str),op1_str,op2_str,hexfloatsubhexfloat(op1_str,op2_str),op1_str,op2_str,hexfloatmulthexfloat(op1_str,op2_str),op1_str,op2_str,hexfloatdivhexfloat(op1_str,op2_str)) ;
      #endif 
    }
    
    
    
  }
  free(op1_str) ;
  free(op2_str) ;
  
  return  ;
}

void integer_operations_test(void) {
  int c ;
  long long op1,op2 ;
  char *op1_str, *op2_str ;
  op1_str=malloc(128) ;
  
  op2_str=malloc(128) ;
  
  struct timeval tv ;
  
  for (c=0 ; c < 10000 ; c++) {
    /** Loop for assertions for integer operations */
    gettimeofday(&tv,NULL) ;   /** get an random seed */
    
    srand(tv.tv_usec /4 ) ;    /** setting the first operand random seed */
    op1= ((long long ) rand() % LLONG_MAX) ; /** We take a positiv value. */
    
    srand(tv.tv_usec / 3 ) ;   /** setting the second operand random seed */
    op2=  -  ((long long) rand() % LLONG_MAX) ; /** We take a negativ value. */
    
    memset(op1_str,'\0',128) ;
    memset(op2_str,'\0',128) ;
    inttobin(op1,op1_str) ; /** Convert the integer op1 in an binar string op1_str */
    inttobin(op2,op2_str) ; /** Convert the integer op2 in an binar string op2_str */
    
    #ifdef DEBUG
    /** Check if the values are correct converted */
    printf("%Li == %Li\n",op1,bintoint(op1_str)) ; 
    printf("%Li == %Li\n",op2,bintoint(op2_str)) ; 
    #endif
    
    if (! (op1 + op2 == binaddbin(op1_str,op2_str) ) ) {
      printf("assertion integer bin add error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %Li\nerror: %Li\n",c,op1,op1_str,op2,op2_str,op1+op2,binaddbin(op1_str,op2_str)) ;
      break ;
    }
    if (! (op1 - op2 == binsubbin(op1_str,op2_str)) ) {
      printf("assertion integer bin sub error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %Li\nerror: %Li\n",c,op1,op1_str,op2,op2_str,op1+op2,binsubbin(op1_str,op2_str)) ;
      break ;
    }
    if (! (op1 * op2 == binmultbin(op1_str,op2_str)) ) { 
      printf("assertion integer bin mult error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %Li\nerror: %Li\n",c,op1,op1_str,op2,op2_str,op1+op2,binmultbin(op1_str,op2_str)) ;
      break ;
    }
    if (! ((long double) op1 / (long double) op2 == bindivbin(op1_str,op2_str)) ) {
      printf("assertion integer bin div error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,(long double)op1+op2,bindivbin(op1_str,op2_str)) ;
      break ;
    }
    
  
    
    memset(op1_str,'\0',128) ;
    memset(op2_str,'\0',128) ;
    inttooct(op1,op1_str) ; /** Convert the integer op1 in an octal string op1_str */ 
    inttooct(op2,op2_str) ; /** Convert the integer op2 in an octal string op2_str */
    
    #ifdef DEBUG
    /** Check if the values are correct converted */
    printf("%Li == %Li\n",op1,octtoint(op1_str)) ;
    printf("%Li == %Li\n",op2,octtoint(op2_str)) ;
    #endif
    
    printf("%Li == %Li\n%Li == %Li\n",op1,octtoint(op1_str),op2,octtoint(op2_str)) ;

    if (! (op1 + op2 == octaddoct(op1_str,op2_str) ) ) {
	printf("assertion integer oct add error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %Li\nerror: %Li\n",c,op1,op1_str,op2,op2_str,op1+op2,octaddoct(op1_str,op2_str)) ;
	break ;
      }
    if (! (op1 - op2 == octsuboct(op1_str,op2_str)) ) {
      printf("assertion integer oct sub error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %Li\nerror: %Li\n",c,op1,op1_str,op2,op2_str,op1+op2,octsuboct(op1_str,op2_str)) ;
      break ;
    }
    if (! (op1 * op2 == octmultoct(op1_str,op2_str)) ) { 
      printf("assertion integer oct mult error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %Li\nerror: %Li\n",c,op1,op1_str,op2,op2_str,op1+op2,octmultoct(op1_str,op2_str)) ;
      break ;
    }
    if (! ((long double) op1 / (long double) op2 == octdivoct(op1_str,op2_str)) ) {
      printf("assertion integer oct div error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,(long double)op1+op2,octdivoct(op1_str,op2_str)) ;
      break ;
    }
     
     
   
    memset(op1_str,'\0',128) ;
    memset(op2_str,'\0',128) ; 
    inttohex(op1,op1_str) ; /** Convert the integer op1 in an hexadecimal string op1_str */
    inttohex(op2,op2_str) ; /** Convert the integer op2 in an hexadecimal string op2_str */
    
    #ifdef DEBUG
    /** Check if the values are correct converted */
    printf("%Li == %Li\n",op1,hextoint(op1_str)) ;
    printf("%Li == %Li\n",op2,hextoint(op2_str)) ;
    #endif

    if (! (op1 + op2 == hexaddhex(op1_str,op2_str) ) ) {
	printf("assertion integer hex add error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %Li\nerror: %Li\n",c,op1,op1_str,op2,op2_str,op1+op2,hexaddhex(op1_str,op2_str)) ;
	break ;
    }
    if (! (op1 - op2 == hexsubhex(op1_str,op2_str)) ) {
      printf("assertion integer hex sub error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %Li\nerror: %Li\n",c,op1,op1_str,op2,op2_str,op1+op2,hexsubhex(op1_str,op2_str)) ;
      break ;
    }
    if (! (op1 * op2 == hexmulthex(op1_str,op2_str)) ) { 
      printf("assertion integer hex mult error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %Li\nerror: %Li\n",c,op1,op1_str,op2,op2_str,op1+op2,hexmulthex(op1_str,op2_str)) ;
      break ;
    }
    if (! ((long double) op1 / (long double) op2 == hexdivhex(op1_str,op2_str)) ) {
      printf("assertion integer hex div error by iteration %d:\nop1: %Li == %s\nop2: %Li == %s\nresult: %.15Lf\nerror: %.15Lf\n",c,op1,op1_str,op2,op2_str,(long double)op1+op2,hexdivhex(op1_str,op2_str)) ;
      break ;
    }

    
    
  }
  
  free(op1_str) ;
  free(op2_str) ;
  return ;
  
}

