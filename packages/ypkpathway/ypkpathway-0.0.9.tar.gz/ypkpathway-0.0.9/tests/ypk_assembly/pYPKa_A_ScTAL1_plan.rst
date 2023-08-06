==============
pYPKa_A_ScTAL1
==============

Plan for the construction of E. coli vector `pYPKa_A_ScTAL1 <./pYPKa_A_ScTAL1.txt>`_

Step 1 PCR of the insert
........................

PCR with primers pfw1008 & prv1008 and template `ScTAL1_template <./ScTAL1_template.txt>`_ results in 
a 1010bp `PCR product <./ScTAL1.txt>`_


Primers annealing on template:
::

   5ATGTCTGAACCAGCTC...AAGAAAGTTACCGCTTAA3
                       |||||||||||||||||| tm 42.9 (dbd) 53.4
                      3TTCTTTCAATGGCGAATT5
 5aaATGTCTGAACCAGCTC3
    |||||||||||||||| tm 44.1 (dbd) 52.9
   3TACAGACTTGGTCGAG...TTCTTTCAATGGCGAATT5

Suggested PCR programs for Taq polymerase and for Polymerases with DNA binding domain:
::

 
 Taq (rate 30 nt/s)
 Three-step|         30 cycles     |      |SantaLucia 1998
 94.0°C    |94.0°C                 |      |SaltC 50mM
 __________|_____          72.0°C  |72.0°C|
 04min00s  |30s  \         ________|______|
           |      \ 52.0°C/ 0min30s|10min |
           |       \_____/         |      |
           |         30s           |      |4-8°C
 
 Pfu-Sso7d (rate 15s/kb)
 Three-step|          30 cycles   |      |Breslauer1986,SantaLucia1998
 98.0°C    |98.0°C                |      |SaltC 50mM
 __________|_____          72.0°C |72.0°C|Primer1C   1µM
 00min30s  |10s  \ 53.0°C ________|______|Primer2C   1µM
           |      \______/ 0min15s|10min |
           |        10s           |      |4-8°C

Step 2 Vector digestion and cloning
...................................

Clone the `PCR product <./ScTAL1.txt>`_ in `pYPKa <./pYPKa.txt>`_ digested 
with `AjiI <http://rebase.neb.com/rebase/enz/AjiI.html>`_ resulting in `pYPKa_A_ScTAL1 <./pYPKa_A_ScTAL1.txt>`_


Step 3 Diagnostic PCR confirmation
..................................

Confirm the structure of the `pYPKa_A_ScTAL1 <./pYPKa_A_ScTAL1.txt>`_ using primers 468, 342 and pfw1008 
in a multiplex PCR reaction.

Expected PCR products sizes from 468, 342 and pfw1008 (bp):

pYPKa with insert in correct orientation: 1776, 1726 |br|
pYPKa with insert in reverse orientation: 1776, 1060 |br|
Empty pYPKa clone                       : 766 


.. |br| raw:: html

   <br />
