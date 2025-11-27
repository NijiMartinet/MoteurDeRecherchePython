from Corpus import Corpus
from numpy import array
from numpy import zeros
from math import log
import re
from scipy.sparse import csr_matrix

class SearchEngine:

    #Fonction pour construire le vocabulaire du dictionnaire
    def defVocab(self):
        i=0
        vocab = dict()
        for doc in self.corpus.id2doc.values():
            texte = doc.get_texte()
            texte = texte.lower()
            texte = re.sub(r'[^a-z]', ' ', texte)

            vocabulaire = texte.split()
            nvdoucument=[]
            for mot in vocabulaire:
                if mot not in vocab:
                    vocab[mot]={'identifiant':i,'frequenceCorpus':1,'frequenceDocument':1}
                    i+=1
                else:
                    vocab[mot]['frequenceCorpus']+=1
                if mot not in nvdoucument:
                    nvdoucument.append(mot)
                    vocab[mot]['frequenceDocument']+=1
        #print("i:",i,"\nvocab:",len(vocab.keys()))
    
    #Fonction pour définir la matrice mat_TF
    def defMat_TF(self):
        mat_TF = zeros((self.corpus.ndoc,len(self.vocab)))
        for d in self.corpus.id2doc:
            for v in self.vocab:
                i = self.vocab[v]['identifiant']
                p = re.compile(v)
                textefound = list(p.finditer(self.corpus.id2doc.get(d).get_texte()))
                mat_TF[d][i]=len(textefound)
        mat_TF = csr_matrix(mat_TF, dtype=int).toarray()
        self.mat_TF = mat_TF
    
    def defMat_TFxIDF(self):
        mat_TFxIDF = zeros((self.corpus.ndoc,len(self.vocab)))
        for d in self.corpus.id2doc:
            nb_mot_doc = len(self.corpus.id2doc.get(d).get_texte().split())
            for v in self.vocab:
                i = self.vocab[v]['identifiant']
                tf=self.mat_TF[d][i] / nb_mot_doc
                idf = log(self.corpus.ndoc / self.vocab[v]['frequenceDocument'])
                mat_TFxIDF[d][i]= tf * idf
        mat_TFxIDF = csr_matrix(mat_TFxIDF, dtype=int).toarray()
        return mat_TFxIDF

    def __init__(self, corpus):
        self.corpus=corpus
        self.vocab=self.defVocab()
        self.mat_TF=self.defMat_TF()
        self.mat_TFxIDF = self.defMat_TFxIDF()

    def recherche(self, texte):
        vector = zeros((len(self.vocab)))
        print(vector,len(vector))
 
    def info(self):
        print("Taille de vocab :", len(self.vocab))
        print("Taille de invvocab :", len(self.invvocab))
        print("Nombre de documents :",self.corpus.ndoc)
        print("Taille de mat_TF :", self.mat_TF.size)
