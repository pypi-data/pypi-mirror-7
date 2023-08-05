# Compiled by Charles Harris, dated October 3, 2002
# updated to 2002 values by BasSw, 2006
# Updated to 2006 values by Vincent Davis June 2010

"""
Fundamental Physical Constants
------------------------------

These constants are taken from CODATA Recommended Values of the Fundamental
Physical Constants 2010.

Object
------
physical_constants : dict
    A dictionary containing physical constants. Keys are the names of
    physical constants, values are tuples (value, units, precision).

Functions
---------
value(key):
    Returns the value of the physical constant(key).
unit(key):
    Returns the units of the physical constant(key).
precision(key):
    Returns the relative precision of the physical constant(key).
find(sub):
    Prints or returns list of keys containing the string sub, default is
    all.

Source
------
The values of the constants provided at this site are recommended for
international use by CODATA and are the latest available. Termed the "2010
CODATA recommended values," they are generally recognized worldwide for use in
all fields of science and technology. The values became available on 2 June
2011 and replaced the 2006 CODATA set. They are based on all of the data
available through 31 December 2010. The 2010 adjustment was carried out under
the auspices of the CODATA Task Group on Fundamental Constants. See References
for an introduction to the constants for nonexperts.

References
----------
Theoretical and experimental publications relevant to the fundamental
constants and closely related precision measurements published since the mid
1980s, but also including many older papers of particular interest, some of
which date back to the 1800s. To search bibliography visit

http://physics.nist.gov/cuu/Constants/

"""
from __future__ import division, print_function, absolute_import


import warnings
from math import pi, sqrt
__all__ = ['physical_constants', 'value', 'unit', 'precision', 'find',
           'ConstantWarning']

"""
Source:  http://physics.nist.gov/cuu/Constants/index.html

The values of the constants provided at the above site are recommended
for international use by CODATA and are the latest available. Termed
the "2006 CODATA recommended values", they are generally recognized
worldwide for use in all fields of science and technology. The values
became available in March 2007 and replaced the 2002 CODATA set. They
are based on all of the data available through 31 December 2006. The
2006 adjustment was carried out under the auspices of the CODATA Task
Group on Fundamental Constants.
"""

#
# Source:  http://physics.nist.gov/cuu/Constants/index.html
#

# Quantity                                             Value                 Uncertainty          Unit
# ---------------------------------------------------- --------------------- -------------------- -------------
txt2002 = """\
Wien displacement law constant                         2.897 7685e-3         0.000 0051e-3         m K
atomic unit of 1st hyperpolarizablity                  3.206 361 51e-53      0.000 000 28e-53      C^3 m^3 J^-2
atomic unit of 2nd hyperpolarizablity                  6.235 3808e-65        0.000 0011e-65        C^4 m^4 J^-3
atomic unit of electric dipole moment                  8.478 353 09e-30      0.000 000 73e-30      C m
atomic unit of electric polarizablity                  1.648 777 274e-41     0.000 000 016e-41     C^2 m^2 J^-1
atomic unit of electric quadrupole moment              4.486 551 24e-40      0.000 000 39e-40      C m^2
atomic unit of magn. dipole moment                     1.854 801 90e-23      0.000 000 16e-23      J T^-1
atomic unit of magn. flux density                      2.350 517 42e5        0.000 000 20e5        T
deuteron magn. moment                                  0.433 073 482e-26     0.000 000 038e-26     J T^-1
deuteron magn. moment to Bohr magneton ratio           0.466 975 4567e-3     0.000 000 0050e-3
deuteron magn. moment to nuclear magneton ratio        0.857 438 2329        0.000 000 0092
deuteron-electron magn. moment ratio                   -4.664 345 548e-4     0.000 000 050e-4
deuteron-proton magn. moment ratio                     0.307 012 2084        0.000 000 0045
deuteron-neutron magn. moment ratio                    -0.448 206 52         0.000 000 11
electron gyromagn. ratio                               1.760 859 74e11       0.000 000 15e11       s^-1 T^-1
electron gyromagn. ratio over 2 pi                     28 024.9532           0.0024                MHz T^-1
electron magn. moment                                  -928.476 412e-26      0.000 080e-26         J T^-1
electron magn. moment to Bohr magneton ratio           -1.001 159 652 1859   0.000 000 000 0038
electron magn. moment to nuclear magneton ratio        -1838.281 971 07      0.000 000 85
electron magn. moment anomaly                          1.159 652 1859e-3     0.000 000 0038e-3
electron to shielded proton magn. moment ratio         -658.227 5956         0.000 0071
electron to shielded helion magn. moment ratio         864.058 255           0.000 010
electron-deuteron magn. moment ratio                   -2143.923 493         0.000 023
electron-muon magn. moment ratio                       206.766 9894          0.000 0054
electron-neutron magn. moment ratio                    960.920 50            0.000 23
electron-proton magn. moment ratio                     -658.210 6862         0.000 0066
magn. constant                                         12.566 370 614...e-7  0                     N A^-2
magn. flux quantum                                     2.067 833 72e-15      0.000 000 18e-15      Wb
muon magn. moment                                      -4.490 447 99e-26     0.000 000 40e-26      J T^-1
muon magn. moment to Bohr magneton ratio               -4.841 970 45e-3      0.000 000 13e-3
muon magn. moment to nuclear magneton ratio            -8.890 596 98         0.000 000 23
muon-proton magn. moment ratio                         -3.183 345 118        0.000 000 089
neutron gyromagn. ratio                                1.832 471 83e8        0.000 000 46e8        s^-1 T^-1
neutron gyromagn. ratio over 2 pi                      29.164 6950           0.000 0073            MHz T^-1
neutron magn. moment                                   -0.966 236 45e-26     0.000 000 24e-26      J T^-1
neutron magn. moment to Bohr magneton ratio            -1.041 875 63e-3      0.000 000 25e-3
neutron magn. moment to nuclear magneton ratio         -1.913 042 73         0.000 000 45
neutron to shielded proton magn. moment ratio          -0.684 996 94         0.000 000 16
neutron-electron magn. moment ratio                    1.040 668 82e-3       0.000 000 25e-3
neutron-proton magn. moment ratio                      -0.684 979 34         0.000 000 16
proton gyromagn. ratio                                 2.675 222 05e8        0.000 000 23e8        s^-1 T^-1
proton gyromagn. ratio over 2 pi                       42.577 4813           0.000 0037            MHz T^-1
proton magn. moment                                    1.410 606 71e-26      0.000 000 12e-26      J T^-1
proton magn. moment to Bohr magneton ratio             1.521 032 206e-3      0.000 000 015e-3
proton magn. moment to nuclear magneton ratio          2.792 847 351         0.000 000 028
proton magn. shielding correction                      25.689e-6             0.015e-6
proton-neutron magn. moment ratio                      -1.459 898 05         0.000 000 34
shielded helion gyromagn. ratio                        2.037 894 70e8        0.000 000 18e8        s^-1 T^-1
shielded helion gyromagn. ratio over 2 pi              32.434 1015           0.000 0028            MHz T^-1
shielded helion magn. moment                           -1.074 553 024e-26    0.000 000 093e-26     J T^-1
shielded helion magn. moment to Bohr magneton ratio    -1.158 671 474e-3     0.000 000 014e-3
shielded helion magn. moment to nuclear magneton ratio -2.127 497 723        0.000 000 025
shielded helion to proton magn. moment ratio           -0.761 766 562        0.000 000 012
shielded helion to shielded proton magn. moment ratio  -0.761 786 1313       0.000 000 0033
shielded helion gyromagn. ratio                        2.037 894 70e8        0.000 000 18e8        s^-1 T^-1
shielded helion gyromagn. ratio over 2 pi              32.434 1015           0.000 0028            MHz T^-1
shielded proton magn. moment                           1.410 570 47e-26      0.000 000 12e-26      J T^-1
shielded proton magn. moment to Bohr magneton ratio    1.520 993 132e-3      0.000 000 016e-3
shielded proton magn. moment to nuclear magneton ratio 2.792 775 604         0.000 000 030
{220} lattice spacing of silicon                       192.015 5965e-12      0.000 0070e-12        m"""

txt2006 = """\
lattice spacing of silicon                             192.015 5762 e-12     0.000 0050 e-12       m
alpha particle-electron mass ratio                     7294.299 5365         0.000 0031
alpha particle mass                                    6.644 656 20 e-27     0.000 000 33 e-27     kg
alpha particle mass energy equivalent                  5.971 919 17 e-10     0.000 000 30 e-10     J
alpha particle mass energy equivalent in MeV           3727.379 109          0.000 093             MeV
alpha particle mass in u                               4.001 506 179 127     0.000 000 000 062     u
alpha particle molar mass                              4.001 506 179 127 e-3 0.000 000 000 062 e-3 kg mol^-1
alpha particle-proton mass ratio                       3.972 599 689 51      0.000 000 000 41
Angstrom star                                          1.000 014 98 e-10     0.000 000 90 e-10     m
atomic mass constant                                   1.660 538 782 e-27    0.000 000 083 e-27    kg
atomic mass constant energy equivalent                 1.492 417 830 e-10    0.000 000 074 e-10    J
atomic mass constant energy equivalent in MeV          931.494 028           0.000 023             MeV
atomic mass unit-electron volt relationship            931.494 028 e6        0.000 023 e6          eV
atomic mass unit-hartree relationship                  3.423 177 7149 e7     0.000 000 0049 e7     E_h
atomic mass unit-hertz relationship                    2.252 342 7369 e23    0.000 000 0032 e23    Hz
atomic mass unit-inverse meter relationship            7.513 006 671 e14     0.000 000 011 e14     m^-1
atomic mass unit-joule relationship                    1.492 417 830 e-10    0.000 000 074 e-10    J
atomic mass unit-kelvin relationship                   1.080 9527 e13        0.000 0019 e13        K
atomic mass unit-kilogram relationship                 1.660 538 782 e-27    0.000 000 083 e-27    kg
atomic unit of 1st hyperpolarizability                 3.206 361 533 e-53    0.000 000 081 e-53    C^3 m^3 J^-2
atomic unit of 2nd hyperpolarizability                 6.235 380 95 e-65     0.000 000 31 e-65     C^4 m^4 J^-3
atomic unit of action                                  1.054 571 628 e-34    0.000 000 053 e-34    J s
atomic unit of charge                                  1.602 176 487 e-19    0.000 000 040 e-19    C
atomic unit of charge density                          1.081 202 300 e12     0.000 000 027 e12     C m^-3
atomic unit of current                                 6.623 617 63 e-3      0.000 000 17 e-3      A
atomic unit of electric dipole mom.                    8.478 352 81 e-30     0.000 000 21 e-30     C m
atomic unit of electric field                          5.142 206 32 e11      0.000 000 13 e11      V m^-1
atomic unit of electric field gradient                 9.717 361 66 e21      0.000 000 24 e21      V m^-2
atomic unit of electric polarizability                 1.648 777 2536 e-41   0.000 000 0034 e-41   C^2 m^2 J^-1
atomic unit of electric potential                      27.211 383 86         0.000 000 68          V
atomic unit of electric quadrupole mom.                4.486 551 07 e-40     0.000 000 11 e-40     C m^2
atomic unit of energy                                  4.359 743 94 e-18     0.000 000 22 e-18     J
atomic unit of force                                   8.238 722 06 e-8      0.000 000 41 e-8      N
atomic unit of length                                  0.529 177 208 59 e-10 0.000 000 000 36 e-10 m
atomic unit of mag. dipole mom.                        1.854 801 830 e-23    0.000 000 046 e-23    J T^-1
atomic unit of mag. flux density                       2.350 517 382 e5      0.000 000 059 e5      T
atomic unit of magnetizability                         7.891 036 433 e-29    0.000 000 027 e-29    J T^-2
atomic unit of mass                                    9.109 382 15 e-31     0.000 000 45 e-31     kg
atomic unit of momentum                                1.992 851 565 e-24    0.000 000 099 e-24    kg m s^-1
atomic unit of permittivity                            1.112 650 056... e-10 (exact)               F m^-1
atomic unit of time                                    2.418 884 326 505 e-17 0.000 000 000 016 e-17 s
atomic unit of velocity                                2.187 691 2541 e6     0.000 000 0015 e6     m s^-1
Avogadro constant                                      6.022 141 79 e23      0.000 000 30 e23      mol^-1
Bohr magneton                                          927.400 915 e-26      0.000 023 e-26        J T^-1
Bohr magneton in eV/T                                  5.788 381 7555 e-5    0.000 000 0079 e-5    eV T^-1
Bohr magneton in Hz/T                                  13.996 246 04 e9      0.000 000 35 e9       Hz T^-1
Bohr magneton in inverse meters per tesla              46.686 4515           0.000 0012            m^-1 T^-1
Bohr magneton in K/T                                   0.671 7131            0.000 0012            K T^-1
Bohr radius                                            0.529 177 208 59 e-10 0.000 000 000 36 e-10 m
Boltzmann constant                                     1.380 6504 e-23       0.000 0024 e-23       J K^-1
Boltzmann constant in eV/K                             8.617 343 e-5         0.000 015 e-5         eV K^-1
Boltzmann constant in Hz/K                             2.083 6644 e10        0.000 0036 e10        Hz K^-1
Boltzmann constant in inverse meters per kelvin        69.503 56             0.000 12              m^-1 K^-1
characteristic impedance of vacuum                     376.730 313 461...    (exact)               ohm
classical electron radius                              2.817 940 2894 e-15   0.000 000 0058 e-15   m
Compton wavelength                                     2.426 310 2175 e-12   0.000 000 0033 e-12   m
Compton wavelength over 2 pi                           386.159 264 59 e-15   0.000 000 53 e-15     m
conductance quantum                                    7.748 091 7004 e-5    0.000 000 0053 e-5    S
conventional value of Josephson constant               483 597.9 e9          (exact)               Hz V^-1
conventional value of von Klitzing constant            25 812.807            (exact)               ohm
Cu x unit                                              1.002 076 99 e-13     0.000 000 28 e-13     m
deuteron-electron mag. mom. ratio                      -4.664 345 537 e-4    0.000 000 039 e-4
deuteron-electron mass ratio                           3670.482 9654         0.000 0016
deuteron g factor                                      0.857 438 2308        0.000 000 0072
deuteron mag. mom.                                     0.433 073 465 e-26    0.000 000 011 e-26    J T^-1
deuteron mag. mom. to Bohr magneton ratio              0.466 975 4556 e-3    0.000 000 0039 e-3
deuteron mag. mom. to nuclear magneton ratio           0.857 438 2308        0.000 000 0072
deuteron mass                                          3.343 583 20 e-27     0.000 000 17 e-27     kg
deuteron mass energy equivalent                        3.005 062 72 e-10     0.000 000 15 e-10     J
deuteron mass energy equivalent in MeV                 1875.612 793          0.000 047             MeV
deuteron mass in u                                     2.013 553 212 724     0.000 000 000 078     u
deuteron molar mass                                    2.013 553 212 724 e-3 0.000 000 000 078 e-3 kg mol^-1
deuteron-neutron mag. mom. ratio                       -0.448 206 52         0.000 000 11
deuteron-proton mag. mom. ratio                        0.307 012 2070        0.000 000 0024
deuteron-proton mass ratio                             1.999 007 501 08      0.000 000 000 22
deuteron rms charge radius                             2.1402 e-15           0.0028 e-15           m
electric constant                                      8.854 187 817... e-12 (exact)               F m^-1
electron charge to mass quotient                       -1.758 820 150 e11    0.000 000 044 e11     C kg^-1
electron-deuteron mag. mom. ratio                      -2143.923 498         0.000 018
electron-deuteron mass ratio                           2.724 437 1093 e-4    0.000 000 0012 e-4
electron g factor                                      -2.002 319 304 3622   0.000 000 000 0015
electron gyromag. ratio                                1.760 859 770 e11     0.000 000 044 e11     s^-1 T^-1
electron gyromag. ratio over 2 pi                      28 024.953 64         0.000 70              MHz T^-1
electron mag. mom.                                     -928.476 377 e-26     0.000 023 e-26        J T^-1
electron mag. mom. anomaly                             1.159 652 181 11 e-3  0.000 000 000 74 e-3
electron mag. mom. to Bohr magneton ratio              -1.001 159 652 181 11 0.000 000 000 000 74
electron mag. mom. to nuclear magneton ratio           -1838.281 970 92      0.000 000 80
electron mass                                          9.109 382 15 e-31     0.000 000 45 e-31     kg
electron mass energy equivalent                        8.187 104 38 e-14     0.000 000 41 e-14     J
electron mass energy equivalent in MeV                 0.510 998 910         0.000 000 013         MeV
electron mass in u                                     5.485 799 0943 e-4    0.000 000 0023 e-4    u
electron molar mass                                    5.485 799 0943 e-7    0.000 000 0023 e-7    kg mol^-1
electron-muon mag. mom. ratio                          206.766 9877          0.000 0052
electron-muon mass ratio                               4.836 331 71 e-3      0.000 000 12 e-3
electron-neutron mag. mom. ratio                       960.920 50            0.000 23
electron-neutron mass ratio                            5.438 673 4459 e-4    0.000 000 0033 e-4
electron-proton mag. mom. ratio                        -658.210 6848         0.000 0054
electron-proton mass ratio                             5.446 170 2177 e-4    0.000 000 0024 e-4
electron-tau mass ratio                                2.875 64 e-4          0.000 47 e-4
electron to alpha particle mass ratio                  1.370 933 555 70 e-4  0.000 000 000 58 e-4
electron to shielded helion mag. mom. ratio            864.058 257           0.000 010
electron to shielded proton mag. mom. ratio            -658.227 5971         0.000 0072
electron volt                                          1.602 176 487 e-19    0.000 000 040 e-19    J
electron volt-atomic mass unit relationship            1.073 544 188 e-9     0.000 000 027 e-9     u
electron volt-hartree relationship                     3.674 932 540 e-2     0.000 000 092 e-2     E_h
electron volt-hertz relationship                       2.417 989 454 e14     0.000 000 060 e14     Hz
electron volt-inverse meter relationship               8.065 544 65 e5       0.000 000 20 e5       m^-1
electron volt-joule relationship                       1.602 176 487 e-19    0.000 000 040 e-19    J
electron volt-kelvin relationship                      1.160 4505 e4         0.000 0020 e4         K
electron volt-kilogram relationship                    1.782 661 758 e-36    0.000 000 044 e-36    kg
elementary charge                                      1.602 176 487 e-19    0.000 000 040 e-19    C
elementary charge over h                               2.417 989 454 e14     0.000 000 060 e14     A J^-1
Faraday constant                                       96 485.3399           0.0024                C mol^-1
Faraday constant for conventional electric current     96 485.3401           0.0048                C_90 mol^-1
Fermi coupling constant                                1.166 37 e-5          0.000 01 e-5          GeV^-2
fine-structure constant                                7.297 352 5376 e-3    0.000 000 0050 e-3
first radiation constant                               3.741 771 18 e-16     0.000 000 19 e-16     W m^2
first radiation constant for spectral radiance         1.191 042 759 e-16    0.000 000 059 e-16    W m^2 sr^-1
hartree-atomic mass unit relationship                  2.921 262 2986 e-8    0.000 000 0042 e-8    u
hartree-electron volt relationship                     27.211 383 86         0.000 000 68          eV
Hartree energy                                         4.359 743 94 e-18     0.000 000 22 e-18     J
Hartree energy in eV                                   27.211 383 86         0.000 000 68          eV
hartree-hertz relationship                             6.579 683 920 722 e15 0.000 000 000 044 e15 Hz
hartree-inverse meter relationship                     2.194 746 313 705 e7  0.000 000 000 015 e7  m^-1
hartree-joule relationship                             4.359 743 94 e-18     0.000 000 22 e-18     J
hartree-kelvin relationship                            3.157 7465 e5         0.000 0055 e5         K
hartree-kilogram relationship                          4.850 869 34 e-35     0.000 000 24 e-35     kg
helion-electron mass ratio                             5495.885 2765         0.000 0052
helion mass                                            5.006 411 92 e-27     0.000 000 25 e-27     kg
helion mass energy equivalent                          4.499 538 64 e-10     0.000 000 22 e-10     J
helion mass energy equivalent in MeV                   2808.391 383          0.000 070             MeV
helion mass in u                                       3.014 932 2473        0.000 000 0026        u
helion molar mass                                      3.014 932 2473 e-3    0.000 000 0026 e-3    kg mol^-1
helion-proton mass ratio                               2.993 152 6713        0.000 000 0026
hertz-atomic mass unit relationship                    4.439 821 6294 e-24   0.000 000 0064 e-24   u
hertz-electron volt relationship                       4.135 667 33 e-15     0.000 000 10 e-15     eV
hertz-hartree relationship                             1.519 829 846 006 e-16 0.000 000 000010e-16 E_h
hertz-inverse meter relationship                       3.335 640 951... e-9  (exact)               m^-1
hertz-joule relationship                               6.626 068 96 e-34     0.000 000 33 e-34     J
hertz-kelvin relationship                              4.799 2374 e-11       0.000 0084 e-11       K
hertz-kilogram relationship                            7.372 496 00 e-51     0.000 000 37 e-51     kg
inverse fine-structure constant                        137.035 999 679       0.000 000 094
inverse meter-atomic mass unit relationship            1.331 025 0394 e-15   0.000 000 0019 e-15   u
inverse meter-electron volt relationship               1.239 841 875 e-6     0.000 000 031 e-6     eV
inverse meter-hartree relationship                     4.556 335 252 760 e-8 0.000 000 000 030 e-8 E_h
inverse meter-hertz relationship                       299 792 458           (exact)               Hz
inverse meter-joule relationship                       1.986 445 501 e-25    0.000 000 099 e-25    J
inverse meter-kelvin relationship                      1.438 7752 e-2        0.000 0025 e-2        K
inverse meter-kilogram relationship                    2.210 218 70 e-42     0.000 000 11 e-42     kg
inverse of conductance quantum                         12 906.403 7787       0.000 0088            ohm
Josephson constant                                     483 597.891 e9        0.012 e9              Hz V^-1
joule-atomic mass unit relationship                    6.700 536 41 e9       0.000 000 33 e9       u
joule-electron volt relationship                       6.241 509 65 e18      0.000 000 16 e18      eV
joule-hartree relationship                             2.293 712 69 e17      0.000 000 11 e17      E_h
joule-hertz relationship                               1.509 190 450 e33     0.000 000 075 e33     Hz
joule-inverse meter relationship                       5.034 117 47 e24      0.000 000 25 e24      m^-1
joule-kelvin relationship                              7.242 963 e22         0.000 013 e22         K
joule-kilogram relationship                            1.112 650 056... e-17 (exact)               kg
kelvin-atomic mass unit relationship                   9.251 098 e-14        0.000 016 e-14        u
kelvin-electron volt relationship                      8.617 343 e-5         0.000 015 e-5         eV
kelvin-hartree relationship                            3.166 8153 e-6        0.000 0055 e-6        E_h
kelvin-hertz relationship                              2.083 6644 e10        0.000 0036 e10        Hz
kelvin-inverse meter relationship                      69.503 56             0.000 12              m^-1
kelvin-joule relationship                              1.380 6504 e-23       0.000 0024 e-23       J
kelvin-kilogram relationship                           1.536 1807 e-40       0.000 0027 e-40       kg
kilogram-atomic mass unit relationship                 6.022 141 79 e26      0.000 000 30 e26      u
kilogram-electron volt relationship                    5.609 589 12 e35      0.000 000 14 e35      eV
kilogram-hartree relationship                          2.061 486 16 e34      0.000 000 10 e34      E_h
kilogram-hertz relationship                            1.356 392 733 e50     0.000 000 068 e50     Hz
kilogram-inverse meter relationship                    4.524 439 15 e41      0.000 000 23 e41      m^-1
kilogram-joule relationship                            8.987 551 787... e16  (exact)               J
kilogram-kelvin relationship                           6.509 651 e39         0.000 011 e39         K
lattice parameter of silicon                           543.102 064 e-12      0.000 014 e-12        m
Loschmidt constant (273.15 K, 101.325 kPa)             2.686 7774 e25        0.000 0047 e25        m^-3
mag. constant                                          12.566 370 614... e-7 (exact)               N A^-2
mag. flux quantum                                      2.067 833 667 e-15    0.000 000 052 e-15    Wb
molar gas constant                                     8.314 472             0.000 015             J mol^-1 K^-1
molar mass constant                                    1 e-3                 (exact)               kg mol^-1
molar mass of carbon-12                                12 e-3                (exact)               kg mol^-1
molar Planck constant                                  3.990 312 6821 e-10   0.000 000 0057 e-10   J s mol^-1
molar Planck constant times c                          0.119 626 564 72      0.000 000 000 17      J m mol^-1
molar volume of ideal gas (273.15 K, 100 kPa)          22.710 981 e-3        0.000 040 e-3         m^3 mol^-1
molar volume of ideal gas (273.15 K, 101.325 kPa)      22.413 996 e-3        0.000 039 e-3         m^3 mol^-1
molar volume of silicon                                12.058 8349 e-6       0.000 0011 e-6        m^3 mol^-1
Mo x unit                                              1.002 099 55 e-13     0.000 000 53 e-13     m
muon Compton wavelength                                11.734 441 04 e-15    0.000 000 30 e-15     m
muon Compton wavelength over 2 pi                      1.867 594 295 e-15    0.000 000 047 e-15    m
muon-electron mass ratio                               206.768 2823          0.000 0052
muon g factor                                          -2.002 331 8414       0.000 000 0012
muon mag. mom.                                         -4.490 447 86 e-26    0.000 000 16 e-26     J T^-1
muon mag. mom. anomaly                                 1.165 920 69 e-3      0.000 000 60 e-3
muon mag. mom. to Bohr magneton ratio                  -4.841 970 49 e-3     0.000 000 12 e-3
muon mag. mom. to nuclear magneton ratio               -8.890 597 05         0.000 000 23
muon mass                                              1.883 531 30 e-28     0.000 000 11 e-28     kg
muon mass energy equivalent                            1.692 833 510 e-11    0.000 000 095 e-11    J
muon mass energy equivalent in MeV                     105.658 3668          0.000 0038            MeV
muon mass in u                                         0.113 428 9256        0.000 000 0029        u
muon molar mass                                        0.113 428 9256 e-3    0.000 000 0029 e-3    kg mol^-1
muon-neutron mass ratio                                0.112 454 5167        0.000 000 0029
muon-proton mag. mom. ratio                            -3.183 345 137        0.000 000 085
muon-proton mass ratio                                 0.112 609 5261        0.000 000 0029
muon-tau mass ratio                                    5.945 92 e-2          0.000 97 e-2
natural unit of action                                 1.054 571 628 e-34    0.000 000 053 e-34    J s
natural unit of action in eV s                         6.582 118 99 e-16     0.000 000 16 e-16     eV s
natural unit of energy                                 8.187 104 38 e-14     0.000 000 41 e-14     J
natural unit of energy in MeV                          0.510 998 910         0.000 000 013         MeV
natural unit of length                                 386.159 264 59 e-15   0.000 000 53 e-15     m
natural unit of mass                                   9.109 382 15 e-31     0.000 000 45 e-31     kg
natural unit of momentum                               2.730 924 06 e-22     0.000 000 14 e-22     kg m s^-1
natural unit of momentum in MeV/c                      0.510 998 910         0.000 000 013         MeV/c
natural unit of time                                   1.288 088 6570 e-21   0.000 000 0018 e-21   s
natural unit of velocity                               299 792 458           (exact)               m s^-1
neutron Compton wavelength                             1.319 590 8951 e-15   0.000 000 0020 e-15   m
neutron Compton wavelength over 2 pi                   0.210 019 413 82 e-15 0.000 000 000 31 e-15 m
neutron-electron mag. mom. ratio                       1.040 668 82 e-3      0.000 000 25 e-3
neutron-electron mass ratio                            1838.683 6605         0.000 0011
neutron g factor                                       -3.826 085 45         0.000 000 90
neutron gyromag. ratio                                 1.832 471 85 e8       0.000 000 43 e8       s^-1 T^-1
neutron gyromag. ratio over 2 pi                       29.164 6954           0.000 0069            MHz T^-1
neutron mag. mom.                                      -0.966 236 41 e-26    0.000 000 23 e-26     J T^-1
neutron mag. mom. to Bohr magneton ratio               -1.041 875 63 e-3     0.000 000 25 e-3
neutron mag. mom. to nuclear magneton ratio            -1.913 042 73         0.000 000 45
neutron mass                                           1.674 927 211 e-27    0.000 000 084 e-27    kg
neutron mass energy equivalent                         1.505 349 505 e-10    0.000 000 075 e-10    J
neutron mass energy equivalent in MeV                  939.565 346           0.000 023             MeV
neutron mass in u                                      1.008 664 915 97      0.000 000 000 43      u
neutron molar mass                                     1.008 664 915 97 e-3  0.000 000 000 43 e-3  kg mol^-1
neutron-muon mass ratio                                8.892 484 09          0.000 000 23
neutron-proton mag. mom. ratio                         -0.684 979 34         0.000 000 16
neutron-proton mass ratio                              1.001 378 419 18      0.000 000 000 46
neutron-tau mass ratio                                 0.528 740             0.000 086
neutron to shielded proton mag. mom. ratio             -0.684 996 94         0.000 000 16
Newtonian constant of gravitation                      6.674 28 e-11         0.000 67 e-11         m^3 kg^-1 s^-2
Newtonian constant of gravitation over h-bar c         6.708 81 e-39         0.000 67 e-39         (GeV/c^2)^-2
nuclear magneton                                       5.050 783 24 e-27     0.000 000 13 e-27     J T^-1
nuclear magneton in eV/T                               3.152 451 2326 e-8    0.000 000 0045 e-8    eV T^-1
nuclear magneton in inverse meters per tesla           2.542 623 616 e-2     0.000 000 064 e-2     m^-1 T^-1
nuclear magneton in K/T                                3.658 2637 e-4        0.000 0064 e-4        K T^-1
nuclear magneton in MHz/T                              7.622 593 84          0.000 000 19          MHz T^-1
Planck constant                                        6.626 068 96 e-34     0.000 000 33 e-34     J s
Planck constant in eV s                                4.135 667 33 e-15     0.000 000 10 e-15     eV s
Planck constant over 2 pi                              1.054 571 628 e-34    0.000 000 053 e-34    J s
Planck constant over 2 pi in eV s                      6.582 118 99 e-16     0.000 000 16 e-16     eV s
Planck constant over 2 pi times c in MeV fm            197.326 9631          0.000 0049            MeV fm
Planck length                                          1.616 252 e-35        0.000 081 e-35        m
Planck mass                                            2.176 44 e-8          0.000 11 e-8          kg
Planck mass energy equivalent in GeV                   1.220 892 e19         0.000 061 e19         GeV
Planck temperature                                     1.416 785 e32         0.000 071 e32         K
Planck time                                            5.391 24 e-44         0.000 27 e-44         s
proton charge to mass quotient                         9.578 833 92 e7       0.000 000 24 e7       C kg^-1
proton Compton wavelength                              1.321 409 8446 e-15   0.000 000 0019 e-15   m
proton Compton wavelength over 2 pi                    0.210 308 908 61 e-15 0.000 000 000 30 e-15 m
proton-electron mass ratio                             1836.152 672 47       0.000 000 80
proton g factor                                        5.585 694 713         0.000 000 046
proton gyromag. ratio                                  2.675 222 099 e8      0.000 000 070 e8      s^-1 T^-1
proton gyromag. ratio over 2 pi                        42.577 4821           0.000 0011            MHz T^-1
proton mag. mom.                                       1.410 606 662 e-26    0.000 000 037 e-26    J T^-1
proton mag. mom. to Bohr magneton ratio                1.521 032 209 e-3     0.000 000 012 e-3
proton mag. mom. to nuclear magneton ratio             2.792 847 356         0.000 000 023
proton mag. shielding correction                       25.694 e-6            0.014 e-6
proton mass                                            1.672 621 637 e-27    0.000 000 083 e-27    kg
proton mass energy equivalent                          1.503 277 359 e-10    0.000 000 075 e-10    J
proton mass energy equivalent in MeV                   938.272 013           0.000 023             MeV
proton mass in u                                       1.007 276 466 77      0.000 000 000 10      u
proton molar mass                                      1.007 276 466 77 e-3  0.000 000 000 10 e-3  kg mol^-1
proton-muon mass ratio                                 8.880 243 39          0.000 000 23
proton-neutron mag. mom. ratio                         -1.459 898 06         0.000 000 34
proton-neutron mass ratio                              0.998 623 478 24      0.000 000 000 46
proton rms charge radius                               0.8768 e-15           0.0069 e-15           m
proton-tau mass ratio                                  0.528 012             0.000 086
quantum of circulation                                 3.636 947 5199 e-4    0.000 000 0050 e-4    m^2 s^-1
quantum of circulation times 2                         7.273 895 040 e-4     0.000 000 010 e-4     m^2 s^-1
Rydberg constant                                       10 973 731.568 527    0.000 073             m^-1
Rydberg constant times c in Hz                         3.289 841 960 361 e15 0.000 000 000 022 e15 Hz
Rydberg constant times hc in eV                        13.605 691 93         0.000 000 34          eV
Rydberg constant times hc in J                         2.179 871 97 e-18     0.000 000 11 e-18     J
Sackur-Tetrode constant (1 K, 100 kPa)                 -1.151 7047           0.000 0044
Sackur-Tetrode constant (1 K, 101.325 kPa)             -1.164 8677           0.000 0044
second radiation constant                              1.438 7752 e-2        0.000 0025 e-2        m K
shielded helion gyromag. ratio                         2.037 894 730 e8      0.000 000 056 e8      s^-1 T^-1
shielded helion gyromag. ratio over 2 pi               32.434 101 98         0.000 000 90          MHz T^-1
shielded helion mag. mom.                              -1.074 552 982 e-26   0.000 000 030 e-26    J T^-1
shielded helion mag. mom. to Bohr magneton ratio       -1.158 671 471 e-3    0.000 000 014 e-3
shielded helion mag. mom. to nuclear magneton ratio    -2.127 497 718        0.000 000 025
shielded helion to proton mag. mom. ratio              -0.761 766 558        0.000 000 011
shielded helion to shielded proton mag. mom. ratio     -0.761 786 1313       0.000 000 0033
shielded proton gyromag. ratio                         2.675 153 362 e8      0.000 000 073 e8      s^-1 T^-1
shielded proton gyromag. ratio over 2 pi               42.576 3881           0.000 0012            MHz T^-1
shielded proton mag. mom.                              1.410 570 419 e-26    0.000 000 038 e-26    J T^-1
shielded proton mag. mom. to Bohr magneton ratio       1.520 993 128 e-3     0.000 000 017 e-3
shielded proton mag. mom. to nuclear magneton ratio    2.792 775 598         0.000 000 030
speed of light in vacuum                               299 792 458           (exact)               m s^-1
standard acceleration of gravity                       9.806 65              (exact)               m s^-2
standard atmosphere                                    101 325               (exact)               Pa
Stefan-Boltzmann constant                              5.670 400 e-8         0.000 040 e-8         W m^-2 K^-4
tau Compton wavelength                                 0.697 72 e-15         0.000 11 e-15         m
tau Compton wavelength over 2 pi                       0.111 046 e-15        0.000 018 e-15        m
tau-electron mass ratio                                3477.48               0.57
tau mass                                               3.167 77 e-27         0.000 52 e-27         kg
tau mass energy equivalent                             2.847 05 e-10         0.000 46 e-10         J
tau mass energy equivalent in MeV                      1776.99               0.29                  MeV
tau mass in u                                          1.907 68              0.000 31              u
tau molar mass                                         1.907 68 e-3          0.000 31 e-3          kg mol^-1
tau-muon mass ratio                                    16.8183               0.0027
tau-neutron mass ratio                                 1.891 29              0.000 31
tau-proton mass ratio                                  1.893 90              0.000 31
Thomson cross section                                  0.665 245 8558 e-28   0.000 000 0027 e-28   m^2
triton-electron mag. mom. ratio                        -1.620 514 423 e-3    0.000 000 021 e-3
triton-electron mass ratio                             5496.921 5269         0.000 0051
triton g factor                                        5.957 924 896         0.000 000 076
triton mag. mom.                                       1.504 609 361 e-26    0.000 000 042 e-26    J T^-1
triton mag. mom. to Bohr magneton ratio                1.622 393 657 e-3     0.000 000 021 e-3
triton mag. mom. to nuclear magneton ratio             2.978 962 448         0.000 000 038
triton mass                                            5.007 355 88 e-27     0.000 000 25 e-27     kg
triton mass energy equivalent                          4.500 387 03 e-10     0.000 000 22 e-10     J
triton mass energy equivalent in MeV                   2808.920 906          0.000 070             MeV
triton mass in u                                       3.015 500 7134        0.000 000 0025        u
triton molar mass                                      3.015 500 7134 e-3    0.000 000 0025 e-3    kg mol^-1
triton-neutron mag. mom. ratio                         -1.557 185 53         0.000 000 37
triton-proton mag. mom. ratio                          1.066 639 908         0.000 000 010
triton-proton mass ratio                               2.993 717 0309        0.000 000 0025
unified atomic mass unit                               1.660 538 782 e-27    0.000 000 083 e-27    kg
von Klitzing constant                                  25 812.807 557        0.000 018             ohm
weak mixing angle                                      0.222 55              0.000 56
Wien frequency displacement law constant               5.878 933 e10         0.000 010 e10         Hz K^-1
Wien wavelength displacement law constant              2.897 7685 e-3        0.000 0051 e-3        m K"""

txt2010 = """\
{220} lattice spacing of silicon                       192.015 5714 e-12     0.000 0032 e-12       m
alpha particle-electron mass ratio                     7294.299 5361         0.000 0029
alpha particle mass                                    6.644 656 75 e-27     0.000 000 29 e-27     kg
alpha particle mass energy equivalent                  5.971 919 67 e-10     0.000 000 26 e-10     J
alpha particle mass energy equivalent in MeV           3727.379 240          0.000 082             MeV
alpha particle mass in u                               4.001 506 179 125     0.000 000 000 062     u
alpha particle molar mass                              4.001 506 179 125 e-3 0.000 000 000 062 e-3 kg mol^-1
alpha particle-proton mass ratio                       3.972 599 689 33      0.000 000 000 36
Angstrom star                                          1.000 014 95 e-10     0.000 000 90 e-10     m
atomic mass constant                                   1.660 538 921 e-27    0.000 000 073 e-27    kg
atomic mass constant energy equivalent                 1.492 417 954 e-10    0.000 000 066 e-10    J
atomic mass constant energy equivalent in MeV          931.494 061           0.000 021             MeV
atomic mass unit-electron volt relationship            931.494 061 e6        0.000 021 e6          eV
atomic mass unit-hartree relationship                  3.423 177 6845 e7     0.000 000 0024 e7     E_h
atomic mass unit-hertz relationship                    2.252 342 7168 e23    0.000 000 0016 e23    Hz
atomic mass unit-inverse meter relationship            7.513 006 6042 e14    0.000 000 0053 e14    m^-1
atomic mass unit-joule relationship                    1.492 417 954 e-10    0.000 000 066 e-10    J
atomic mass unit-kelvin relationship                   1.080 954 08 e13      0.000 000 98 e13      K
atomic mass unit-kilogram relationship                 1.660 538 921 e-27    0.000 000 073 e-27    kg
atomic unit of 1st hyperpolarizability                 3.206 361 449 e-53    0.000 000 071 e-53    C^3 m^3 J^-2
atomic unit of 2nd hyperpolarizability                 6.235 380 54 e-65     0.000 000 28 e-65     C^4 m^4 J^-3
atomic unit of action                                  1.054 571 726 e-34    0.000 000 047 e-34    J s
atomic unit of charge                                  1.602 176 565 e-19    0.000 000 035 e-19    C
atomic unit of charge density                          1.081 202 338 e12     0.000 000 024 e12     C m^-3
atomic unit of current                                 6.623 617 95 e-3      0.000 000 15 e-3      A
atomic unit of electric dipole mom.                    8.478 353 26 e-30     0.000 000 19 e-30     C m
atomic unit of electric field                          5.142 206 52 e11      0.000 000 11 e11      V m^-1
atomic unit of electric field gradient                 9.717 362 00 e21      0.000 000 21 e21      V m^-2
atomic unit of electric polarizability                 1.648 777 2754 e-41   0.000 000 0016 e-41   C^2 m^2 J^-1
atomic unit of electric potential                      27.211 385 05         0.000 000 60          V
atomic unit of electric quadrupole mom.                4.486 551 331 e-40    0.000 000 099 e-40    C m^2
atomic unit of energy                                  4.359 744 34 e-18     0.000 000 19 e-18     J
atomic unit of force                                   8.238 722 78 e-8      0.000 000 36 e-8      N
atomic unit of length                                  0.529 177 210 92 e-10 0.000 000 000 17 e-10 m
atomic unit of mag. dipole mom.                        1.854 801 936 e-23    0.000 000 041 e-23    J T^-1
atomic unit of mag. flux density                       2.350 517 464 e5      0.000 000 052 e5      T
atomic unit of magnetizability                         7.891 036 607 e-29    0.000 000 013 e-29    J T^-2
atomic unit of mass                                    9.109 382 91 e-31     0.000 000 40 e-31     kg
atomic unit of mom.um                                  1.992 851 740 e-24    0.000 000 088 e-24    kg m s^-1
atomic unit of permittivity                            1.112 650 056... e-10 (exact)               F m^-1
atomic unit of time                                    2.418 884 326 502e-17 0.000 000 000 012e-17 s
atomic unit of velocity                                2.187 691 263 79 e6   0.000 000 000 71 e6   m s^-1
Avogadro constant                                      6.022 141 29 e23      0.000 000 27 e23      mol^-1
Bohr magneton                                          927.400 968 e-26      0.000 020 e-26        J T^-1
Bohr magneton in eV/T                                  5.788 381 8066 e-5    0.000 000 0038 e-5    eV T^-1
Bohr magneton in Hz/T                                  13.996 245 55 e9      0.000 000 31 e9       Hz T^-1
Bohr magneton in inverse meters per tesla              46.686 4498           0.000 0010            m^-1 T^-1
Bohr magneton in K/T                                   0.671 713 88          0.000 000 61          K T^-1
Bohr radius                                            0.529 177 210 92 e-10 0.000 000 000 17 e-10 m
Boltzmann constant                                     1.380 6488 e-23       0.000 0013 e-23       J K^-1
Boltzmann constant in eV/K                             8.617 3324 e-5        0.000 0078 e-5        eV K^-1
Boltzmann constant in Hz/K                             2.083 6618 e10        0.000 0019 e10        Hz K^-1
Boltzmann constant in inverse meters per kelvin        69.503 476            0.000 063             m^-1 K^-1
characteristic impedance of vacuum                     376.730 313 461...    (exact)               ohm
classical electron radius                              2.817 940 3267 e-15   0.000 000 0027 e-15   m
Compton wavelength                                     2.426 310 2389 e-12   0.000 000 0016 e-12   m
Compton wavelength over 2 pi                           386.159 268 00 e-15   0.000 000 25 e-15     m
conductance quantum                                    7.748 091 7346 e-5    0.000 000 0025 e-5    S
conventional value of Josephson constant               483 597.9 e9          (exact)               Hz V^-1
conventional value of von Klitzing constant            25 812.807            (exact)               ohm
Cu x unit                                              1.002 076 97 e-13     0.000 000 28 e-13     m
deuteron-electron mag. mom. ratio                      -4.664 345 537 e-4    0.000 000 039 e-4
deuteron-electron mass ratio                           3670.482 9652         0.000 0015
deuteron g factor                                      0.857 438 2308        0.000 000 0072
deuteron mag. mom.                                     0.433 073 489 e-26    0.000 000 010 e-26    J T^-1
deuteron mag. mom. to Bohr magneton ratio              0.466 975 4556 e-3    0.000 000 0039 e-3
deuteron mag. mom. to nuclear magneton ratio           0.857 438 2308        0.000 000 0072
deuteron mass                                          3.343 583 48 e-27     0.000 000 15 e-27     kg
deuteron mass energy equivalent                        3.005 062 97 e-10     0.000 000 13 e-10     J
deuteron mass energy equivalent in MeV                 1875.612 859          0.000 041             MeV
deuteron mass in u                                     2.013 553 212 712     0.000 000 000 077     u
deuteron molar mass                                    2.013 553 212 712 e-3 0.000 000 000 077 e-3 kg mol^-1
deuteron-neutron mag. mom. ratio                       -0.448 206 52         0.000 000 11
deuteron-proton mag. mom. ratio                        0.307 012 2070        0.000 000 0024
deuteron-proton mass ratio                             1.999 007 500 97      0.000 000 000 18
deuteron rms charge radius                             2.1424 e-15           0.0021 e-15           m
electric constant                                      8.854 187 817... e-12 (exact)               F m^-1
electron charge to mass quotient                       -1.758 820 088 e11    0.000 000 039 e11     C kg^-1
electron-deuteron mag. mom. ratio                      -2143.923 498         0.000 018
electron-deuteron mass ratio                           2.724 437 1095 e-4    0.000 000 0011 e-4
electron g factor                                      -2.002 319 304 361 53 0.000 000 000 000 53
electron gyromag. ratio                                1.760 859 708 e11     0.000 000 039 e11     s^-1 T^-1
electron gyromag. ratio over 2 pi                      28 024.952 66         0.000 62              MHz T^-1
electron-helion mass ratio                             1.819 543 0761 e-4    0.000 000 0017 e-4
electron mag. mom.                                     -928.476 430 e-26     0.000 021 e-26        J T^-1
electron mag. mom. anomaly                             1.159 652 180 76 e-3  0.000 000 000 27 e-3
electron mag. mom. to Bohr magneton ratio              -1.001 159 652 180 76 0.000 000 000 000 27
electron mag. mom. to nuclear magneton ratio           -1838.281 970 90      0.000 000 75
electron mass                                          9.109 382 91 e-31     0.000 000 40 e-31     kg
electron mass energy equivalent                        8.187 105 06 e-14     0.000 000 36 e-14     J
electron mass energy equivalent in MeV                 0.510 998 928         0.000 000 011         MeV
electron mass in u                                     5.485 799 0946 e-4    0.000 000 0022 e-4    u
electron molar mass                                    5.485 799 0946 e-7    0.000 000 0022 e-7    kg mol^-1
electron-muon mag. mom. ratio                          206.766 9896          0.000 0052
electron-muon mass ratio                               4.836 331 66 e-3      0.000 000 12 e-3
electron-neutron mag. mom. ratio                       960.920 50            0.000 23
electron-neutron mass ratio                            5.438 673 4461 e-4    0.000 000 0032 e-4
electron-proton mag. mom. ratio                        -658.210 6848         0.000 0054
electron-proton mass ratio                             5.446 170 2178 e-4    0.000 000 0022 e-4
electron-tau mass ratio                                2.875 92 e-4          0.000 26 e-4
electron to alpha particle mass ratio                  1.370 933 555 78 e-4  0.000 000 000 55 e-4
electron to shielded helion mag. mom. ratio            864.058 257           0.000 010
electron to shielded proton mag. mom. ratio            -658.227 5971         0.000 0072
electron-triton mass ratio                             1.819 200 0653 e-4    0.000 000 0017 e-4
electron volt                                          1.602 176 565 e-19    0.000 000 035 e-19    J
electron volt-atomic mass unit relationship            1.073 544 150 e-9     0.000 000 024 e-9     u
electron volt-hartree relationship                     3.674 932 379 e-2     0.000 000 081 e-2     E_h
electron volt-hertz relationship                       2.417 989 348 e14     0.000 000 053 e14     Hz
electron volt-inverse meter relationship               8.065 544 29 e5       0.000 000 18 e5       m^-1
electron volt-joule relationship                       1.602 176 565 e-19    0.000 000 035 e-19    J
electron volt-kelvin relationship                      1.160 4519 e4         0.000 0011 e4         K
electron volt-kilogram relationship                    1.782 661 845 e-36    0.000 000 039 e-36    kg
elementary charge                                      1.602 176 565 e-19    0.000 000 035 e-19    C
elementary charge over h                               2.417 989 348 e14     0.000 000 053 e14     A J^-1
Faraday constant                                       96 485.3365           0.0021                C mol^-1
Faraday constant for conventional electric current     96 485.3321           0.0043                C_90 mol^-1
Fermi coupling constant                                1.166 364 e-5         0.000 005 e-5         GeV^-2
fine-structure constant                                7.297 352 5698 e-3    0.000 000 0024 e-3
first radiation constant                               3.741 771 53 e-16     0.000 000 17 e-16     W m^2
first radiation constant for spectral radiance         1.191 042 869 e-16    0.000 000 053 e-16    W m^2 sr^-1
hartree-atomic mass unit relationship                  2.921 262 3246 e-8    0.000 000 0021 e-8    u
hartree-electron volt relationship                     27.211 385 05         0.000 000 60          eV
Hartree energy                                         4.359 744 34 e-18     0.000 000 19 e-18     J
Hartree energy in eV                                   27.211 385 05         0.000 000 60          eV
hartree-hertz relationship                             6.579 683 920 729 e15 0.000 000 000 033 e15 Hz
hartree-inverse meter relationship                     2.194 746 313 708 e7  0.000 000 000 011 e7  m^-1
hartree-joule relationship                             4.359 744 34 e-18     0.000 000 19 e-18     J
hartree-kelvin relationship                            3.157 7504 e5         0.000 0029 e5         K
hartree-kilogram relationship                          4.850 869 79 e-35     0.000 000 21 e-35     kg
helion-electron mass ratio                             5495.885 2754         0.000 0050
helion g factor                                        -4.255 250 613        0.000 000 050
helion mag. mom.                                       -1.074 617 486 e-26   0.000 000 027 e-26    J T^-1
helion mag. mom. to Bohr magneton ratio                -1.158 740 958 e-3    0.000 000 014 e-3
helion mag. mom. to nuclear magneton ratio             -2.127 625 306        0.000 000 025
helion mass                                            5.006 412 34 e-27     0.000 000 22 e-27     kg
helion mass energy equivalent                          4.499 539 02 e-10     0.000 000 20 e-10     J
helion mass energy equivalent in MeV                   2808.391 482          0.000 062             MeV
helion mass in u                                       3.014 932 2468        0.000 000 0025        u
helion molar mass                                      3.014 932 2468 e-3    0.000 000 0025 e-3    kg mol^-1
helion-proton mass ratio                               2.993 152 6707        0.000 000 0025
hertz-atomic mass unit relationship                    4.439 821 6689 e-24   0.000 000 0031 e-24   u
hertz-electron volt relationship                       4.135 667 516 e-15    0.000 000 091 e-15    eV
hertz-hartree relationship                             1.519 829 8460045e-16 0.000 000 0000076e-16 E_h
hertz-inverse meter relationship                       3.335 640 951... e-9  (exact)               m^-1
hertz-joule relationship                               6.626 069 57 e-34     0.000 000 29 e-34     J
hertz-kelvin relationship                              4.799 2434 e-11       0.000 0044 e-11       K
hertz-kilogram relationship                            7.372 496 68 e-51     0.000 000 33 e-51     kg
inverse fine-structure constant                        137.035 999 074       0.000 000 044
inverse meter-atomic mass unit relationship            1.331 025 051 20 e-15 0.000 000 000 94 e-15 u
inverse meter-electron volt relationship               1.239 841 930 e-6     0.000 000 027 e-6     eV
inverse meter-hartree relationship                     4.556 335 252 755 e-8 0.000 000 000 023 e-8 E_h
inverse meter-hertz relationship                       299 792 458           (exact)               Hz
inverse meter-joule relationship                       1.986 445 684 e-25    0.000 000 088 e-25    J
inverse meter-kelvin relationship                      1.438 7770 e-2        0.000 0013 e-2        K
inverse meter-kilogram relationship                    2.210 218 902 e-42    0.000 000 098 e-42    kg
inverse of conductance quantum                         12 906.403 7217       0.000 0042            ohm
Josephson constant                                     483 597.870 e9        0.011 e9              Hz V^-1
joule-atomic mass unit relationship                    6.700 535 85 e9       0.000 000 30 e9       u
joule-electron volt relationship                       6.241 509 34 e18      0.000 000 14 e18      eV
joule-hartree relationship                             2.293 712 48 e17      0.000 000 10 e17      E_h
joule-hertz relationship                               1.509 190 311 e33     0.000 000 067 e33     Hz
joule-inverse meter relationship                       5.034 117 01 e24      0.000 000 22 e24      m^-1
joule-kelvin relationship                              7.242 9716 e22        0.000 0066 e22        K
joule-kilogram relationship                            1.112 650 056... e-17 (exact)               kg
kelvin-atomic mass unit relationship                   9.251 0868 e-14       0.000 0084 e-14       u
kelvin-electron volt relationship                      8.617 3324 e-5        0.000 0078 e-5        eV
kelvin-hartree relationship                            3.166 8114 e-6        0.000 0029 e-6        E_h
kelvin-hertz relationship                              2.083 6618 e10        0.000 0019 e10        Hz
kelvin-inverse meter relationship                      69.503 476            0.000 063             m^-1
kelvin-joule relationship                              1.380 6488 e-23       0.000 0013 e-23       J
kelvin-kilogram relationship                           1.536 1790 e-40       0.000 0014 e-40       kg
kilogram-atomic mass unit relationship                 6.022 141 29 e26      0.000 000 27 e26      u
kilogram-electron volt relationship                    5.609 588 85 e35      0.000 000 12 e35      eV
kilogram-hartree relationship                          2.061 485 968 e34     0.000 000 091 e34     E_h
kilogram-hertz relationship                            1.356 392 608 e50     0.000 000 060 e50     Hz
kilogram-inverse meter relationship                    4.524 438 73 e41      0.000 000 20 e41      m^-1
kilogram-joule relationship                            8.987 551 787... e16  (exact)               J
kilogram-kelvin relationship                           6.509 6582 e39        0.000 0059 e39        K
lattice parameter of silicon                           543.102 0504 e-12     0.000 0089 e-12       m
Loschmidt constant (273.15 K, 100 kPa)                 2.651 6462 e25        0.000 0024 e25        m^-3
Loschmidt constant (273.15 K, 101.325 kPa)             2.686 7805 e25        0.000 0024 e25        m^-3
mag. constant                                          12.566 370 614... e-7 (exact)               N A^-2
mag. flux quantum                                      2.067 833 758 e-15    0.000 000 046 e-15    Wb
molar gas constant                                     8.314 4621            0.000 0075            J mol^-1 K^-1
molar mass constant                                    1 e-3                 (exact)               kg mol^-1
molar mass of carbon-12                                12 e-3                (exact)               kg mol^-1
molar Planck constant                                  3.990 312 7176 e-10   0.000 000 0028 e-10   J s mol^-1
molar Planck constant times c                          0.119 626 565 779     0.000 000 000 084     J m mol^-1
molar volume of ideal gas (273.15 K, 100 kPa)          22.710 953 e-3        0.000 021 e-3         m^3 mol^-1
molar volume of ideal gas (273.15 K, 101.325 kPa)      22.413 968 e-3        0.000 020 e-3         m^3 mol^-1
molar volume of silicon                                12.058 833 01 e-6     0.000 000 80 e-6      m^3 mol^-1
Mo x unit                                              1.002 099 52 e-13     0.000 000 53 e-13     m
muon Compton wavelength                                11.734 441 03 e-15    0.000 000 30 e-15     m
muon Compton wavelength over 2 pi                      1.867 594 294 e-15    0.000 000 047 e-15    m
muon-electron mass ratio                               206.768 2843          0.000 0052
muon g factor                                          -2.002 331 8418       0.000 000 0013
muon mag. mom.                                         -4.490 448 07 e-26    0.000 000 15 e-26     J T^-1
muon mag. mom. anomaly                                 1.165 920 91 e-3      0.000 000 63 e-3
muon mag. mom. to Bohr magneton ratio                  -4.841 970 44 e-3     0.000 000 12 e-3
muon mag. mom. to nuclear magneton ratio               -8.890 596 97         0.000 000 22
muon mass                                              1.883 531 475 e-28    0.000 000 096 e-28    kg
muon mass energy equivalent                            1.692 833 667 e-11    0.000 000 086 e-11    J
muon mass energy equivalent in MeV                     105.658 3715          0.000 0035            MeV
muon mass in u                                         0.113 428 9267        0.000 000 0029        u
muon molar mass                                        0.113 428 9267 e-3    0.000 000 0029 e-3    kg mol^-1
muon-neutron mass ratio                                0.112 454 5177        0.000 000 0028
muon-proton mag. mom. ratio                            -3.183 345 107        0.000 000 084
muon-proton mass ratio                                 0.112 609 5272        0.000 000 0028
muon-tau mass ratio                                    5.946 49 e-2          0.000 54 e-2
natural unit of action                                 1.054 571 726 e-34    0.000 000 047 e-34    J s
natural unit of action in eV s                         6.582 119 28 e-16     0.000 000 15 e-16     eV s
natural unit of energy                                 8.187 105 06 e-14     0.000 000 36 e-14     J
natural unit of energy in MeV                          0.510 998 928         0.000 000 011         MeV
natural unit of length                                 386.159 268 00 e-15   0.000 000 25 e-15     m
natural unit of mass                                   9.109 382 91 e-31     0.000 000 40 e-31     kg
natural unit of mom.um                                 2.730 924 29 e-22     0.000 000 12 e-22     kg m s^-1
natural unit of mom.um in MeV/c                        0.510 998 928         0.000 000 011         MeV/c
natural unit of time                                   1.288 088 668 33 e-21 0.000 000 000 83 e-21 s
natural unit of velocity                               299 792 458           (exact)               m s^-1
neutron Compton wavelength                             1.319 590 9068 e-15   0.000 000 0011 e-15   m
neutron Compton wavelength over 2 pi                   0.210 019 415 68 e-15 0.000 000 000 17 e-15 m
neutron-electron mag. mom. ratio                       1.040 668 82 e-3      0.000 000 25 e-3
neutron-electron mass ratio                            1838.683 6605         0.000 0011
neutron g factor                                       -3.826 085 45         0.000 000 90
neutron gyromag. ratio                                 1.832 471 79 e8       0.000 000 43 e8       s^-1 T^-1
neutron gyromag. ratio over 2 pi                       29.164 6943           0.000 0069            MHz T^-1
neutron mag. mom.                                      -0.966 236 47 e-26    0.000 000 23 e-26     J T^-1
neutron mag. mom. to Bohr magneton ratio               -1.041 875 63 e-3     0.000 000 25 e-3
neutron mag. mom. to nuclear magneton ratio            -1.913 042 72         0.000 000 45
neutron mass                                           1.674 927 351 e-27    0.000 000 074 e-27    kg
neutron mass energy equivalent                         1.505 349 631 e-10    0.000 000 066 e-10    J
neutron mass energy equivalent in MeV                  939.565 379           0.000 021             MeV
neutron mass in u                                      1.008 664 916 00      0.000 000 000 43      u
neutron molar mass                                     1.008 664 916 00 e-3  0.000 000 000 43 e-3  kg mol^-1
neutron-muon mass ratio                                8.892 484 00          0.000 000 22
neutron-proton mag. mom. ratio                         -0.684 979 34         0.000 000 16
neutron-proton mass difference                         2.305 573 92 e-30     0.000 000 76 e-30
neutron-proton mass difference energy equivalent       2.072 146 50 e-13     0.000 000 68 e-13
neutron-proton mass difference energy equivalent in MeV 1.293 332 17          0.000 000 42
neutron-proton mass difference in u                    0.001 388 449 19      0.000 000 000 45
neutron-proton mass ratio                              1.001 378 419 17      0.000 000 000 45
neutron-tau mass ratio                                 0.528 790             0.000 048
neutron to shielded proton mag. mom. ratio             -0.684 996 94         0.000 000 16
Newtonian constant of gravitation                      6.673 84 e-11         0.000 80 e-11         m^3 kg^-1 s^-2
Newtonian constant of gravitation over h-bar c         6.708 37 e-39         0.000 80 e-39         (GeV/c^2)^-2
nuclear magneton                                       5.050 783 53 e-27     0.000 000 11 e-27     J T^-1
nuclear magneton in eV/T                               3.152 451 2605 e-8    0.000 000 0022 e-8    eV T^-1
nuclear magneton in inverse meters per tesla           2.542 623 527 e-2     0.000 000 056 e-2     m^-1 T^-1
nuclear magneton in K/T                                3.658 2682 e-4        0.000 0033 e-4        K T^-1
nuclear magneton in MHz/T                              7.622 593 57          0.000 000 17          MHz T^-1
Planck constant                                        6.626 069 57 e-34     0.000 000 29 e-34     J s
Planck constant in eV s                                4.135 667 516 e-15    0.000 000 091 e-15    eV s
Planck constant over 2 pi                              1.054 571 726 e-34    0.000 000 047 e-34    J s
Planck constant over 2 pi in eV s                      6.582 119 28 e-16     0.000 000 15 e-16     eV s
Planck constant over 2 pi times c in MeV fm            197.326 9718          0.000 0044            MeV fm
Planck length                                          1.616 199 e-35        0.000 097 e-35        m
Planck mass                                            2.176 51 e-8          0.000 13 e-8          kg
Planck mass energy equivalent in GeV                   1.220 932 e19         0.000 073 e19         GeV
Planck temperature                                     1.416 833 e32         0.000 085 e32         K
Planck time                                            5.391 06 e-44         0.000 32 e-44         s
proton charge to mass quotient                         9.578 833 58 e7       0.000 000 21 e7       C kg^-1
proton Compton wavelength                              1.321 409 856 23 e-15 0.000 000 000 94 e-15 m
proton Compton wavelength over 2 pi                    0.210 308 910 47 e-15 0.000 000 000 15 e-15 m
proton-electron mass ratio                             1836.152 672 45       0.000 000 75
proton g factor                                        5.585 694 713         0.000 000 046
proton gyromag. ratio                                  2.675 222 005 e8      0.000 000 063 e8      s^-1 T^-1
proton gyromag. ratio over 2 pi                        42.577 4806           0.000 0010            MHz T^-1
proton mag. mom.                                       1.410 606 743 e-26    0.000 000 033 e-26    J T^-1
proton mag. mom. to Bohr magneton ratio                1.521 032 210 e-3     0.000 000 012 e-3
proton mag. mom. to nuclear magneton ratio             2.792 847 356         0.000 000 023
proton mag. shielding correction                       25.694 e-6            0.014 e-6
proton mass                                            1.672 621 777 e-27    0.000 000 074 e-27    kg
proton mass energy equivalent                          1.503 277 484 e-10    0.000 000 066 e-10    J
proton mass energy equivalent in MeV                   938.272 046           0.000 021             MeV
proton mass in u                                       1.007 276 466 812     0.000 000 000 090     u
proton molar mass                                      1.007 276 466 812 e-3 0.000 000 000 090 e-3 kg mol^-1
proton-muon mass ratio                                 8.880 243 31          0.000 000 22
proton-neutron mag. mom. ratio                         -1.459 898 06         0.000 000 34
proton-neutron mass ratio                              0.998 623 478 26      0.000 000 000 45
proton rms charge radius                               0.8775 e-15           0.0051 e-15           m
proton-tau mass ratio                                  0.528 063             0.000 048
quantum of circulation                                 3.636 947 5520 e-4    0.000 000 0024 e-4    m^2 s^-1
quantum of circulation times 2                         7.273 895 1040 e-4    0.000 000 0047 e-4    m^2 s^-1
Rydberg constant                                       10 973 731.568 539    0.000 055             m^-1
Rydberg constant times c in Hz                         3.289 841 960 364 e15 0.000 000 000 017 e15 Hz
Rydberg constant times hc in eV                        13.605 692 53         0.000 000 30          eV
Rydberg constant times hc in J                         2.179 872 171 e-18    0.000 000 096 e-18    J
Sackur-Tetrode constant (1 K, 100 kPa)                 -1.151 7078           0.000 0023
Sackur-Tetrode constant (1 K, 101.325 kPa)             -1.164 8708           0.000 0023
second radiation constant                              1.438 7770 e-2        0.000 0013 e-2        m K
shielded helion gyromag. ratio                         2.037 894 659 e8      0.000 000 051 e8      s^-1 T^-1
shielded helion gyromag. ratio over 2 pi               32.434 100 84         0.000 000 81          MHz T^-1
shielded helion mag. mom.                              -1.074 553 044 e-26   0.000 000 027 e-26    J T^-1
shielded helion mag. mom. to Bohr magneton ratio       -1.158 671 471 e-3    0.000 000 014 e-3
shielded helion mag. mom. to nuclear magneton ratio    -2.127 497 718        0.000 000 025
shielded helion to proton mag. mom. ratio              -0.761 766 558        0.000 000 011
shielded helion to shielded proton mag. mom. ratio     -0.761 786 1313       0.000 000 0033
shielded proton gyromag. ratio                         2.675 153 268 e8      0.000 000 066 e8      s^-1 T^-1
shielded proton gyromag. ratio over 2 pi               42.576 3866           0.000 0010            MHz T^-1
shielded proton mag. mom.                              1.410 570 499 e-26    0.000 000 035 e-26    J T^-1
shielded proton mag. mom. to Bohr magneton ratio       1.520 993 128 e-3     0.000 000 017 e-3
shielded proton mag. mom. to nuclear magneton ratio    2.792 775 598         0.000 000 030
speed of light in vacuum                               299 792 458           (exact)               m s^-1
standard acceleration of gravity                       9.806 65              (exact)               m s^-2
standard atmosphere                                    101 325               (exact)               Pa
standard-state pressure                                100 000               (exact)               Pa
Stefan-Boltzmann constant                              5.670 373 e-8         0.000 021 e-8         W m^-2 K^-4
tau Compton wavelength                                 0.697 787 e-15        0.000 063 e-15        m
tau Compton wavelength over 2 pi                       0.111 056 e-15        0.000 010 e-15        m
tau-electron mass ratio                                3477.15               0.31
tau mass                                               3.167 47 e-27         0.000 29 e-27         kg
tau mass energy equivalent                             2.846 78 e-10         0.000 26 e-10         J
tau mass energy equivalent in MeV                      1776.82               0.16                  MeV
tau mass in u                                          1.907 49              0.000 17              u
tau molar mass                                         1.907 49 e-3          0.000 17 e-3          kg mol^-1
tau-muon mass ratio                                    16.8167               0.0015
tau-neutron mass ratio                                 1.891 11              0.000 17
tau-proton mass ratio                                  1.893 72              0.000 17
Thomson cross section                                  0.665 245 8734 e-28   0.000 000 0013 e-28   m^2
triton-electron mass ratio                             5496.921 5267         0.000 0050
triton g factor                                        5.957 924 896         0.000 000 076
triton mag. mom.                                       1.504 609 447 e-26    0.000 000 038 e-26    J T^-1
triton mag. mom. to Bohr magneton ratio                1.622 393 657 e-3     0.000 000 021 e-3
triton mag. mom. to nuclear magneton ratio             2.978 962 448         0.000 000 038
triton mass                                            5.007 356 30 e-27     0.000 000 22 e-27     kg
triton mass energy equivalent                          4.500 387 41 e-10     0.000 000 20 e-10     J
triton mass energy equivalent in MeV                   2808.921 005          0.000 062             MeV
triton mass in u                                       3.015 500 7134        0.000 000 0025        u
triton molar mass                                      3.015 500 7134 e-3    0.000 000 0025 e-3    kg mol^-1
triton-proton mass ratio                               2.993 717 0308        0.000 000 0025
unified atomic mass unit                               1.660 538 921 e-27    0.000 000 073 e-27    kg
von Klitzing constant                                  25 812.807 4434       0.000 0084            ohm
weak mixing angle                                      0.2223                0.0021
Wien frequency displacement law constant               5.878 9254 e10        0.000 0053 e10        Hz K^-1
Wien wavelength displacement law constant              2.897 7721 e-3        0.000 0026 e-3        m K"""

# -----------------------------------------------------------------------------

physical_constants = {}


def parse_constants(d):
    constants = {}
    for line in d.split('\n'):
        name = line[:55].rstrip()
        val = line[55:77].replace(' ','').replace('...','')
        val = float(val)
        uncert = line[77:99].replace(' ','').replace('(exact)', '0')
        uncert = float(uncert)
        units = line[99:].rstrip()
        constants[name] = (val, units, uncert)
    return constants

_physical_constants_2002 = parse_constants(txt2002)
_physical_constants_2006 = parse_constants(txt2006)
_physical_constants_2010 = parse_constants(txt2010)

physical_constants.update(_physical_constants_2002)
physical_constants.update(_physical_constants_2006)
physical_constants.update(_physical_constants_2010)
_current_constants = _physical_constants_2010
_current_codata = "CODATA 2010"

# check obsolete values
_obsolete_constants = {}
for k in physical_constants:
    if k not in _current_constants:
        _obsolete_constants[k] = True

# generate some additional aliases
_aliases = {}
for k in _physical_constants_2002:
    if 'magn.' in k:
        _aliases[k] = k.replace('magn.', 'mag.')
for k in _physical_constants_2006:
    if 'momentum' in k:
        _aliases[k] = k.replace('momentum', 'mom.um')


class ConstantWarning(DeprecationWarning):
    """Accessing a constant no longer in current CODATA data set"""
    pass


def _check_obsolete(key):
    if key in _obsolete_constants and key not in _aliases:
        warnings.warn("Constant '%s' is not in current %s data set" % (
            key, _current_codata), ConstantWarning)


def value(key):
    """
    Value in physical_constants indexed by key

    Parameters
    ----------
    key : Python string or unicode
        Key in dictionary `physical_constants`

    Returns
    -------
    value : float
        Value in `physical_constants` corresponding to `key`

    See Also
    --------
    codata : Contains the description of `physical_constants`, which, as a
        dictionary literal object, does not itself possess a docstring.

        Examples
    --------
    >>> from scipy.constants import codata
    >>> codata.value('elementary charge')
        1.602176487e-019

    """
    _check_obsolete(key)
    return physical_constants[key][0]


def unit(key):
    """
    Unit in physical_constants indexed by key

    Parameters
    ----------
    key : Python string or unicode
        Key in dictionary `physical_constants`

    Returns
    -------
    unit : Python string
        Unit in `physical_constants` corresponding to `key`

    See Also
    --------
    codata : Contains the description of `physical_constants`, which, as a
        dictionary literal object, does not itself possess a docstring.

    Examples
    --------
    >>> from scipy.constants import codata
    >>> codata.unit(u'proton mass')
    'kg'

    """
    _check_obsolete(key)
    return physical_constants[key][1]


def precision(key):
    """
    Relative precision in physical_constants indexed by key

    Parameters
    ----------
    key : Python string or unicode
        Key in dictionary `physical_constants`

    Returns
    -------
    prec : float
        Relative precision in `physical_constants` corresponding to `key`

    See Also
    --------
    codata : Contains the description of `physical_constants`, which, as a
        dictionary literal object, does not itself possess a docstring.

    Examples
    --------
    >>> from scipy.constants import codata
    >>> codata.precision(u'proton mass')
    4.96226989798e-08

    """
    _check_obsolete(key)
    return physical_constants[key][2] / physical_constants[key][0]


def find(sub=None, disp=False):
    """
    Return list of codata.physical_constant keys containing a given string.

    Parameters
    ----------
    sub : str, unicode
        Sub-string to search keys for.  By default, return all keys.
    disp : bool
        If True, print the keys that are found, and return None.
        Otherwise, return the list of keys without printing anything.

    Returns
    -------
    keys : list or None
        If `disp` is False, the list of keys is returned.
        Otherwise, None is returned.

    See Also
    --------
    codata : Contains the description of `physical_constants`, which, as a
        dictionary literal object, does not itself possess a docstring.

    """
    if sub is None:
        result = list(_current_constants.keys())
    else:
        result = [key for key in _current_constants
                 if sub.lower() in key.lower()]

    result.sort()
    if disp:
        for key in result:
            print(key)
        return
    else:
        return result

# Table is lacking some digits for exact values: calculate from definition
c = value('speed of light in vacuum')
mu0 = 4e-7*pi
epsilon0 = 1/(mu0*c*c)

exact_values = {
'mag. constant': (mu0, 'N A^-2', 0.0),
'electric constant': (epsilon0, 'F m^-1', 0.0),
'characteristic impedance of vacuum': (sqrt(mu0/epsilon0), 'ohm', 0.0),
'atomic unit of permittivity': (4*epsilon0*pi, 'F m^-1', 0.0),  # is that the definition?
'joule-kilogram relationship': (1/(c*c), 'kg', 0.0),
'kilogram-joule relationship': (c*c, 'J', 0.0),
'hertz-inverse meter relationship': (1/c, 'm^-1', 0.0)
}

# sanity check
for key in exact_values:
    val = _current_constants[key][0]
    if abs(exact_values[key][0] - val) / val > 1e-9:
        raise ValueError("Constants.codata: exact values too far off.")

physical_constants.update(exact_values)

# finally, insert aliases for values
for k, v in list(_aliases.items()):
    if v in _current_constants:
        physical_constants[k] = physical_constants[v]
    else:
        del _aliases[k]
