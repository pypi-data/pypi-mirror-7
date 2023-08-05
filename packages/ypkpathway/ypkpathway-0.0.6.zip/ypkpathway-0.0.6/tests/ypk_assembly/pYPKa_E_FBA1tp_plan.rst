==============
pYPKa_E_FBA1tp
==============

Plan for the construction of E. coli vector `pYPKa_E_FBA1tp <./pYPKa_E_FBA1tp.txt>`_

Step 1 PCR of the insert
........................

PCR with primers pfw630 & prv630 and template `FBA1_template <./FBA1_template.txt>`_ results in 
a 643bp `PCR product <./FBA1.txt>`_


Primers annealing on template:
::

       5ATAACAATACTGACAGTACTAAATAAT...ATAACCAAGTAATACATATTCAAA3
                                      |||||||||||||||||||||||| tm 44.2 (dbd) 54.6
                                     3TATTGGTTCATTATGTATAAGTTTaattaat5
 5ttaaatATAACAATACTGACAGTACTAAATAAT3
        ||||||||||||||||||||||||||| tm 47.0 (dbd) 54.0
       3TATTGTTATGACTGTCATGATTTATTA...TATTGGTTCATTATGTATAAGTTT5

Suggested PCR programs for Taq polymerase and for Polymerases with DNA binding domain:
::

 
 Taq (rate 30 nt/s)
 Three-step|         30 cycles     |      |SantaLucia 1998
 94.0°C    |94.0°C                 |      |SaltC 50mM
 __________|_____          72.0°C  |72.0°C|
 04min00s  |30s  \         ________|______|
           |      \ 50.0°C/ 0min19s|10min |
           |       \_____/         |      |
           |         30s           |      |4-8°C
 
 Pfu-Sso7d (rate 15s/kb)
 Three-step|          30 cycles   |      |Breslauer1986,SantaLucia1998
 98.0°C    |98.0°C                |      |SaltC 50mM
 __________|_____          72.0°C |72.0°C|Primer1C   1µM
 00min30s  |10s  \ 57.0°C ________|______|Primer2C   1µM
           |      \______/ 0min 9s|10min |
           |        10s           |      |4-8°C

Step 2 Vector digestion and cloning
...................................

Clone the `PCR product <./FBA1.txt>`_ in `pYPKa <./pYPKa.txt>`_ digested 
with `EcoRV <http://rebase.neb.com/rebase/enz/EcoRV.html>`_ resulting in `pYPKa_E_FBA1tp <./pYPKa_E_FBA1tp.txt>`_


Step 3 Diagnostic PCR confirmation
..................................

Confirm the structure of the `pYPKa_E_FBA1tp <./pYPKa_E_FBA1tp.txt>`_ using primers 568, 342 and pfw630 
in a multiplex PCR reaction.

Expected PCR products sizes from 568, 342 and pfw630 (bp):

pYPKa with insert in correct orientation: 1359, 1328 |br|
pYPKa with insert in reverse orientation: 1359, 674 |br|
Empty pYPKa clone                       : 716 


.. |br| raw:: html

   <br />
