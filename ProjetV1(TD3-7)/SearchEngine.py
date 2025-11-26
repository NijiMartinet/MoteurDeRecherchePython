from Corpus import Corpus
from numpy import array
from numpy import zeros
import re
from scipy.sparse import csr_matrix

class SearchEngine:

    #Fonction pour construire le vocabulaire du dictionnaire
    def defVocab(self):
        i=0
        for doc in self.corpus.id2doc.values():
            texte = doc.get_texte()
            texte = texte.lower()
            texte = re.sub(r'[^a-z0-9]', ' ', texte)

            vocabulaire = texte.split()
            vocab = dict()
            nvdoucument=[]
            for mot in vocabulaire:
                if mot not in self.vocab:
                    vocab[mot]={'identifiant':i,'frequenceCorpus':1,'frequenceDocument':1}
                    i+=1
                    print(mot)
                else:
                    vocab[mot]['frequenceCorpus']+=1
                if mot not in nvdoucument:
                    nvdoucument.append(mot)
                    vocab[mot]['frequenceDocument']+=1
        return vocab

    #Fonction pour inversé le dictionnaire vocab
    def defInvvocab(self):
        invvocab=dict()
        for mot in self.vocab:
            invvocab[self.vocab[mot]['identifiant']]=mot
        return invvocab
    
    #Fonction pour définir la matrice mat_TF
    def defMat_TF(self):
        ni = self.corpus.ndoc
        nj = len(self.invvocab)
        mat_TF = zeros((ni,nj))
        for i in range(ni):
            for j in range(nj):
                p = re.compile(self.invvocab[j])
                textefound = list(p.finditer(self.corpus.id2doc.get(i).get_texte()))
                mat_TF[i][j]=len(textefound)
        mat_TF = csr_matrix(mat_TF, dtype=int).toarray()
        return mat_TF
    
    def defMat_TFxIDF(self):
        ndoc = self.corpus.ndoc
        nvoc = len(self.invvocab)
        for v in range(nvoc):
            for d in range(ndoc):
                print(v,d)


    def __init__(self, corpus):
        self.corpus=corpus
        self.vocab=self.defVocab()
        self.invvocab= self.defInvvocab()
        self.mat_TF=array([])
 
    def info(self):
        print("Taille de vocab :", len(self.vocab))
        print("Taille de invvocab :", len(self.invvocab))
        print("Nombre de documents :",self.corpus.ndoc)
        print("Taille de mat_TF :", self.mat_TF.size)
