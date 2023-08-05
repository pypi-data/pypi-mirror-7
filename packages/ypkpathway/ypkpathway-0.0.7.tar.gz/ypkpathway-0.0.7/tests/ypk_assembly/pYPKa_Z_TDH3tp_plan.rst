==============
pYPKa_Z_TDH3tp
==============

Plan for the construction of E. coli vector `pYPKa_Z_TDH3tp <./pYPKa_Z_TDH3tp.txt>`_

Step 1 PCR of the insert
........................

PCR with primers pfw698 & prv698 and template `TDH3_template <./TDH3_template.txt>`_ results in 
a 711bp `PCR product <./TDH3.txt>`_


Primers annealing on template:
::

       5ATAAAAAACACGCTTTTTC...AACACACATAAACAAACAAA3
                              |||||||||||||||||||| tm 44.1 (dbd) 54.7
                             3TTGTGTGTATTTGTTTGTTTaattaat5
 5ttaaatATAAAAAACACGCTTTTTC3
        ||||||||||||||||||| tm 42.7 (dbd) 55.3
       3TATTTTTTGTGCGAAAAAG...TTGTGTGTATTTGTTTGTTT5

Suggested PCR programs for Taq polymerase and for Polymerases with DNA binding domain:
::

 
 Taq (rate 30 nt/s)
 Three-step|         30 cycles     |      |SantaLucia 1998
 94.0°C    |94.0°C                 |      |SaltC 50mM
 __________|_____          72.0°C  |72.0°C|
 04min00s  |30s  \         ________|______|
           |      \ 50.0°C/ 0min21s|10min |
           |       \_____/         |      |
           |         30s           |      |4-8°C
 
 Pfu-Sso7d (rate 15s/kb)
 Three-step|          30 cycles   |      |Breslauer1986,SantaLucia1998
 98.0°C    |98.0°C                |      |SaltC 50mM
 __________|_____          72.0°C |72.0°C|Primer1C   1µM
 00min30s  |10s  \ 55.0°C ________|______|Primer2C   1µM
           |      \______/ 0min10s|10min |
           |        10s           |      |4-8°C

Step 2 Vector digestion and cloning
...................................

Clone the `PCR product <./TDH3.txt>`_ in `pYPKa <./pYPKa.txt>`_ digested 
with `ZraI <http://rebase.neb.com/rebase/enz/ZraI.html>`_ resulting in `pYPKa_Z_TDH3tp <./pYPKa_Z_TDH3tp.txt>`_


Step 3 Diagnostic PCR confirmation
..................................

Confirm the structure of the `pYPKa_Z_TDH3tp <./pYPKa_Z_TDH3tp.txt>`_ using primers 577, 342 and pfw698 
in a multiplex PCR reaction.

Expected PCR products sizes from 577, 342 and pfw698 (bp):

pYPKa with insert in correct orientation: 1645, 1477 |br|
pYPKa with insert in reverse orientation: 1645, 879 |br|
Empty pYPKa clone                       : 934 


.. |br| raw:: html

   <br />
