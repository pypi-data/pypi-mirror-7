#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

#NaturalLanguageToolKit
from nltk.corpus import stopwords
from  nltk.tokenize import *
import nltk

import subprocess

import Parameters

class KeywordsList:
    keywords=[]

    def __init__(self, sentence, params):
        self.keywords = []

        self.treetagger=params.treetagger
        self.postag=params.postag
        self.lang = params.lang
        self.noun=params.noun
        self.adj=params.adj
        self.verb=params.verb
        self.default=params.default
        self.brute=params.brute

        nwords = sentence.count(' ')

        # Test case: "moi"
        if (nwords>0):
            keyw = self.removeStopWords(sentence)
            if self.postag:
                self.keywords = self.addScoreToKeywords(self.removeStopWords(sentence))
            else:
                self.keywords = self.removeStopWords(sentence)
        else:
            if self.postag:
                self.keywords.append([sentence,1])
            else:
                self.keywords = [sentence]

    def __len__(self):
        return len(self.keywords)

    def getWord(self, num):
        if self.postag:
            return self.keywords[num][0]
        else:
            return self.keywords[num]

    def getScore(self, num):
        if self.postag:
            return self.keywords[num][1]
        else:
            return 1


    ##    removeStopWords
    ##    Input:     String (FR)
    ##    Output:    List of [keywords,score]
    ##    note: can also output list of keyw only
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def removeStopWords(self,s):
        #We only want to work with lowercase for the comparisons
        s = s.lower()
        #remove punctuation and split into seperate words
        words = re.findall(r'\w+', s,flags = re.UNICODE | re.LOCALE)

        #This is the more pythonic way
        important_words = filter(lambda x: x not in stopwords.words(self.lang), words)
        # remove words like "ça" that becomes "a"
        important_words = filter(lambda x: len(x)>1, important_words)

        #return the keywords only
        return important_words

    ##    removeStopWords
    ##    Input:     String (FR)
    ##    Output:    List of [keywords,score]
    ##    note: can also output list of keyw only
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def addScoreToKeywords(self,keyw):
        # Array of keywords and their "score"
        kws = []
        cpt = 0
        # For each keyword
        for x in keyw:
            score = 1
            # If postag option, get the score
            if self.postag:
                score = self.getPostagScore(x)
                # if brute option, ignore all default words
                if self.brute:
                    if score != 1:
                        kws.append([x,score])
                else:
                    kws.append([x,score])
            else:
                kws.append([x,score])

        #print kws
        return kws

    ##    getPostagScore
    ##    Input:     word
    ##    Output:    Score depending on tag
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getPostagScore(self,w):
        shell = 1
        if shell:
            # Call TreeTagger
            proc = subprocess.Popen(["echo '"+w+"' | tree-tagger -lemma -quiet "+self.treetagger+"lib/french-utf8.par |cut -d ' ' -f 1", ""], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()

            # Category
            s=out
            #print s

            # Try and find a category
            m = re.findall("ADJ|NOM|VER",s)
            # Depending on it, score
            if len(m) != 0:
                m = re.findall("NOM",s)
                if len(m) != 0:
                    return self.noun

                m = re.findall("ADJ",s)
                if len(m) != 0:
                    return self.adj

                m = re.findall("VER",s)
                if len(m) != 0:
                    return self.verb
        else:
            print "Nope"

        return 1
