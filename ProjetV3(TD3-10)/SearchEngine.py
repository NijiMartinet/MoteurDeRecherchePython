from Corpus import Corpus
from Corpus import vocabulaire_texte
from numpy import array
from numpy import zeros
from numpy import dot
from numpy import empty
from numpy.linalg import norm
from math import log
import re
import pandas as pd
from tqdm import tqdm
from scipy.sparse import csr_matrix
from collections import Counter



class SearchEngine:

    # Fonction pour construire la variable vocab
    def defVocab(self):
        print("Construction du vocabulaire")
        with tqdm(total=self.corpus.ndoc) as bar:
            i=0 # L'identifiant unique
            vocab = dict() # Initialisation d'un dictionnaire
            for doc in self.corpus.id2doc.values(): # Pour chaque document
                mots = vocabulaire_texte(doc.get_texte())          
            
                # Cette variable nous permettra de récupérer les mots qui sont dans ce dictionnaire
                nvdoucument=[]

                # Pour chaque mot
                for mot in mots:
                    # S'il n'est pas dans le vocabulaire
                    if mot not in vocab:
                        # On le rajoute avec la fréquence dans le corpus à 1 et la frequence document qui compte le nombre de documents qui contienne ce mot
                        vocab[mot]={'identifiant':i,'frequenceCorpus':1,'frequenceDocument':1}
                        # On augmente l'identifiant
                        i+=1
                    else:
                        # Sinon on ajoute 1 à la frequence corpus 
                        vocab[mot]['frequenceCorpus']+=1
                    # S'il n'est pas dans le tableau -> c'est la première fois qu'on voit ce mot dans ce document
                    if mot not in nvdoucument:
                        # On le rajoute dans le tableau
                        nvdoucument.append(mot)
                        # On augmente sa fréquence document
                        vocab[mot]['frequenceDocument']+=1
                bar.update(1)
        return vocab

    def defMat_TF(self):
        mat_TF = zeros((self.corpus.ndoc, len(self.vocab)), dtype=int)
        with tqdm(total=self.corpus.ndoc) as bar:
            for d, doc in self.corpus.id2doc.items():
                # Tokenisation du texte
                tokens = vocabulaire_texte(doc.get_texte())  # renvoie déjà une liste de mots
                counts = Counter(tokens)  # compte toutes les occurrences en une seule fois

                # Remplissage de la ligne correspondante au document
                for word, data in self.vocab.items():
                    idx = data["identifiant"]     # index colonne dans la matrice
                    mat_TF[d][idx] = counts.get(word, 0)
                bar.update(1)

        return csr_matrix(mat_TF, dtype=int).toarray()
    
    # Fonction pour définir la matrice mat_TFxIDF
    def defMat_TFxIDF(self):
        with tqdm(total=self.corpus.ndoc) as bar:
            # On la met au bonne dimension
            mat_TFxIDF = empty((self.corpus.ndoc,len(self.vocab)))
            # Pour chaque document d
            for d in self.corpus.id2doc:
                # On récupère le nombre de mot dans le document
                nb_mot_doc = len(vocabulaire_texte(self.corpus.id2doc.get(d).get_texte()))
                # Pour chaque mot du vocabulaire v
                for v in self.vocab:
                    # On récupère son identifiant
                    i = self.vocab[v]['identifiant']
                    # On calcule tf = nb d'occurence du mot dans le doc / nb_mot_doc
                    tf=self.mat_TF[d][i] / nb_mot_doc
                    # On calcule idf = log(nombre de document / nombre de document où il y a le mot)
                    idf = log(self.corpus.ndoc / self.vocab[v]['frequenceDocument'])
                    # On ajoute la valeure à la bonne case de la matrice 
                    mat_TFxIDF[d][i]= tf * idf    
                bar.update(1)    
        # On retourne la matrice
        return mat_TFxIDF

    # Initialisation de la classe qui va utiliser les fonctions précédentes pour définir certain termes
    def __init__(self, corpus):
        self.corpus=corpus
        self.vocab=self.defVocab()
        print("Construction de la matrice TF:")
        self.mat_TF=self.defMat_TF()
        print("Construction de la matrice TFxIDF:")
        self.mat_TFxIDF = self.defMat_TFxIDF()

    def search(self, texte, n):
        # On crée un vecteur de la bonne dimention remplis de 0
        vector = array(zeros((len(self.vocab))))
        # On récupère tout les mot du texte et on fait les traitement dessus
        mots = vocabulaire_texte(texte)

        for v in self.vocab:
            if v in mots:
                # On met à 1 là où on retrouve un mot présent dans le vocabulaire et dans le texte
                vector[self.vocab[v]['identifiant']]=1
        
        # On crée un tableau qui comportera la mesure de distance et l'id du docuement
        tab_doc = []
        # Pour chaque document
        for d in self.corpus.id2doc:
            # On récupère son vecteur TFxIDF
            vector_doc = array(self.mat_TFxIDF[d])
            # On calcule le cosinus
            cos = dot(vector,vector_doc) / (norm(vector) * norm(vector_doc))
            #On ajoute au tableau les informations
            tab_doc.append((cos,d))

        # On trie le tableau en fonction de la mesure de distance dans l'ordre croissant
        tab_doc = sorted(tab_doc, key=lambda x: x[0])
        # On fait notre tableau de résultats
        res = []
        # Pour facilité, on récupère le dictionnaire des documents
        docs = self.corpus.id2doc
        # On boucle de 1 à n avec n le nombre de document qu'on veux (vu qu'on veux aller à n on met n+1)
        for i in range(1,n+1):
            # On ajoute au résultats le document avec son id, son titre et son texte
            res.append({"id":tab_doc[-i][1], 
                        "titre": docs.get(tab_doc[-i][1]).get_titre(),
                        "texte": docs.get(tab_doc[-i][1]).get_texte()}
                      )
            # On utilise -i car les mesures de distance sont ranger dans l'ordre croissant donc celle qui nous interressent sont à la fin
        return pd.DataFrame(res)
            

    def info(self):
        print("Taille de vocab :", len(self.vocab))
        print("Nombre de documents :",self.corpus.ndoc)
        print("Taille de mat_TF :", self.mat_TF.size)

    def __str__(self):
        return "Corpus de "+str(self.corpus.ndoc)+" documents avec "+str(len(self.vocab))+" mot de vocabulaire différents"