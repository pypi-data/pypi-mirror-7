=============
pYPKa_E_PGItp
=============

Plan for the construction of E. coli vector `pYPKa_E_PGItp <./pYPKa_E_PGItp.txt>`_

Step 1 PCR of the insert
........................

PCR with primers pfw1000 & prv1000 and template `PGI_template <./PGI_template.txt>`_ results in 
a 1013bp `PCR product <./PGI.txt>`_


Primers annealing on template:
::

       5AATTCAGTTTTCTGACTGA...CAAGATACCAGCCTAAAA3
                              |||||||||||||||||| tm 43.0 (dbd) 54.5
                             3GTTCTATGGTCGGATTTTaattaat5
 5ttaaatAATTCAGTTTTCTGACTGA3
        ||||||||||||||||||| tm 43.6 (dbd) 53.8
       3TTAAGTCAAAAGACTGACT...GTTCTATGGTCGGATTTT5

Suggested PCR programs for Taq polymerase and for Polymerases with DNA binding domain:
::

 
 Taq (rate 30 nt/s)
 Three-step|         30 cycles     |      |SantaLucia 1998
 94.0°C    |94.0°C                 |      |SaltC 50mM
 __________|_____          72.0°C  |72.0°C|
 04min00s  |30s  \         ________|______|
           |      \ 51.0°C/ 0min30s|10min |
           |       \_____/         |      |
           |         30s           |      |4-8°C
 
 Pfu-Sso7d (rate 15s/kb)
 Three-step|          30 cycles   |      |Breslauer1986,SantaLucia1998
 98.0°C    |98.0°C                |      |SaltC 50mM
 __________|_____          72.0°C |72.0°C|Primer1C   1µM
 00min30s  |10s  \ 54.0°C ________|______|Primer2C   1µM
           |      \______/ 0min15s|10min |
           |        10s           |      |4-8°C

Step 2 Vector digestion and cloning
...................................

Clone the `PCR product <./PGI.txt>`_ in `pYPKa <./pYPKa.txt>`_ digested 
with `EcoRV <http://rebase.neb.com/rebase/enz/EcoRV.html>`_ resulting in `pYPKa_E_PGItp <./pYPKa_E_PGItp.txt>`_


Step 3 Diagnostic PCR confirmation
..................................

Confirm the structure of the `pYPKa_E_PGItp <./pYPKa_E_PGItp.txt>`_ using primers 568, 342 and pfw1000 
in a multiplex PCR reaction.

Expected PCR products sizes from 568, 342 and pfw1000 (bp):

pYPKa with insert in correct orientation: 1729, 1698 |br|
pYPKa with insert in reverse orientation: 1729, 1044 |br|
Empty pYPKa clone                       : 716 


.. |br| raw:: html

   <br />
