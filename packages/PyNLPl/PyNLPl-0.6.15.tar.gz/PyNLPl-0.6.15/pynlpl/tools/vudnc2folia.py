#!/usr/bin/env python
#-*- coding:utf-8 -*-


#---------------------------------------------------------------
# PyNLPl - Conversion script for converting the VU-DNC corpus to FoLiA XML
#   by Maarten van Gompel, ILK, Tilburg University
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------


import sys
import os
from lxml import etree

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

import pynlpl.formats.folia as folia
import pynlpl.formats.sonar as sonar
from multiprocessing import Pool, Process
import datetime
import codecs



def process(data):
    i, filename = data
    category = os.path.basename(os.path.dirname(filename))
    progress = round((i+1) / float(len(index)) * 100,1)    
    print "#" + str(i+1) + " " + filename + ' ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' +  str(progress) + '%'
    try:
        doc = folia.Document(file=filename)
    except Exception as e:
        print >> sys.stderr,"ERROR loading " + filename + ":" + str(e)
        return False
    filename = filename.replace(sonardir,'')
    if filename[0] == '/':
        filename = filename[1:]
    if filename[-4:] == '.pos':
        filename = filename[:-4]
    if filename[-4:] == '.tok':
        filename = filename[:-4]    
    if filename[-4:] == '.ilk':
        filename = filename[:-4]    
    #Load document prior to tokenisation
    try:
        pretokdoc = folia.Document(file=sonardir + '/' + filename)
    except:
        print >> sys.stderr,"WARNING unable to load pretokdoc " + filename
        pretokdoc = None
    if pretokdoc:
        for p2 in pretokdoc.paragraphs():
            try:
                p = doc[p2.id]        
            except:
                print >> sys.stderr,"ERROR: Paragraph " + p2.id + " not found. Tokenised and pre-tokenised versions out of sync?"
                continue
            if p2.text:
                p.text = p2.text                     
    try:
        os.mkdir(foliadir + os.path.dirname(filename))
    except:
        pass
        
    try:        
        doc.save(foliadir + filename)
    except:
        print >> sys.stderr,"ERROR saving " + foliadir + filename
    
    try:
        f = codecs.open(foliadir + filename.replace('.xml','.tok.txt'),'w','utf-8')
        f.write(unicode(doc))    
        f.close()        
    except:
        print >> sys.stderr,"ERROR saving " + foliadir + filename.replace('.xml','.tok.txt')

            
    sys.stdout.flush()
    sys.stderr.flush()
    return True
    



if __name__ == '__main__':    
    inputdir = sys.argv[1]
    outputdir = sys.argv[2]
    threads = int(sys.argv[3])
    if outputdir[-1] != '/': outputdir += '/'
    try:
        os.mkdir(outputdir[:-1])
    except:
        pass
            
            
    print "Building index of all input files..."
    index = []
    for filepath in glob.glob(intputdir + '/*xml'):
        
    
    
    index = enumerate(index)

    print "Processing..."
    p = Pool(threads)
    p.map(process, index )

