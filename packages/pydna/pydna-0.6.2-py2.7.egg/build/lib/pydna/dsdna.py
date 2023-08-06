#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 by Björn Johansson.  All rights reserved.
# This code is part of the Python-dna distribution and governed by its
# license.  Please see the LICENSE.txt file that should have been included
# as part of this package.

'''Provides two classes, Dseq and Dseqrecord, for handling double stranded
DNA sequences. Dseq and Dseqrecord are subclasses of Biopythons
Seq and SeqRecord classes, respectively. These classes support the
notion of circular and linear DNA.

'''

import copy
import datetime
import itertools
import operator
import os
import re
import string
import StringIO
import sys
import textwrap
import warnings
import math
from pprint import pprint


from Bio                    import Alphabet
from Bio                    import SeqIO
from Bio.Alphabet.IUPAC     import IUPACAmbiguousDNA
from Bio.Seq                import Seq
from Bio.Seq                import _maketrans
from Bio.Data.IUPACData     import ambiguous_dna_complement as amb_compl
from Bio.SeqRecord          import SeqRecord
from Bio.SeqFeature         import SeqFeature
from Bio.SeqFeature         import FeatureLocation, CompoundLocation
from Bio.SeqUtils.CheckSum  import seguid
from Bio.GenBank            import RecordParser
from pydna.utils            import eq, cseguid
from pydna.findsubstrings_suffix_arrays_python import common_sub_strings

amb_compl.update({"U":"A"})
_complement_table = _maketrans(amb_compl)

def rc(sequence):
    '''returns the reverse complement of sequence (string)
    accepts mixed DNA/RNA
    '''
    return sequence.translate(_complement_table)[::-1]

class Dseq(Seq):
    '''Dseq is a class designed to hold information for a double stranded
    DNA fragment. Dseq also holds information describing the topology of
    the DNA fragment (linear or circular).

    Dseq is a subclass of the Biopython Seq object. It stores two
    strings representing the watson (sense) and crick(antisense) strands.
    two properties called linear and circular, and a numeric value ovhg
    (overhang) describing the stagger for the watson and crick strand
    in the 5' end of the fragment.

    The most common usage is probably to create a Dseq object as a
    part of a Dseqrecord object (see Dseqrecord).

    There are three ways of creating a Dseq object directly:

    Only one argument (string):

    >>> import pydna
    >>> pydna.Dseq("aaa")
    Dseq(-3)
    aaa
    ttt

    The given string will be interpreted as the watson strand of a
    blunt, linear double stranded sequence object. The crick strand
    is created automatically from the watson strand.

    Two arguments (string, string):

    >>> import pydna
    >>> pydna.Dseq("gggaaat","ttt")
    Dseq(-7)
    gggaaat
       ttt

    If both watson and crick are given, but not ovhg an attempt
    will be made to find the best annealing between the strands.
    There are limitations to this! For long fragments it is quite
    slow. The length of the annealing sequences have to be at least
    half the length of the shortest of the strands.

    Three arguments (string, string, ovhg=int):

    The ovhg parameter controls the stagger at the five prime end::

        ovhg=-2

        XXXXX
          XXXXX

        ovhg=-1

        XXXXX
         XXXXX


        ovhg=0

        XXXXX
        XXXXX

        ovhg=1

         XXXXX
        XXXXX

        ovhg=2

          XXXXX
        XXXXX

    Example of creating Dseq objects with different amounts of stagger:

    >>> pydna.Dseq(watson="agt",crick="actta",ovhg=-2)
    Dseq(-7)
    agt
      attca
    >>> pydna.Dseq(watson="agt",crick="actta",ovhg=-1)
    Dseq(-6)
    agt
     attca
    >>> pydna.Dseq(watson="agt",crick="actta",ovhg=0)
    Dseq(-5)
    agt
    attca
    >>> pydna.Dseq(watson="agt",crick="actta",ovhg=1)
    Dseq(-5)
     agt
    attca
    >>> pydna.Dseq(watson="agt",crick="actta",ovhg=2)
    Dseq(-5)
      agt
    attca

    the ovhg parameter has to be given with both watson and crick,
    otherwise an exception is raised.

    >>> pydna.Dseq(watson="agt",ovhg=2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/usr/local/lib/python2.7/dist-packages/pydna_/dsdna.py", line 169, in __init__
        else:
    Exception: ovhg defined without crick strand!


    The default alphabet is set to Biopython IUPACAmbiguousDNA

    The shape of the fragment is set by either:

    linear   = False, True

    or

    circular = True, False

    Note that both ends of the DNA fragment has to be blunt to set
    circular = True (or linear = False).


    >>> pydna.Dseq("aaa","ttt")
    Dseq(-3)
    aaa
    ttt
    >>> pydna.Dseq("aaa","ttt",ovhg=0)
    Dseq(-3)
    aaa
    ttt
    >>> pydna.Dseq("aaa", "ttt", linear = False ,ovhg=0)
    Dseq(o3)
    aaa
    ttt
    >>> pydna.Dseq("aaa", "ttt", circular = True , ovhg=0)
    Dseq(o3)
    aaa
    ttt

    Coercing to string

    >>> a=pydna.Dseq("tttcccc","aaacccc")
    >>> a
    Dseq(-11)
        tttcccc
    ccccaaa

    >>> str(a)
    'ggggtttcccc'

    The double stranded part is accessible through the dsdata property:

    >>> a.dsdata
    'ttt'

    Dseqrecord and Dseq share the same concept of length
    ::

        <-- length -->
        GATCCTTT
             AAAGCCTAG
    
    
    
    The slicing of a linear Dseq object works mostly as it does for a string.
    
    
    >>> s="ggatcc"
    >>> s[2:3]
    'a'
    >>> s[2:4]
    'at'
    >>> s[2:4:-1]
    ''
    >>> s[::2]
    'gac'
    >>> import pydna
    >>> d=pydna.Dseq(s, linear=True)
    >>> d[2:3]
    Dseq(-1)
    a
    t
    >>> d[2:4]
    Dseq(-2)
    at
    ta
    >>> d[2:4:-1]
    Dseq(-0)
    <BLANKLINE>
    <BLANKLINE>
    >>> d[::2]
    Dseq(-3)
    gac
    ctg
    
    
    The slicing of a circular Dseq object has a slightly different meaning.
    

    >>> s="ggAtCc"
    >>> d=pydna.Dseq(s, circular=True)
    >>> d
    Dseq(o6)
    ggAtCc
    ccTaGg
    >>> d[4:3]
    Dseq(-5)
    CcggA
    GgccT

    
    The slice [X:X] produces an empty slice for a string, while this will return
    the linearized sequence starting at X:
    
    >>> s="ggatcc"
    >>> d=pydna.Dseq(s, circular=True)
    >>> d
    Dseq(o6)
    ggatcc
    cctagg
    >>> d[3:3]
    Dseq(-6)
    tccgga
    aggcct
    >>>
    
    
    

    '''

    def __init__(self,
                  watson,
                  crick         = None,
                  ovhg          = None,
                  linear        = None,
                  circular      = None,
                  alphabet      = IUPACAmbiguousDNA()):


        if ovhg is None:
            if crick is None:
                self.crick = rc(watson)
                self._ovhg = 0
            else:
                olaps = common_sub_strings(str(watson).lower(),
                                           str(rc(crick).lower()),
                                           int(math.log(len(watson))/math.log(4)))                    
                try:
                    F,T,L = olaps[0]
                except IndexError:
                    raise Exception("Could not anneal the two strands! "
                                    "ovhg should be provided")
                ovhgs = [ol[1]-ol[0] for ol in olaps if ol[2]==L]
                if len(ovhgs)>1:
                    for o in ovhgs:
                        print o
                    raise Exception("More than one way of annealing the strands "
                                    "ovhg should be provided")
                    
                self._ovhg = T-F
                self.crick = crick
        elif crick is None:
            raise Exception("ovhg defined without crick strand!")
        else:
            self._ovhg = ovhg
            self.crick = crick

        self.watson = watson

        sns = ((self._ovhg*" ")  + str(self.watson))
        asn = ((-self._ovhg*" ") + str(rc(self.crick)))

        self.todata = "".join([a.strip() or b.strip() for a,b in itertools.izip_longest(sns,asn, fillvalue=" ")])
        self.dsdata = "".join([a for a, b in itertools.izip_longest(sns,asn, fillvalue=" ") if a.lower()==b.lower()])

        if circular == None and linear in (True, False,):
            self._linear   = linear
            self._circular = not linear
        elif linear == None and circular in (True, False,):
            self._circular = circular
            self._linear   = not circular
        elif circular == linear == None:
            self._circular = False
            self._linear   = True
        elif linear in (True, False,) and circular in (True, False,) and circular != linear:
            self._circular = circular
            self._linear   = not circular
        else:
            raise Exception("circular and linear argument set to {} and {}, respectively\n".format(circular,linear)+
                            "circular and linear are each others opposites.")

        assert self._circular != self._linear

        if (self.circular and
            self.five_prime_end()[0]  != "blunt" and
            self.three_prime_end()[0] != "blunt"):
            raise Exception("DNA is circular, but has staggered ends!\n")

        Seq.__init__(self, self.todata, alphabet)

    def find(self, sub, start=0, end=sys.maxint):
        """Find method, like that of a python string.

        This behaves like the python string method of the same name.

        Returns an integer, the index of the first occurrence of substring
        argument sub in the (sub)sequence given by [start:end].

        Arguments:
         - sub - a string or another Seq object to look for
         - start - optional integer, slice start
         - end - optional integer, slice end

        Returns -1 if the subsequence is NOT found.

        e.g. Locating the first typical start codon, AUG, in an RNA sequence:

        >>> from Bio.Seq import Seq
        >>> my_rna = Seq("GUCAUGGCCAUUGUAAUGGGCCGCUGAAAGGGUGCCCGAUAGUUG")
        >>> my_rna.find("AUG")
        3
        """

        if self.linear:
            return Seq.find(self, sub, start, end)
            
        sub_str = self._get_seq_str_and_check_alphabet(sub)

        return (str(self)+str(self)).find(sub_str, start, end)



    def __getitem__(self, sl):
        '''Returns a subsequence.
        '''
                
        if self.linear:
            sns = (self._ovhg*" " + self.watson)[sl]
            asn = (-self._ovhg*" " + self.crick[::-1])[sl]
            ovhg = max((len(sns) - len(sns.lstrip()),
                        -len(asn) + len(asn.lstrip())),
                        key=abs)            
            return Dseq(sns.strip(), asn[::-1].strip(), ovhg=ovhg, linear=True)
        else:
            sl = slice(sl.start or 0,
                       sl.stop  or len(self),
                       sl.step)            
            
            if sl.start<sl.stop:
                return Dseq(self.watson[sl],self.crick[::-1][sl][::-1], ovhg=0, linear=True)
            else:
                #print sl.start,sl.stop, "<---"
                try:
                    stp = abs(sl.step)
                except TypeError:
                    stp = 1
                start=sl.start
                stop=sl.stop
                if not start:
                    start=0
                if not stop:
                    stop=len(self)
                        
                w = self.watson[(start or len(self))::stp] + self.watson[:(stop or 0):stp]
                c = self.crick[len(self)-stop::stp] + self.crick[:len(self)-start:stp]
                
                return Dseq(w, c, ovhg=0, linear=True)

    def __eq__( self, other ):
        '''Compare to another Dseq object OR an object that implements
        watson, crick and ovhg properties. This comparison is case
        insensitive.

        '''
        try:
            same = (other.watson.lower() == self.watson.lower() and
                    other.crick.lower()  == self.crick.lower()  and
                    other.ovhg == self._ovhg)
        except AttributeError:
            same = False
        return same


    def fig(self):
        '''Returns a representation of the sequence, truncated if
       longer than 30 bp:

       Examples
       --------

       >>> import pydna
       >>> a=pydna.Dseq("atcgcttactagcgtactgatcatctgactgactagcgtga")
       >>> a
       Dseq(-41)
       atcg..gtga
       tagc..cact
       >>>

       '''
        return self.__repr__()

    def __repr__(self):
        '''Returns a representation of the sequence, truncated if
        longer than 30 bp'''        

        if len(self) > 30:
            
            if self.ovhg>0:
                d = self.crick[-self.ovhg:][::-1]
                hej = len(d)
                if len(d)>10:
                    d = "{}..{}".format(d[:4], d[-4:])
                a = len(d)*" "
                
            elif self.ovhg<0:
                a = self.watson[:max(0,-self.ovhg)]
                hej = len(a)
                if len(a)>10:
                    a = "{}..{}".format(a[:4], a[-4:])
                d = len(a)*" "
            else:
                a = ""
                d = ""
                hej=0
            
            x = self.ovhg+len(self.watson)-len(self.crick)

            if x>0:
                c=self.watson[len(self.crick)-self.ovhg:]
                y=len(c)
                if len(c)>10:
                    c = "{}..{}".format(c[:4], c[-4:])
                f=len(c)*" "
            elif x<0:
                f=self.crick[:-x][::-1]
                y=len(f)
                if len(f)>10:
                    f = "{}..{}".format(f[:4], f[-4:])
                c=len(f)*" "
            else:
                c = ""
                f = ""
                y=0
                
            L = len(self)-hej-y
            x1 = -min(0, self.ovhg)
            x2 = x1+L
            x3 = -min(0, x)
            x4 = x3+L
            
            b=self.watson[x1:x2]
            e=self.crick[x3:x4][::-1]
            
            if len(b)>10:
                b = "{}..{}".format(b[:4], b[-4:])
                e = "{}..{}".format(e[:4], e[-4:])
            
            #import sys;sys.exit()
            
            return ("{klass}({top}{size})\n"
                    "{a}{b}{c}\n"
                    "{d}{e}{f}").format(klass = self.__class__.__name__,
                                          top = {True:"-", False:"o"}[self.linear],
                                          size = len(self),
                                          a=a,
                                          b=b,                        
                                          c=c,
                                          d=d,
                                          e=e,
                                          f=f,)  
            
         
        else:
            return "{}({}{})\n{}\n{}".format(self.__class__.__name__,
                                                {True:"-", False:"o"}[self.linear],
                                                len(self),
                                                self._ovhg*" " + self.watson,
                                               -self._ovhg*" "+ self.crick[::-1])

    def rc(self):
        '''Alias of the reverse_complement method'''
        return self.reverse_complement()

    def reverse_complement(self):
        '''Returns a Dseq object where watson and crick have switched
        places.

       '''
        ovhg = len(self.watson) - len(self.crick) + self._ovhg
        return Dseq(self.crick, self.watson, ovhg=ovhg, circular = self.circular)

    def looped(self):
        '''Returns a circularized Dseq object. This can only be done if the
       two ends are compatible, otherwise a TypeError is raised.

       Examples
       --------

       >>> import pydna
       >>> a=pydna.Dseq("catcgatc")
       >>> a
       Dseq(-8)
       catcgatc
       gtagctag
       >>> a.looped()
       Dseq(o8)
       catcgatc
       gtagctag
       >>> a.T4("t")
       Dseq(-8)
       catcgat
        tagctag
       >>> a.T4("t").looped()
       Dseq(o7)
       catcgat
       gtagcta
       >>> a.T4("a")
       Dseq(-8)
       catcga
         agctag
       >>> a.T4("a").looped()
       Traceback (most recent call last):
         File "<stdin>", line 1, in <module>
         File "/usr/local/lib/python2.7/dist-packages/pydna/dsdna.py", line 357, in looped
           if type5 == type3 and str(sticky5) == str(rc(sticky3)):
       TypeError: DNA cannot be circularized.
       5' and 3' sticky ends not compatible!
       >>>

       '''
        if self.circular:
            return self
        type5, sticky5 = self.five_prime_end()
        type3, sticky3 = self.three_prime_end()
        if type5 == type3 and str(sticky5) == str(rc(sticky3)):
            nseq = Dseq(self.watson, self.crick[-self._ovhg:] + self.crick[:-self._ovhg], 0, circular=True)
            assert len(nseq.crick) == len(nseq.watson)
            return nseq
        else:
            raise TypeError("DNA cannot be circularized.\n"
                             "5' and 3' sticky ends not compatible!")

    def tolinear(self):
        '''Returns a blunt, linear copy of a circular Dseq object. This can
       only be done if the Dseq object is circular, otherwise a
       TypeError is raised.

       Examples
       --------

       >>> import pydna
       >>> a=pydna.Dseq("catcgatc", circular=True)
       >>> a
       Dseq(o8)
       catcgatc
       gtagctag
       >>> a.tolinear()
       Dseq(-8)
       catcgatc
       gtagctag
       >>>

       '''

        if self.linear:
            raise TypeError("DNA is not circular.\n")
        return self.__class__(self.watson, self.crick, ovhg=0, linear=True)

    def five_prime_end(self):
        '''Returns a tuple describing the structure of the 5' end of
        the DNA fragment

        >>> import pydna
        >>> a=pydna.Dseq("aaa", "ttt")
        >>> a
        Dseq(-3)
        aaa
        ttt
        >>> a.five_prime_end()
        ('blunt', '')
        >>> a=pydna.Dseq("aaa", "ttt", ovhg=1)
        >>> a
        Dseq(-4)
         aaa
        ttt
        >>> a.five_prime_end()
        ("3'", 't')
        >>> a=pydna.Dseq("aaa", "ttt", ovhg=-1)
        >>> a
        Dseq(-4)
        aaa
         ttt
        >>> a.five_prime_end()
        ("5'", 'a')
        >>>


        '''
        if self.watson and not self.crick:
            return "5'",self.watson.lower()
        if not self.watson and self.crick:
            return "3'",self.crick.lower()
        if self._ovhg < 0:
            sticky = self.watson[:-self._ovhg].lower()
            type_ = "5'"
        elif self._ovhg > 0:
            sticky = self.crick[-self._ovhg:].lower()
            type_ = "3'"
        else:
            sticky = ""
            type_ = "blunt"
        return type_, sticky

    def three_prime_end(self):
        '''Returns a tuple describing the structure of the 5' end of
        the DNA fragment



        >>> import pydna
        >>> a=pydna.Dseq("aaa", "ttt")
        >>> a
        Dseq(-3)
        aaa
        ttt
        >>> a.three_prime_end()
        ('blunt', '')
        >>> a=pydna.Dseq("aaa", "ttt", ovhg=1)
        >>> a
        Dseq(-4)
         aaa
        ttt
        >>> a.three_prime_end()
        ("3'", 'a')
        >>> a=pydna.Dseq("aaa", "ttt", ovhg=-1)
        >>> a
        Dseq(-4)
        aaa
         ttt
        >>> a.three_prime_end()
        ("5'", 't')
        >>>


        '''

        ovhg = len(self.watson)-len(self.crick)+self._ovhg

        if ovhg < 0:
            sticky = self.crick[:-ovhg].lower()
            type_ = "5'"
        elif ovhg > 0:
            sticky = self.watson[-ovhg:].lower()
            type_ = "3'"
        else:
            sticky = ''
            type_ = "blunt"
        return type_, sticky

    def __add__(self, other):
        '''Simulates ligation between two DNA fragments.

        Add other Dseq object at the end of the sequence.
        Type error if all of the points below are fulfilled:

        * either objects are circular
        * if three prime sticky end of self is not the same type
          (5' or 3') as the sticky end of other
        * three prime sticky end of self complementary with five
          prime sticky end of other.

        Phosphorylation and dephosphorylation is not considered.
        DNA is allways presumed to have the necessary 5' phospate
        group necessary for ligation.

       '''
        # test for circular DNA
        if self.circular:
            raise TypeError("circular DNA cannot be ligated!")
        try:
            if other.circular:
                raise TypeError("circular DNA cannot be ligated!")
        except AttributeError:
            pass

        self_type,  self_tail  = self.three_prime_end()
        other_type, other_tail = other.five_prime_end()
        
        if (self_type == other_type and
            str(self_tail) == str(rc(other_tail))):
            answer = Dseq(self.watson + other.watson,
                          other.crick + self.crick,
                          self._ovhg,)
        elif not self:
            answer = copy.copy(other)
        elif not other:
            answer = copy.copy(self)
        else:
            raise TypeError("sticky ends not compatible!")
        return answer

    def __mul__(self, number):
        if not isinstance(number, int):
            raise TypeError("TypeError: can't multiply Dseq by non-int of type {}".format(type(number)))
        if number<=0:
            return self.__class__("")
        new = copy.copy(self)
        for i in range(number-1):
            new += self
        return new

    def _fill_in_five_prime(self, nucleotides):
        stuffer = ''
        type, se = self.five_prime_end()
        if type == "5'":
            for n in rc(se):
                if n in nucleotides:
                    stuffer+=n
                else:
                    break
        return self.crick+stuffer, self._ovhg+len(stuffer)

    def _fill_in_three_prime(self, nucleotides):
        stuffer = ''
        type, se = self.three_prime_end()
        if type == "5'":
            for n in rc(se):
                if n in nucleotides:
                    stuffer+=n
                else:
                    break
        return self.watson+stuffer

    def fill_in(self, nucleotides=None):
        '''Fill in of five prime protruding end with a DNA polymerase
        that has only DNA polymerase activity (such as exo-klenow)
        and any combination of A, G, C or T. Default are all four
        nucleotides together.

        Examples
        --------

        >>> import pydna
        >>> a=pydna.Dseq("aaa", "ttt")
        >>> a
        Dseq(-3)
        aaa
        ttt
        >>> a.fill_in()
        Dseq(-3)
        aaa
        ttt
        >>> b=pydna.Dseq("caaa", "cttt")
        >>> b
        Dseq(-5)
        caaa
         tttc
        >>> b.fill_in()
        Dseq(-5)
        caaag
        gtttc
        >>> b.fill_in("g")
        Dseq(-5)
        caaag
        gtttc
        >>> b.fill_in("tac")
        Dseq(-5)
        caaa
         tttc
        >>> b=pydna.Dseq("aaac", "tttg")
        >>> c=pydna.Dseq("aaac", "tttg")
        >>> c
        Dseq(-5)
         aaac
        gttt
        >>> c.fill_in()
        Dseq(-5)
         aaac
        gttt
        >>>

        '''
        if not nucleotides:
            nucleotides = self.alphabet.letters
        nucleotides = set(nucleotides.lower()+nucleotides.upper())
        crick, ovhg = self._fill_in_five_prime(nucleotides)
        watson = self._fill_in_three_prime(nucleotides)
        return Dseq(watson, crick, ovhg)

    def mung(self):
        '''
       Simulates treatment a nuclease with 5'-3' and 3'-5' single
       strand specific exonuclease activity (such as mung bean nuclease)::

            ggatcc    ->     gatcc
             ctaggg          ctagg

             ggatcc   ->      ggatc
            tcctag            cctag

        >>> import pydna
        >>> b=pydna.Dseq("caaa", "cttt")
        >>> b
        Dseq(-5)
        caaa
         tttc
        >>> b.mung()
        Dseq(-3)
        aaa
        ttt
        >>> c=pydna.Dseq("aaac", "tttg")
        >>> c
        Dseq(-5)
         aaac
        gttt
        >>> c.mung()
        Dseq(-3)
        aaa
        ttt
        '''
        return Dseq(self.dsdata)

    def t4(self,*args,**kwargs):
        '''Alias for the T4 method'''
        return self.T4(*args,**kwargs)

    def T4(self, nucleotides=None):
        '''Fill in of five prime protruding ends and chewing back of
       three prime protruding ends by a DNA polymerase providing both
       5'-3' DNA polymerase activity and 3'-5' nuclease acitivty
       (such as T4 DNA polymerase). This in presence of any
       combination of A, G, C or T. Default are all four
       nucleotides together.

       Examples
       --------

       >>> import pydna
       >>> a=pydna.Dseq("gatcgatc")
       >>> a
       Dseq(-8)
       gatcgatc
       ctagctag
       >>> a.T4()
       Dseq(-8)
       gatcgatc
       ctagctag
       >>> a.T4("t")
       Dseq(-8)
       gatcgat
        tagctag
       >>> a.T4("a")
       Dseq(-8)
       gatcga
         agctag
       >>> a.T4("g")
       Dseq(-8)
       gatcg
          gctag
       >>>

       '''

        if not nucleotides: nucleotides = self.alphabet.letters
        nucleotides = set(nucleotides.lower() + nucleotides.upper())
        type, se = self.five_prime_end()
        crick = self.crick
        if type == "5'":
            crick, ovhg = self._fill_in_five_prime(nucleotides)
        else:
            if type == "3'":
                ovhg = 0
                crick = self.crick[:-len(se)]
        x = len(crick)-1
        while x>=0:
            if crick[x] in nucleotides:
                break
            x-=1
        ovhg = x-len(crick)+1
        crick = crick[:x+1]
        if not crick: ovhg=0
        watson = self.watson
        type, se = self.three_prime_end()
        if type == "5'":
            watson = self._fill_in_three_prime(nucleotides)
        else:
            if type == "3'":
                watson = self.watson[:-len(se)]
        x = len(watson)-1
        while x>=0:
            if watson[x] in nucleotides:
                break
            x-=1
        watson=watson[:x+1]
        return Dseq(watson, crick, ovhg)

    def _cut(self, *enzymes):

        output = []
        stack = []
        stack.extend(reversed(enzymes))
        while stack:
            top = stack.pop()
            if hasattr(top, "__iter__"):
                stack.extend(reversed(top))
            else:
                output.append(top)
        enzymes = output

        if not hasattr(enzymes, '__iter__'):
            enzymes = (enzymes,)

        if self.circular:
            frags=[self.tolinear()*3,]
        else:
            frags=[self,]

        newfrags=[]

        enzymes = [e for (p,e) in sorted([(enzyme.search(Seq(frags[0].dsdata))[::-1], enzyme) for enzyme in enzymes], reverse=True) if p]

        if not enzymes:
            return [self,]

        for enzyme in enzymes:
            for frag in frags:

                if enzyme.search(Seq(frag.dsdata)):

                    watson_fragments = [str(s) for s in enzyme.catalyze(Seq(frag.watson+"N"))]
                    crick_fragments  = [str(s) for s in enzyme.catalyze(Seq(frag.crick+"N" ))[::-1]]

                    watson_fragments[-1] = watson_fragments[-1][:-1]
                    crick_fragments[0]   = crick_fragments[0][:-1]

                    s = zip(watson_fragments, crick_fragments)

                    if frag.linear:
                        newfrags.append(Dseq(*s.pop(0),
                                             ovhg = frag.ovhg,
                                             linear = True))
                        for seqs in s:
                            newfrags.append(Dseq(*seqs,
                                                 ovhg = enzyme.ovhg,
                                                 linear = True))
                    else:
                        for seqs in s:
                            newfrags.append(Dseq(*seqs,
                                                 ovhg=enzyme.ovhg,
                                                 linear=True))
                else:
                    newfrags.append(frag)
            frags=newfrags
            newfrags=[]

        if self.circular:
            swl = len(self.watson)
            frags = frags[1:-1]
            newfrags = [frags.pop(0),]
            while sum(len(f.watson) for f in newfrags) < swl:
                newfrags.append(frags.pop(0))
            frags = newfrags

        return frags

    def cut(self, *enzymes):
        '''Returns a list of linear Dseq fragments produced in the digestion.
        If there is not cut, an empty list is returned.


        Examples
        --------

        >>> from pydna import Dseq
        >>> seq=Dseq("ggatccnnngaattc")
        >>> seq
        Dseq(-15)
        ggatccnnngaattc
        cctaggnnncttaag
        >>> from Bio.Restriction import BamHI,EcoRI
        >>> type(seq.cut(BamHI))
        <type 'list'>
        >>> for frag in seq.cut(BamHI):
        ...     print frag.fig()
        Dseq(-5)
        g
        cctag
        Dseq(-14)
        gatccnnngaattc
            gnnncttaag
        >>> seq.cut(EcoRI, BamHI) ==  seq.cut(BamHI, EcoRI)
        True
        >>> a,b,c = seq.cut(EcoRI, BamHI)
        >>> a+b+c
        Dseq(-15)
        ggatccnnngaattc
        cctaggnnncttaag
        >>>

        '''
        output = []
        stack = []
        stack.extend(reversed(enzymes))
        while stack:
            top = stack.pop()
            if hasattr(top, "__iter__"):
                stack.extend(reversed(top))
            else:
                output.append(top)
        enzymes = output
        if not hasattr(enzymes, '__iter__'):
            enzymes = (enzymes,)

        if self.circular:
            frags=[self.tolinear()*3,]
        else:
            frags=[self,]

        newfrags=[]

        enzymes = [e for (p,e) in sorted([(enzyme.search(Seq(frags[0].dsdata))[::-1], enzyme) for enzyme in enzymes], reverse=True) if p]

        if not enzymes:
            return []

        for enz in enzymes:
            for frag in frags:

                ws = [x-1 for x in enz.search(Seq(frag.watson)+"N")] #, linear = frag.linear
                cs = [x-1 for x in enz.search(Seq(frag.crick) +"N")] #, linear = frag.linear

                sitepairs = [(sw, sc) for sw, sc in zip(ws,cs[::-1])
                             if (sw + max(0, frag.ovhg) -
                             max(0, enz.ovhg)
                             ==
                             len(frag.crick)-sc -
                             min(0, frag.ovhg) +
                             min(0, enz.ovhg))]

                sitepairs = sitepairs + [(len(frag.watson), 0)]

                w2, c1 = sitepairs[0]

                nwat = frag.watson[:w2]
                ncrk = frag.crick[c1:]

                newfrags.append(Dseq(nwat, ncrk, ovhg=frag.ovhg))

                for (w1, c2), (w2, c1)  in zip(sitepairs[:-1], sitepairs[1:]):
                    nwat = frag.watson[w1:w2]
                    ncrk = frag.crick[c1:c2]
                    newfrag = Dseq(nwat, ncrk, ovhg = enz.ovhg)
                    newfrags.append(newfrag)

                if not newfrags:
                    newfrags.append(frag)

            frags=newfrags
            newfrags=[]

        if self.circular:
            swl = len(self.watson)
            frags = frags[1:-1]
            newfrags = [frags.pop(0),]
            while sum(len(f.watson) for f in newfrags) < swl:
                newfrags.append(frags.pop(0))
            frags = newfrags[-1:] + newfrags[:-1]

        return frags

    @property
    def ovhg(self):
        '''The ovhg property'''
        return self._ovhg

    @property
    def linear(self):
        '''The linear property'''
        return self._linear

    @property
    def circular(self):
        '''The circular property'''
        return self._circular


class Dseqrecord(SeqRecord):
    '''Dseqrecord is a double stranded version of the Biopython SeqRecord class.
    The Dseqrecord object holds a Dseq object describing the sequence.
    Additionally, Dseqrecord hold meta information about the sequence in the
    from of a list of SeqFeatures, in the same way as the SeqRecord does.
    The Dseqrecord can be initialized with a string, Seq, Dseq, SeqRecord
    or another Dseqrecord. The sequence information will be stored in a
    Dseq object in all cases. Dseqrecord objects can be read or parsed
    from sequences in Fasta, Embl or Genbank format.

    There is a short representation associated with the Dseqrecord.
    ``Dseqrecord(-3)`` represents a linear sequence of length 2
    while ``Dseqrecord(o7)``
    represents a circular sequence of length 7.

    Dseqrecord and Dseq share the same concept of length
    ::

        <-- length -->
        GATCCTTT
             AAAGCCTAG




    Parameters
    ----------
    record  : string, Seq, SeqRecord, Dseq or other Dseqrecord object
        This data will be used to form the seq property

    circular : bool, optional
        True or False reflecting the shape of the DNA molecule

    linear : bool, optional
        True or False reflecting the shape of the DNA molecule


    Examples
    --------

    >>> from pydna import Dseqrecord
    >>> a=Dseqrecord("aaa")
    >>> a
    Dseqrecord(-3)
    >>> a.seq
    Dseq(-3)
    aaa
    ttt
    >>> from Bio.Seq import Seq
    >>> b=Dseqrecord(Seq("aaa"))
    >>> b
    Dseqrecord(-3)
    >>> b.seq
    Dseq(-3)
    aaa
    ttt
    >>> from Bio.SeqRecord import SeqRecord
    >>> c=Dseqrecord(SeqRecord(Seq("aaa")))
    >>> c
    Dseqrecord(-3)
    >>> c.seq
    Dseq(-3)
    aaa
    ttt
    >>> a.seq.alphabet
    IUPACAmbiguousDNA()
    >>> b.seq.alphabet
    IUPACAmbiguousDNA()
    >>> c.seq.alphabet
    IUPACAmbiguousDNA()
    >>>

    '''

    def __init__(self, record,
                       circular               = None,
                       linear                 = None,
                       n                      = 10E-12, # pmols
                       *args, 
                       **kwargs):
        self.n = n
        if circular == None and linear in (True, False,):
            circular = not linear
        elif linear == None and circular in (True, False,):
            linear   = not circular

        if isinstance(record, basestring):  # record is a string
            SeqRecord.__init__(self,
                               Dseq(record,
                                    rc(record),
                                    ovhg=0 ,
                                    linear=linear,
                                    circular=circular),
                               *args,
                               **kwargs)
        elif hasattr(record, "features"): # record is SeqRecord or Dseqrecord?
            for key, value in record.__dict__.items():
                setattr(self, key, value )                
            if hasattr(record.seq, "watson"): # record.seq is a Dseq, so record is Dseqrecord
                new_seq = copy.copy(record.seq)
                if new_seq.circular and linear:
                    new_seq = new_seq.tolinear()
                if new_seq.linear and circular:
                    new_seq = new_seq.looped()
                self.seq=new_seq
            else:                             # record is Bio.SeqRecord
                self.seq=Dseq(str(self.seq),
                              rc(str(self.seq)),
                              ovhg=0 ,
                              linear=linear,
                              circular=circular)
        elif hasattr(record, "watson"):      # record is Dseq ?
            if record.circular and linear:
                record = record.tolinear()
            if record.linear and circular:
                record = record.looped()
            SeqRecord.__init__(self, record, *args, **kwargs)
        elif isinstance(record, Seq):         # record is Bio.Seq ?
            SeqRecord.__init__(self, Dseq(str(record),
                                          str(record.reverse_complement()),
                                          ovhg=0 ,
                                          linear=linear,
                                          circular=circular),
                                          *args,
                                          **kwargs)
        else:
            raise TypeError(("record argument needs to be a string,"
                              "Seq, SeqRecord, Dseq or Dseqrecord object,"
                              " got {}").format(type(record)))

        if self.id in ("","."):
            self.id = self.name[:7]

        if self.description ==".":
            self.description = ""

        if not 'date' in self.annotations:
            self.annotations.update({"date": datetime.date.today().strftime("%d-%b-%Y").upper()})

    @property
    def linear(self):
        '''Not really a method, but the linear property'''
        return self.seq.linear

    @property
    def circular(self):
        '''Not really a method, but the circular property'''
        return self.seq.circular

    def seguid(self):
        '''Returns the SEGUID for the sequence

       Examples
       --------

       >>> import pydna
       >>> a=pydna.Dseqrecord("aaa")
       >>> a.seguid()
       'YG7G6b2Kj/KtFOX63j8mRHHoIlE'

       '''
        return seguid(self.seq)

    def cseguid(self):
        '''Returns the cSEGUID for the sequence

       Examples
       --------

       >>> import pydna
       >>> a=pydna.Dseqrecord("aaat", circular=True)
       >>> a.cseguid()
       'oopV+6158nHJqedi8lsshIfcqYA'
       >>> a=pydna.Dseqrecord("ataa", circular=True)
       >>> a.cseguid()
       'oopV+6158nHJqedi8lsshIfcqYA'

       '''
        if self.linear:
            raise Exception("cseguid is only defined for circular sequences.")
        return cseguid(self.seq)

    def stamp(self):
        '''Adds a seguid stamp to the description property. This will
        show in the genbank format. The following string:

        ``SEGUID <seguid>``

        will be appended to the description property of the Dseqrecord
        object (string).

        Examples
        --------

        >>> import pydna
        >>> a=pydna.Dseqrecord("aaa")
        >>> a.stamp()
        >>> a.description
        '<unknown description> SEGUID YG7G6b2Kj/KtFOX63j8mRHHoIlE'
        >>> a.verify_stamp()
        True

        '''
        pattern = "(SEGUID|seguid)\s*\S{27}"
        try:
            stamp = re.search(pattern, self.description).group()
        except AttributeError:
            stamp = "SEGUID {}".format(seguid(self.seq))

        if not self.description:
            self.description = stamp
        elif not re.search(pattern, self.description):
            self.description += " "+stamp

    def verify_stamp(self):
        '''Verifies the SEGUID stamp in the description property is
       valid. True if stamp match the sequid calculated from the sequence.
       Exception raised if no stamp can be found.

        >>> import pydna
        >>> a=pydna.Dseqrecord("aaa")
        >>> a.annotations['date'] = '02-FEB-2013'
        >>> a.seguid()
        'YG7G6b2Kj/KtFOX63j8mRHHoIlE'
        >>> print a.format("gb")
        LOCUS       .                          3 bp    DNA     linear   UNK 02-FEB-2013
        DEFINITION  .
        ACCESSION   <unknown id>
        VERSION     <unknown id>
        KEYWORDS    .
        SOURCE      .
          ORGANISM  .
                    .
        FEATURES             Location/Qualifiers
        ORIGIN
                1 aaa
        //
        >>> a.stamp()
        >>> a
        Dseqrecord(-3)
        >>> print a.format("gb")
        LOCUS       .                          3 bp    DNA     linear   UNK 02-FEB-2013
        DEFINITION  <unknown description> SEGUID YG7G6b2Kj/KtFOX63j8mRHHoIlE
        ACCESSION   <unknown id>
        VERSION     <unknown id>
        KEYWORDS    .
        SOURCE      .
          ORGANISM  .
                    .
        FEATURES             Location/Qualifiers
        ORIGIN
                1 aaa
        //
        >>> a.verify_stamp()
        True
        >>>


       '''
        pattern = "(SEGUID|seguid)\s*\S{27}"
        try:
            stamp = re.search(pattern, self.description).group()
        except AttributeError:
            raise Exception("No stamp present in the description property.")
        return seguid(self.seq) == stamp[-27:]

    def looped(self):
        '''
        Returns a circular version of the Dseqrecord object. The
        underlying Dseq object has to have compatible ends.

        Examples
        --------
        >>> import pydna
        >>> a=pydna.Dseqrecord("aaa")
        >>> a
        Dseqrecord(-3)
        >>> b=a.looped()
        >>> b
        Dseqrecord(o3)
        >>>
        '''
        new = copy.copy(self)
        for key, value in self.__dict__.items():
            setattr(new, key, value )        
        new._seq = self.seq.looped()
        for fn, fo in zip(new.features, self.features):
            fn.qualifiers = fo.qualifiers
            
        return new

    def tolinear(self):
        '''
        Returns a linear, blunt copy of a circular Dseqrecord object. The
        underlying Dseq object has to be circular.

        Examples
        --------
        >>> import pydna
        >>> a=pydna.Dseqrecord("aaa", circular = True)
        >>> a
        Dseqrecord(o3)
        >>> b=a.tolinear()
        >>> b
        Dseqrecord(-3)
        >>>
        
        '''

        new = copy.copy(self)
        for key, value in self.__dict__.items():
            setattr(new, key, value )
        new._seq = self.seq.tolinear()
        for fn, fo in zip(new.features, self.features):
            fn.qualifiers = fo.qualifiers
        
        return new

    def format(self, f="gb"):
        '''Returns the sequence as a string using a format supported by Biopython
        SeqIO. Default is "gb" which is short for Genbank.

        Examples
        --------
        >>> import pydna
        >>> a=pydna.Dseqrecord("aaa")
        >>> a.annotations['date'] = '02-FEB-2013'
        >>> a
        Dseqrecord(-3)
        >>> print a.format()
        LOCUS       .                          3 bp    DNA     linear   UNK 02-FEB-2013
        DEFINITION  .
        ACCESSION   <unknown id>
        VERSION     <unknown id>
        KEYWORDS    .
        SOURCE      .
          ORGANISM  .
                    .
        FEATURES             Location/Qualifiers
        ORIGIN
                1 aaa
        //

        '''

        s = SeqRecord.format(self, f).strip()
        if f in ("genbank","gb"):
            if self.circular:
                return s[:55]+"circular"+s[63:]
            else:
                return s[:55]+"linear"+s[61:]
        else:
            return s

    def write(self, filename=None, f="gb"):
        '''Writes the Dseqrecord to a file using the format f, which must
        be a format supported by Biopython SeqIO. Default is "gb"
        which is short for Genbank.

        Filename is the path to the file where the sequece is to be
        written. The filename is optional, if it is not given, the
        description property (string) is used together with the format:

        If obj is the Dseqrecord object, the default file name will be:

        ``<obj.description>.<f>``

        If the filename already exists and the sequence it contains
        is different, a new file name will be used:

        ``<obj.description>_NEW.<f>``

       '''
        if not filename:
            filename = self.description + "." + f
        if isinstance(filename, basestring):
            if os.path.isfile(filename):
                seguid_new=self.seguid()
                old_file = read(filename)
                seguid_old = old_file.seguid()
                if  seguid_new == seguid_old and self.circular == old_file.circular:
                    os.utime(filename, None)
                else:
                    name, ext = os.path.splitext(filename)
                    new_filename = "{}_NEW{}".format(name, ext)
                    print("\n\nseguid(old) = {} in file {}"
                           "\nseguid(new) = {} in file {}\n").format(seguid_old, filename, seguid_new, new_filename)
                    with open(new_filename, "w") as fp:
                        fp.write(self.format(f))

            else:
                with open(filename, "w") as fp:
                    fp.write(self.format(f))
        else:
            with filename as fp:
                fp.write(self.format(f))

    def __str__(self):
        return ("Dseqrecord\n"
                 "circular: {}\n"
                 "size: {}\n").format(self.circular, len(self))+SeqRecord.__str__(self)

    def __repr__(self):
        return "Dseqrecord({}{})".format({True:"-", False:"o"}[self.linear],len(self))

    def __add__(self, other):
        if hasattr(other, "seq") and hasattr(other.seq, "watson"):
            offset = other.seq.ovhg
            other.features = [f._shift(offset) for f in other.features]
            #answer = self.__class__(SeqRecord.__add__(self, other))
            answer = Dseqrecord(SeqRecord.__add__(self, other))
            answer.n = min(self.n, other.n)
        else:
            #answer = self.__class__(SeqRecord.__add__(self, Dseqrecord(other)))
            answer = Dseqrecord(SeqRecord.__add__(self, Dseqrecord(other)))
            answer.n = self.n
        return answer

    def __mul__(self, number):
        if not isinstance(number, int):
            raise TypeError("TypeError: can't multiply Dseqrecord by non-int of type {}".format(type(number)))
        if self.circular:
            raise TypeError("TypeError: can't multiply circular Dseqrecord")
        if number>0:
            new = copy.copy(self)
            for i in range(1, number):
                new += self
            return new
        else:
            return self.__class__("")

    def __getitem__(self, sl):
        answer = copy.copy(self)
        answer.seq = answer.seq.__getitem__(sl)
        answer.seq.alphabet = self.seq.alphabet
        answer.features = SeqRecord.__getitem__(self, sl).features      
        return answer

    def linearize(self, *enzymes):
        if self.seq._linear:
            raise Exception("Can only linearize circular molecules!")
        fragments = self.cut(*enzymes)
        if len(fragments)>1:
            raise Exception("More than one fragment is formed!")
        if not fragments:
            raise Exception("The enzyme(s) do not cut!")
        return fragments.pop()

    def cut(self, *enzymes):
        '''Digest the Dseqrecord object with one or more restriction enzymes.
       returns a list of linear Dseqrecords. If enzymes do not cut, and empty
       list is returned.

       Parameters
       ----------
       enzymes : iterable object
            iterable containing Biopython
            restriction enzyme objects

       Returns
       -------
       fragments : list
            list of Dseqrecord objects formed by the digestion

       Examples
       --------

       >>> import pydna
       >>> a=pydna.Dseqrecord("ggatcc")
       >>> from Bio.Restriction import BamHI
       >>> a.cut(BamHI)
       [Dseqrecord(-5), Dseqrecord(-5)]
       >>> frag1, frag2 = a.cut(BamHI)
       >>> frag1.seq
       Dseq(-5)
       g
       cctag
       >>> frag2.seq
       Dseq(-5)
       gatcc
           g


       '''
        output, stack = [], []
        stack.extend(reversed(enzymes))
        while stack:
            top = stack.pop()
            if hasattr(top, "__iter__"):
                stack.extend(reversed(top))
            else:
                output.append(top)
        enzymes = output
        if not hasattr(enzymes, '__iter__'):
            enzymes = (enzymes,)

        frags = self.seq.cut(enzymes)
        

        
        if not frags:
            return []

        if self.linear:
            last_pos=0
            #template = self.__class__(self, linear=True)
            #template = copy.copy(self)
            template = self
        else:
            last_pos = [p.pop(0)-max(0,enzyme.ovhg)-1 for (p,e) in
                         sorted([(enzyme.search(Seq(self.seq.dsdata),
                                                linear = self.linear)[::-1],
                                   enzyme) for enzyme in enzymes]) if p]
            if not last_pos:
                return [self]
            if 0 in last_pos:
                last_pos=0
            else:
                last_pos = last_pos.pop()
            template = self._multiply_circular(3)

        Dseqrecord_frags = []
        start = last_pos

        for f in frags:
            end = start + len(str(f))
            Dseqrecord_frag = Dseqrecord(f, linear=True, n=self.n)
            Dseqrecord_frag.features = template[start:end].features

            Dseqrecord_frag.annotations         = copy.copy(self[start:end].annotations) 
            Dseqrecord_frag.name                = copy.copy(self.name)
            Dseqrecord_frag.dbxrefs             = copy.copy(self[start:end].dbxrefs)
            Dseqrecord_frag.id                  = copy.copy(self.id)
            Dseqrecord_frag.letter_annotations  = copy.copy(self[start:end].letter_annotations)

            Dseqrecord_frag.description = self.description+"_"+"_".join(str(e) for e in enzymes)

            Dseqrecord_frags.append(Dseqrecord_frag)
            start = end
            start-= len(f.three_prime_end()[1])

        return Dseqrecord_frags


    def reverse_complement(self):
        '''Returns a new Dseqrecord object which is the reverse complement.

       Examples
       --------
       >>> import pydna
       >>> a=pydna.Dseqrecord("ggaatt")
       >>> a
       Dseqrecord(-6)
       >>> a.seq
       Dseq(-6)
       ggaatt
       ccttaa
       >>> a.reverse_complement().seq
       Dseq(-6)
       aattcc
       ttaagg
       >>>
       '''

        return self.rc()

    def rc(self):
        '''alias of the reverse_complement method'''
        answer = Dseqrecord(super(Dseqrecord, self).reverse_complement())   
        assert answer.circular == self.circular
        answer.name       = "{}_rc".format(self.name[:13])
        answer.description= self.description+"_rc"
        answer.id         = self.id+"_rc"
        return answer
        #return Dseqrecord(self.seq.rc())


    def _multiply_circular(self, multiplier):
        '''returns a linearised version of a circular sequence multiplied by
       multiplier '''

        if self.linear:
            raise TypeError("sequence has to be circular!")
        if not isinstance(multiplier, int):
            raise TypeError("TypeError: can't multiply Dseq by non-int of type {}".format(type(multiplier)))
        if multiplier<=0:
            return self.__class__("")

        new_features = []
        
        for feature in self.features:            
            new_feature = copy.deepcopy(feature)            
            if len(new_feature.location.parts)>1:    # CompoundFeature
                j=0
                while (j+1)<=len(new_feature.location.parts):
                    if new_feature.location.parts[j].end == len(self) and new_feature.location.parts[j+1].start==0:
                        new_feature.location.parts[j] = FeatureLocation(new_feature.location.parts[j].start, 
                                                                        new_feature.location.parts[j].end+len(new_feature.location.parts[j+1]))
                        del new_feature.location.parts[j+1]
                    j+=1
                slask = [new_feature.location.parts.pop(0)]
                for fl in new_feature.location.parts:
                    if fl.start < slask[-1].start:
                        slask.append(fl+len(self))
                    else:
                        slask.append(fl)
                if len(slask)>1:
                    new_feature.location.parts=slask
                else:
                    new_feature.location=slask[0]            
            new_features.append(new_feature)
        
        sequence = self.tolinear()       
        sequence.features = new_features
        sequence = sequence * multiplier
                
        sequence.features = [f for f in sequence.features if f.location.end <= len(sequence)]        
        sequence.features.sort(key = operator.attrgetter('location.start'))

        return sequence

    def shifted(self, shift):
        '''Returns a circular Dseqrecord with a new origin <shift>.
        This only works on circular Dseqrecords. If we consider the following
        circular sequence:


        | ``GAAAT   <-- watson strand``
        | ``CTTTA   <-- crick strand``

        The T and the G on the watson strand are linked together as well
        as the A and the C of the of the crick strand.

        if ``shift`` is 1, this indicates a new origin at position 1:

        |    new origin
        |
        | ``G|AAAT``
        | ``C|TTTA``

        new sequence:

        | ``AAATG``
        | ``TTTAC``

        Shift is always positive and 0<shift<length, so in the example
        below, permissible values of shift are 1,2 and 3

        >>> import pydna
        >>> a=pydna.Dseqrecord("aaat",circular=True)
        >>> a
        Dseqrecord(o4)
        >>> a.seq
        Dseq(o4)
        aaat
        ttta
        >>> b=a.shifted(1)
        >>> b
        Dseqrecord(o4)
        >>> b.seq
        Dseq(o4)
        aata
        ttat

        '''
        if self.linear:
            raise Exception("Sequence is linear.\n"
                             "The origin can only be\n"
                             "shifted for a circular sequence!\n")

        length=len(self)
        
        if not 0<shift<length:
            raise Exception("shift is {}, has to be 0<shift<{}".format(shift, length))

        new = self._multiply_circular(3)[shift:]

        features_to_fold = [f for f in new.features if f.location.start<length<f.location.end]

        folded_features = []

        for feature in features_to_fold:
                      
            if len(feature.location.parts)>1: # CompoundFeature
                nps=[]
                for part in feature.location.parts:
                    
                    if part.start<part.end<=length:
                        nps.append(part)

                    elif part.start<length<part.end:
                        nps.append(FeatureLocation(part.start,length))
                        nps.append(FeatureLocation(0, part.end-length))
                        
                    elif length<=part.start<part.end:
                        nps.append(FeatureLocation(part.start-length, part.end-length))
                    
                folded_features.append(SeqFeature(CompoundLocation(nps),
                                                  qualifiers = feature.qualifiers,
                                                  type=feature.type))

            else:
                folded_features.append(SeqFeature(CompoundLocation([FeatureLocation(feature.location.start, length),
                                                                    FeatureLocation(0, feature.location.end-length)]),
                                                  qualifiers = feature.qualifiers,
                                                  type=feature.type))

        new = new[:length].looped()        
        new.features.extend(folded_features)
        new.features.sort(key = operator.attrgetter('location.start'))
        new.description = "{}_shifted ori {}".format(self.description, shift)
        return new


    def synced(self, ref, limit = 25):
        '''This function returns a new circular sequence (Dseqrecord object), which has ben rotated
        in such a way that there is maximum overlap between the sequence and
        ref, which may be a string, Biopython Seq, SeqRecord object or
        another Dseqrecord object.

        The reason for using this could be to rotate a recombinant plasmid so
        that it starts at the same position after cloning. See the example below:


        Examples
        --------

        >>> import pydna
        >>> a=pydna.Dseqrecord("gaat",circular=True)
        >>> a.seq
        Dseq(o4)
        gaat
        ctta
        >>> d = a[2:] + a[:2]
        >>> d.seq
        Dseq(-4)
        atga
        tact
        >>> insert=pydna.Dseqrecord("CCC")
        >>> recombinant = (d+insert).looped()
        >>> recombinant.seq
        Dseq(o7)
        atgaCCC
        tactGGG
        >>> recombinant.synced(a).seq
        Dseq(o7)
        gaCCCat
        ctGGGta


        '''
        if self.linear:
            raise Exception("Only circular DNA can be synced!")

        sequence = self.seq.tolinear()

        a    = str(sequence.watson).lower()
        a_rc = str(sequence.crick).lower()
        
        sequence_rc = sequence.reverse_complement()
        #double_sequence = sequence+sequence

        if hasattr(ref, "seq"):
            b=ref.seq
            if hasattr(ref, "watson"):
                b = str(b.watson).lower()
            else:
                b = str(b).lower()
        else:
            b = str(ref.lower())

        b=b[:len(a)]

        c = common_sub_strings(a+a, b, limit = min(len(ref),limit, limit*(len(a)/limit)+1))
        d = common_sub_strings(a_rc+a_rc, b, limit = min(len(ref), limit, limit*(len(a)/limit)+1))

        #print c
        #print d

        if c:
            starta, startb, length = c.pop(0)
        else:
            starta, startb, length = 0,0,0

        if d:
            starta_rc, startb_rc, length_rc = d.pop(0)
        else:
            starta_rc, startb_rc, length_rc = 0,0,0

        if not c and not d:
            raise Exception("There is not sufficient overlap between sequences!")
        
        rc=False
        
        if length_rc>length:
            starta, startb = starta_rc, startb_rc
            rc=True

        if starta>startb:
            if len(a)<len(b):
                ofs = starta-startb + len(b)-len(a)
            else:
                ofs = starta-startb # + len(b)-len(a)
                #print ">>>", len(a), len(b), len(b)-len(a), ofs 
                
                #import sys;sys.exit()               
        elif starta<startb:
            ofs = startb-starta + len(a)-len(b)
            ofs = len(a)-ofs
        elif starta==startb:
            ofs=0
        
        if rc:
            return self.rc().shifted(ofs)
        else:
            return self.shifted(ofs)


def read(data, ds = True):
    '''This function is similar the parse funtion but returns only
    the first sequence found.

    Parameters
    ----------
    data : string
        see below
    ds : bool
        Double stranded or single stranded DNA, Return
        "Dseqrecord" or "SeqRecord" objects.

    Returns
    -------
    Dseqrecord
        contains the first Dseqrecord or SeqRecord object parsed.

    Notes
    -----

    The data parameter is similar to the data parameter for parse.

    See Also
    --------
    parse

    '''

    results = parse(data, ds)
    try:
        results = results.pop()
    except IndexError:
        raise ValueError("No sequences found in data ({})".format(data[:30]))
    return results

def parse(data, ds = True):
    '''This function returns *all* DNA sequences found in data. If no
    sequences are found, an empty list is returned. This is a greedy
    function, use carefully.

    Parameters
    ----------
    data : string or iterable
        see below
    ds : bool
        Double stranded or single stranded DNA, Return
        "Dseqrecord" or "SeqRecord" objects.

    Returns
    -------
    list
        contains Dseqrecord or SeqRecord objects

    Notes
    -----

    The data parameter is a string containing:

    1. an absolute path to a local file.
       The file will be read in text
       mode and parsed for EMBL, FASTA
       and Genbank sequences.

    2. an absolute path to a local directory.
       all files in the directory will be
       read and parsed as in 1.

    3. a string containing one or more
       sequences in EMBL, GENBANK,
       or FASTA format. Mixed formats
       are allowed.

    4. data can be a list or other iterable of 1 - 3

    '''
    raw= ""
    if not hasattr(data, '__iter__'):
        data = (data,)
    for item in data:
        if os.path.isdir(item):
            for file_ in os.listdir(item):
                with open(file_,'r') as f:
                    raw+="\n\n"+f.read()
        elif os.path.isfile(os.path.join(os.getcwd(),item)):
            with open(item,'r') as f:
                raw+= f.read()
        else:
            raw+=textwrap.dedent(item).strip()
    pattern =  r"(?:>.+\n^(?:^[^>]+?)(?=\n\n|>|LOCUS|ID))|(?:(?:LOCUS|ID)(?:(?:.|\n)+?)^//)"
    raw = raw.replace( '\r\n', '\n')
    raw = raw.replace( '\r',   '\n')
    rawseqs = re.findall(pattern, textwrap.dedent(raw+ "\n\n"),re.MULTILINE)
    sequences=[]

    while rawseqs:
        circular = False
        rawseq = rawseqs.pop(0)
        handle = StringIO.StringIO(rawseq)

        try:
            parsed = SeqIO.read(handle, "embl", alphabet=IUPACAmbiguousDNA())
            original_format = "embl"
            if "circular" in rawseq.splitlines()[0]:
                circular = True
        except ValueError:
            handle.seek(0)
            try:
                parsed = SeqIO.read(handle, "genbank", alphabet=IUPACAmbiguousDNA())
                original_format = "genbank"
                handle.seek(0)
                parser = RecordParser()
                residue_type = parser.parse(handle).residue_type
                if "circular" in residue_type:
                    circular = True
            except ValueError:
                handle.seek(0)
                try:
                    parsed = SeqIO.read(handle, "fasta", alphabet=IUPACAmbiguousDNA())
                    original_format = "fasta"
                    if "circular" in rawseq.splitlines()[0]:
                        circular = True
                except ValueError:
                    continue

        if ds:
            sequences.append(Dseqrecord(parsed, circular = circular))
        else:
            sequences.append(parsed)
        handle.close()
    #sequences[0].features[8].qualifiers['label'][0] = u'björn' 
    return sequences
    
    #http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?
    #db=nuccore&
    #id=21614549&
    #strand=1&
    #seq_start=1&
    #seq_stop=100&
    #rettype=gb&
    #retmode=text

if __name__=="__main__":
    import doctest
    doctest.testmod()
    
    
    print parse('''
NM_005546
>a
aaa 
''')
    
    
    
    
    
    
