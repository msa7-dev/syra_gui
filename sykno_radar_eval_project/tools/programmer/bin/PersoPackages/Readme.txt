==================================
Personnalisation Package Purpose
==================================

HSMv2 used for SFI and SSP Process are shipped from ST in a virgin state by
default. to use it with our STM32 MCU/MPU you have to provision it with the 
right Perso Package corresponding to the device you have. Personnalisation 
procedure happens in same time of Key and Counter HSM Provisioning.


=================================================
How to select the right Personnalisation Package
=================================================

A first way to select the Perso package is to look at the file name, the first
string indicates the MCU Family, for example :

STM32WL_49701005_SFI._01000000_00000000.enc.bin

is the perso package to be used with STM32WL Devices.

in some cases there is multiple perso packages for same family, which is the
case of STM32H7 Family :

STM32H7_45001001_SFI._01000000_00000000.enc.bin
STM32H7_45002001_SFI._01000000_00000000.enc.bin

In this case you have to check the MCU Product ID you have, the prodcut ID is
the second part in perso package file name, for H7 Family 2 product ID are
available and extracted from Perso package file name :

_45001001_ &  _45002001_

to check your product ID you have to read the chip certificate using
STM32CubeProgrammer CLI in this way : 

STM32_Programmer_CLI -c port=swd mode=hotplug -gc c:\certificate.bin

Edit the certificate.bin using your prefered Hex Editor or simple Text editor 
and you will find the product ID at the beginning of the certificate file 
(ASCII characters).

In some devices like STM32WL/STM32L5/STM32U5 the product ID is directly
displayed by -gc command (which is not the case for H7 where you have to extract
it manually from the certificate).
