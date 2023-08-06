
=======================
pyhobdcalc description.
=======================

-------------------------------------------------------------------
**pyhobdcalc for Python Hexdecimal Octal Binar Decimal Calculator**
-------------------------------------------------------------------

:::::::::::::::::::::::
The module description:
:::::::::::::::::::::::


                                                                                                                                     
  pyhobdcalc is an python module written in C which implement conversion and calculating functions in bases 2, 8, 10, 16.          
                                                                                                                                   
            Which python desn't implement like signed binar, octal, hexadecimal conversion in integers.                            
                                                                                                                                   
            Or signed float conversion from decimal to base 2, 8, 16 or from base 2, 8, 16 in decimal base.                        
                                                                                                                                   
            And permit to add, substract, multiply and divide base 2, 8, 16 integers and floats strings.                           
                                                                                                                                   

    
  
:::::::::::::::::::::
The module implement:
:::::::::::::::::::::

++++++++++++++++++++++++++
Base conversion functions:
++++++++++++++++++++++++++

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Different bases integer strings conversion to integer:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
    
    1. **bintoint**:
    
        Convert an binar string given with optional the binar identifier "0b". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the converted value as an integer string.
        
    2. **octtoint**:
    
        Convert an octal string given with optional the octal identifier "0". The function can thread signed values in the C type *long long int* value range:               
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the converted value as an integer string.
        
    3. **hextoint**:
    
        Convert an hexadecimal string given with optional the hexdecimal identifier "0x". The function can thread signed values in the C type *long long int* value range:               
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the converted value as an integer string.
        
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
Different bases floats strings conversion to floats: 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. **binfloattofloat**:
    
        Convert an binar string with optional binar identifier "0b" representing an floating-point value into an float with maximal precision from 15 digits.
        
        And return the converted value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.
            
    2. **octfloattofloat**:
    
        Convert an octal string with optional octal identifier "0" representing an floating-point value into an float with maximal precision from 15 digits.
        
        And return the converted value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.
            
    3. **hexfloattofloat**:
    
        Convert an hexadecimal string with optional hexdecimal identifier "0x" representing an floating-point value into an float with maximal precision from 15 digits.
        
        And return the converted value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.
            
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Float to different bases floats:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~                     

    1. **floattobinfloat**:
    
        Convert an float given as an string into an floating-point binar string with maximal value from 16 binar digits. The given float integer part can be maximal 8 bytes great.
        
        And return the floating-point binar string corresponding to the given float with the given limitations.
        
    2. **floattooctfloat**:
    
        Convert an float given as an string into an floating-point octal string with maximal value from 16 octal digits. The given float integer part can be maximal 8 bytes great.
        
        And return the floating-point octal string corresponding to the given float with the given limitations.
        
    3. **floattohexfloat**:
    
        Convert an float given as an string into an floating-point hexadecimal string with maximal value from 16 hexadecimal digits. The given float integer part can be maximal 8 bytes great.
        
        And return the floating-point hexadecimal string corresponding to the given float with the given limitations.
                   
                   
+++++++++++++++++++++++++++++++++++++++++++++
Base 2, 8, 16 integers calculating functions:
+++++++++++++++++++++++++++++++++++++++++++++

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Binar integer calculating functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  1. **binaddbin**:
        
        Add 2 binar strings given with optional the binar identifier "0b". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the addition result as an integer string.    
            
            :note: The addition result cannot overflow the same maximal and minimal range as for the given arguments values.
            
  2. **binsubbin**:
        
        Substract 2 binar strings given with optional the binar identifier "0b". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the substraction result as an integer string.    
            
            :note: The substraction result cannot overflow the same maximal and minimal range as for the given arguments values. 
            
  3. **binmultbin**:
        
        Multiply 2 binar strings given with optional the binar identifier "0b". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the multiplication result as an integer string.    
            
            :note: The multiplication result cannot overflow the same maximal and minimal range as for the given arguments values.
            
  4. **bindivbin**:
        
        Divide 2 binar strings given with optional the binar identifier "0b". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the division result as an integer string.    
            
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.
            
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Octal integer calculating functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  1. **octaddoct**:
        
        Add 2 octal strings given with optional the octal identifier "0". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the addition result as an integer string.    
            
            :note: The addition result cannot overflow the same maximal and minimal range as for the given arguments values.
            
  2. **octsuboct**:
        
        Substract 2 octal strings given with optional the octal identifier "0". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the substraction result as an integer string.    
            
            :note: The substraction result cannot overflow the same maximal and minimal range as for the given arguments values. 
            
  3. **octmultoct**:
        
        Multiply 2 octal strings given with optional the octal identifier "0". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the multiplication result as an integer string.    
            
            :note: The multiplication result cannot overflow the same maximal and minimal range as for the given arguments values.
            
  4. **octdivoct**:
        
        Divide 2 octal strings given with optional the octal identifier "0". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the division result as an integer string.    
            
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.
            
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Hexadecimal integer calculating functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  1. **hexaddhex**:
        
        Add 2 hexdecimal strings given with optional the hexdecimal identifier "0x". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the addition result as an integer string.    
            
            :note: The addition result cannot overflow the same maximal and minimal range as for the given arguments values.
            
  2. **hexsubhex**:
        
        Substract 2 hexdecimal strings given with optional the hexdecimal identifier "0x". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the substraction result as an integer string.    
            
            :note: The substraction result cannot overflow the same maximal and minimal range as for the given arguments values. 
            
  3. **hexmulthex**:
        
        Multiply 2 hexdecimal strings given with optional the hexdecimal identifier "0x". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the multiplication result as an integer string.    
            
            :note: The multiplication result cannot overflow the same maximal and minimal range as for the given arguments values.
            
  4. **hexdivhex**:
        
        Divide 2 hexdecimal strings given with optional the hexdecimal identifier "0x". The function can threads signed values in the C type *long long int* value range:
        
            * Maximal value:  9223372036854775807.
            
            * Minimal value: -9223372036854775808.
            
        And return the division result as an integer string.    
            
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.
                                   
            
++++++++++++++++++++++++++++++++++++++++++
Base 2, 8, 16 float calculating functions:
++++++++++++++++++++++++++++++++++++++++++                               

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Binar float calculating functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. **binfloataddbinfloat**:
    
        Add 2 binar strings given with optional the binar identifier "0b". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire binar string can contains 128 binary digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
            
    2. **binfloatsubbinfloat**:
    
        Substract 2 binar strings given with optional the binar identifier "0b". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire binar string can contains 128 binary digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
                  
    3. **binfloatmultbinfloat**:
    
        Multiply 2 binar strings given with optional the binar identifier "0b". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire binar string can contains 128 binary digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
            
    4. **binfloatdivbinfloat**:
    
        Divide 2 binar strings given with optional the binar identifier "0b". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire binar string can contains 128 binary digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
                                
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Octal float calculating functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. **octfloataddoctfloat**:
    
        Add 2 octal strings given with optional the octal identifier "0". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire octal string can contains 48 octal digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
            
    2. **octfloatsuboctfloat**:
    
        Substract 2 octal strings given with optional the octal identifier "0". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire octal string can contains 48 octal digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
                  
    3. **octfloatmultoctfloat**:
    
        Multiply 2 octal strings given with optional the octal identifier "0". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire octal string can contains 48 octal digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
            
    4. **octfloatdivoctfloat**:
    
        Divide 2 octal strings given with optional the octal identifier "0". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire octal string can contains 48 octal digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
                                
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Hexadecimal float calculating functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. **hexfloataddhexfloat**:
    
        Add 2 hexadecimal strings given with optional the hexadecimal identifier "0x". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire hexadecimal string can contains 16 hexadecimal digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
            
    2. **hexfloatsubhexfloat**:
    
        Substract 2 hexadecimal strings given with optional the hexadecimal identifier "0x". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire hexadecimal string can contains 16 hexadecimal digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
                  
    3. **hexfloatmulthexfloat**:
    
        Multiply 2 hexadecimal strings given with optional the hexadecimal identifier "0x". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire hexadecimal string can contains 16 hexadecimal digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
            
    4. **hexfloatdivhexfloat**:
    
        Divide 2 hexadecimal strings given with optional the hexadecimal identifier "0x". The function can threads 8 bytes values for the integer part from the float, in the C type *long long int* value range:
        
            * Maximal integer part value:  9223372036854775807.
            
            * Minimal integer part value: -9223372036854775808.
            
        The entire hexadecimal string can contains 16 hexadecimal digits (without identifier, sign and comma.).
        
        And return the result value as an float string.
        
            :note: The returned value is limited to the C type *double* (15 digits precision) but the module compute internally with the C type *long double* (19 digits precision) for getting an exact value.                                                          
                                                               
                                           
              
                             