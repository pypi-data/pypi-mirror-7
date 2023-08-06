# coding: utf-8
from Bio import SeqIO
from Bio.Alphabet.IUPAC import IUPACAmbiguousDNA

global new_primer
global primer
global old_primer
global new_primer_dict
global primer_dict
global old_primer_dict

from pydna import parse

new_primer = parse("/home/bjorn/Dropbox/wikidata/PrimersToBuy.wiki", ds=False)
primer     = parse("/home/bjorn/Dropbox/wikidata/Primers.wiki", ds=False)

primer     = primer[::-1]
old_primer = primer[:37+18]
primer     = primer[37+18:]

new_primer_dict         = dict((p.id, p) for p in new_primer)
primer_dict             = dict((p.id, p) for p in primer)
old_primer_dict         = dict((p.id, p) for p in old_primer)

assert str(primer_dict["509_mycGFPr"].seq) == "CTACTTGTACAGCTCGTCCA"
assert primer[0].id == "0_S1"
assert primer[580].id == "580_GXF1_YPK_fwd"

if __name__=="__main__":
    print "primers loaded into memory"
    print "{:3d} old primers    -> old_primer [list]".format(len(old_primer))
    print "{:3d} primers        -> primer [list]".format(len(primer))
    print "{:3d} primers to buy -> new_primer [list]".format(len(new_primer))
