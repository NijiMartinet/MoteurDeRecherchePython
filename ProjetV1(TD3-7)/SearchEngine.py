from Corpus import Corpus
from numpy import array

class SearchEngine:
    def __init__(self, corpus):
        self.corpus=corpus
        self.vocab=dict()
        self.mat_TF=array([])

    def blbl(self):
        for doc in self.corpus.id2doc.values():
            #Pensez à split avec la ponctuation, les chiffres, etc ...
            vocabulaire = doc.get_texte().split()
            i=0
            nvdoucument=[]
            for mot in vocabulaire:
                if mot not in self.vocab:
                    i+=1
                    self.vocab[mot]={'identifiant':i,'frequenceCorpus':1,'frequenceDocument':1}
                else:
                    self.vocab[mot]['frequenceCorpus']+=1
                if mot not in nvdoucument:
                    nvdoucument.append(mot)
                    self.vocab[mot]['frequenceDocument']+=1

    def blbl2(self):
        ni = self.corpus.ndoc
        nj = len(self.vocab)
        self.mat_TF = array((ni, nj))

                    


        