#!/usr/bin/env python
# -*- coding: utf-8 -*- 

execfile("header.py")

def design():
    #---------------------------------------------------------------------------
    # This script should define a Dseqrecord named seq
       
    from pydna import parse
    from pydna import pcr
    from pydna import Assembly
    from pydna import Dseqrecord
    
    
    (p577,
     p578,
     p775,
     p778) = parse('''>577          
                      gttctgatcctcgagcatcttaagaattc                                                                           
                      >578            
                      gttcttgtctcattgccacattcataagt
                      >775 
                      gcggccgctgacTTAAAT
                      >778 
                      ggtaaatccggatTAATTAA''', ds=False)
    
    from Bio.Restriction import EcoRV

    from pYPKpw import pYPKpw
    
    pYPKpw_lin = pYPK0.linearize(EcoRV)
    
    from pYPK0_TEF1tp_SsXYL1_TDH3tp import pYPK0_TEF1tp_SsXYL1_TDH3tp as cas1
    from pYPK0_TDH3tp_SsXYL2_PGItp import pYPK0_TDH3tp_SsXYL2_PGItp as cas2
    cas1  = pcr( p577, p778, cas1)
    cas2 = pcr( p775, p578, cas2)    
    
    asm = Assembly((pYPKpw_lin, cas1,cas2))

    print asm.analyze_overlaps(limit=61)

    print asm.create_graph()

    print asm.assemble_circular_from_graph()

    seq = asm.circular_products[0]
    
    print seq.small_fig()
            
    seq = seq.synced("tcgcgcgtttcggtgatgacggtgaaaacctctg")     
    
    # This script should define a Dseqrecord named seq
    #---------------------------------------------------------------------------
    assert isinstance(seq, Dseqrecord)
    return seq
    
execfile("footer.py")
    


