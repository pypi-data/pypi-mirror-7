=========================
pYPK0_TDH3tp_SsXYL2_PGItp
=========================

Step 1 Prepare vector
.....................

Linearize `pYPKpw <./pYPKpw.txt>`_ with `EcoRV <http://rebase.neb.com/rebase/enz/EcoRV.html>`_
resulting in the `linearized vector <./pYPKpw_lin.txt>`_.

Step 2 PCR of first tp
......................

Carry out a PCR with primers 577, 567 and template `pYPKa_Z_TDH3tp <./pYPKa_Z_TDH3tp.txt>`_ resulting in 
the PCR product `929bp_PCR_prod <./pYPKa_Z_TDH3tp_pcr_prd.txt>`_      |br|   
::

 5GTTCTGATCCTCGAGCATCTTAAGAATTC...CTCACTAGTGACCTGCAGCCGAC3
                                  ||||||||||||||||||||||| tm 59.0 (dbd) 70.7
                                 3gagtgatcactggacgtcggcTG5
 5gttctgatcctcgagcatcttaagaattc3
  ||||||||||||||||||||||||||||| tm 56.1 (dbd) 69.4
 3CAAGACTAGGAGCTCGTAGAATTCTTAAG...GAGTGATCACTGGACGTCGGCTG5

 
 Taq (rate 30 nt/s)
 Three-step|         30 cycles     |      |SantaLucia 1998
 94.0°C    |94.0°C                 |      |SaltC 50mM
 __________|_____          72.0°C  |72.0°C|
 04min00s  |30s  \         ________|______|
           |      \ 56.0°C/ 0min27s|10min |
           |       \_____/         |      |
           |         30s           |      |4-8°C
 
 Pfu-Sso7d (rate 15s/kb)
 Two-step|    30 cycles |      |Breslauer1986,SantaLucia1998
 98.0°C  |98.0C         |      |SaltC 50mM
 _____ __|_____         |      |Primer1C 1000µM
 00min30s|10s  \  72.0°C|72.0°C|Primer2C <bound method Amplicon.rc of Amplicon(929)>µM
         |      \_______|______|
         |       0min13s|10min |4-8°C

Step 3 Gene PCR
...............

Carry out a PCR with primers 468, 467 and template `pYPKa_A_SsXYL2 <./pYPKa_A_SsXYL2.txt>`_ resulting in 
the PCR product `1181bp_PCR_prod <./pYPKa_A_SsXYL2_pcr_prd.txt>`_     |br|   
::

 5GTCGAGGAACGCCAGGTTGCCCACT...TCTGTGCAGACAAACGCATCAGGAT3
                              ||||||||||||||||||||||||| tm 59.0 (dbd) 73.8
                             3agacacgtctgtttgcgtagtcctaAATTTA5
 5gtcgaggaacgccaggttgcccact3
  ||||||||||||||||||||||||| tm 64.8 (dbd) 79.7
 3CAGCTCCTTGCGGTCCAACGGGTGA...AGACACGTCTGTTTGCGTAGTCCTA5

 
 Taq (rate 30 nt/s)
 Three-step|         30 cycles     |      |SantaLucia 1998
 94.0°C    |94.0°C                 |      |SaltC 50mM
 __________|_____          72.0°C  |72.0°C|
 04min00s  |30s  \         ________|______|
           |      \ 59.0°C/ 0min35s|10min |
           |       \_____/         |      |
           |         30s           |      |4-8°C
 
 Pfu-Sso7d (rate 15s/kb)
 Two-step|    30 cycles |      |Breslauer1986,SantaLucia1998
 98.0°C  |98.0C         |      |SaltC 50mM
 _____ __|_____         |      |Primer1C 1000µM
 00min30s|10s  \  72.0°C|72.0°C|Primer2C <bound method Amplicon.rc of Amplicon(1181)>µM
         |      \_______|______|
         |       0min17s|10min |4-8°C

Step 4 PCR of last tp
.....................

Carry out a PCR with primers 568, 578 and template `pYPKa_E_PGItp <./pYPKa_E_PGItp.txt>`_ resulting in 
the PCR product `1339bp_PCR_prod <./pYPKa_E_PGItp_pcr_prd.txt>`_      |br|   
::

 5GTGCCATCTGTGCAGACAAACG...ACTTATGAATGTGGCAATGAGACAAGAAC3
                           ||||||||||||||||||||||||||||| tm 56.5 (dbd) 69.5
                          3tgaatacttacaccgttactctgttcttg5
 5GTGCcatctgtgcagacaaacg3
  |||||||||||||||||||||| tm 57.1 (dbd) 71.5
 3CACGGTAGACACGTCTGTTTGC...TGAATACTTACACCGTTACTCTGTTCTTG5

 
 Taq (rate 30 nt/s)
 Three-step|         30 cycles     |      |SantaLucia 1998
 94.0°C    |94.0°C                 |      |SaltC 50mM
 __________|_____          72.0°C  |72.0°C|
 04min00s  |30s  \         ________|______|
           |      \ 56.0°C/ 0min40s|10min |
           |       \_____/         |      |
           |         30s           |      |4-8°C
 
 Pfu-Sso7d (rate 15s/kb)
 Two-step|    30 cycles |      |Breslauer1986,SantaLucia1998
 98.0°C  |98.0C         |      |SaltC 50mM
 _____ __|_____         |      |Primer1C 1000µM
 00min30s|10s  \  72.0°C|72.0°C|Primer2C <bound method Amplicon.rc of Amplicon(1339)>µM
         |      \_______|______|
         |       0min20s|10min |4-8°C


Step 5 Yeast transformation
...........................

Mix the four linear DNA fragments and transform a Saccharomyces cerevisiae ura3 mutant with the mixture.
The fragments will be assembled by in-vivo homologous recombination:

::

  -|pYPKpw|124
 |         \/
 |         /\
 |         124|929bp_PCR_prod|50
 |                            \/
 |                            /\
 |                            50|1181bp_PCR_prod|37
 |                                               \/
 |                                               /\
 |                                               37|1339bp_PCR_prod|242
 |                                                                  \/
 |                                                                  /\
 |                                                                  242-
 |                                                                     |
  ---------------------------------------------------------------------



Step 6 Diagnostic PCR confirmation
..................................

First tp and gene
+++++++++++++++++

PCR using primers 577 & 467 |br|     

PCR products (bp)

    Correct          : 2060 |br|
    Missing first tp : 1349 |br|
    Missing gene     : 966 |br|
    Missing both     : 255 |br|

Gene and last tp
++++++++++++++++

PCR using primers 468 & 578 |br| 

PCR products (bp)

    Correct         : 2483 |br|
    Missing gene    : 1389 |br|
    Missing last tp : 1470 |br|
    Missing both    : 376 |br|

.. |br| raw:: html

   <br />

