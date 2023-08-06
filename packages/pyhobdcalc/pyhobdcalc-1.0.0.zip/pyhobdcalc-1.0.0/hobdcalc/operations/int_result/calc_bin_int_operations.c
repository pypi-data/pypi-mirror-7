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

long long binaddbin(char *bin_str_1,char *bin_str_2) {
  long long bin_value_1 = bintoint(bin_str_1) ;
  long long bin_value_2 = bintoint(bin_str_2) ;
  
  return bin_value_1 + bin_value_2 ;
}

long long binsubbin(char *bin_str_1,char *bin_str_2) {
  long long bin_value_1 = bintoint(bin_str_1) ;
  long long bin_value_2 = bintoint(bin_str_2) ;
  
  return bin_value_1 - bin_value_2 ;
}

long long binmultbin(char *bin_str_1,char *bin_str_2) {
  long long bin_value_1 = bintoint(bin_str_1) ;
  long long bin_value_2 = bintoint(bin_str_2) ;
  
  return bin_value_1 * bin_value_2 ;
}

long double bindivbin(char *bin_str_1,char *bin_str_2) {
  long double bin_value_1 = (long double) bintoint(bin_str_1) ;
  long double bin_value_2 = (long double) bintoint(bin_str_2) ;
  
  return bin_value_1 / bin_value_2 ;
}
