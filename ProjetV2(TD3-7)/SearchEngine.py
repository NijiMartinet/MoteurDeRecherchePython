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
from scipy.sparse import csr_matrix

class SearchEngine:

    #Fonction pour construire la variable vocab
    def defVocab(self):
        i=0 #L'identifiant unique
        vocab = dict() #Initialisation d'un dictionnaire
        for doc in self.corpus.id2doc.values(): #Pour chaque document
            mots = vocabulaire_texte(doc.get_texte())          
            
            #Cette variable nous permettra de récupérer les mots qui sont dans ce dictionnaire
            nvdoucument=[]

            #Pour chaque mot
            for mot in mots:
                #S'il n'est pas dans le vocabulaire
                if mot not in vocab:
                    #On le rajoute avec la fréquence dans le corpus à 1 et la frequence document qui compte le nombre de documents qui contienne ce mot
                    vocab[mot]={'identifiant':i,'frequenceCorpus':1,'frequenceDocument':1}
                    #On augmente l'identifiant
                    i+=1
                else:
                    #Sinon on ajoute 1 à la frequence corpus 
                    vocab[mot]['frequenceCorpus']+=1
                #S'il n'est pas dans le tableau -> c'est la première fois qu'on voit ce mot dans ce document
                if mot not in nvdoucument:
                    #On le rajoute dans le tableau
                    nvdoucument.append(mot)
                    #On augmente sa fréquence document
                    vocab[mot]['frequenceDocument']+=1
        return vocab
    
    #Fonction pour définir la matrice mat_TF
    def defMat_TF(self):
        #On initialise la matrice mat_TF au bonne dimension -> [nb document,nb mot]
        mat_TF = empty((self.corpus.ndoc,len(self.vocab)))
        #Pour chaque document
        for d in self.corpus.id2doc:
            #Pour chaque mot dans le vocabulaire
            for v in self.vocab:
                #i est l'identifiant du mot (une valeur numérique pour le retrouver dans la matrice)
                i = self.vocab[v]['identifiant']
                texte = ' '.join(vocabulaire_texte(self.corpus.id2doc.get(d).get_texte()))

                #On regarde le nombre de fois qu'on trouve le mot v dans le doc d
                p = re.compile(v)
                textefound = list(p.finditer(texte))
                #On met le nombre d'occurence dans la bonne case de la matrice
                mat_TF[d][i]=len(textefound)
        #On utilise csr_matrix pour notre matrice car c'est une matrice creuse
        mat_TF = csr_matrix(mat_TF, dtype=int).toarray()
        #On retourne la matrice
        return mat_TF
    
    #Fonction pour définir la matrice mat_TFxIDF
    def defMat_TFxIDF(self):
        #On la met au bonne dimension
        mat_TFxIDF = empty((self.corpus.ndoc,len(self.vocab)))
        #Pour chaque document d
        for d in self.corpus.id2doc:
            #On récupère le nombre de mot dans le document
            nb_mot_doc = len(vocabulaire_texte(self.corpus.id2doc.get(d).get_texte()))
            #Pour chaque mot du vocabulaire v
            for v in self.vocab:
                #On récupère son identifiant
                i = self.vocab[v]['identifiant']

                #On calcule tf = nb d'occurence du mot dans le doc / nb_mot_doc
                tf=self.mat_TF[d][i] / nb_mot_doc
                #On calcule idf = log(nombre de document / nombre de document où il y a le mot)
                idf = log(self.corpus.ndoc / self.vocab[v]['frequenceDocument'])
                #On ajoute la valeure à la bonne case de la matrice 
                mat_TFxIDF[d][i]= tf * idf        
        #On retourne la matrice
        return mat_TFxIDF


    #Initialisation de la classe qui va utiliser les fonctions précédentes pour définir certain termes
    def __init__(self, corpus):
        self.corpus=corpus
        self.vocab=self.defVocab()
        self.mat_TF=self.defMat_TF()
        self.mat_TFxIDF = self.defMat_TFxIDF()

    #--------------------ICI----------------------------

    def search(self, texte, n):
        #On crée un vecteur de la bonne dimention
        vector = array(zeros((len(self.vocab))))
        #On récupère tout les mot du texte et on fait des traitement dessus
        texte = texte.lower()
        texte = re.sub(r'[^a-z]', ' ', texte)
        mots = texte.split()

        for v in self.vocab:
            if v in mots:
                #On met à 1 là où on retrouve les mots
                vector[self.vocab[v]['identifiant']]=1
        
        #On crée un tableau qui comportera la mesure de distance et l'id du docuement
        tab_doc = []
        #Pour chaque document
        for d in self.corpus.id2doc:
            #On récupère son vecteur
            vector_doc = array(self.mat_TFxIDF[d])
            cos = dot(vector,vector_doc) / (norm(vector) * norm(vector_doc))
            tab_doc.append((cos,d))

        #On trie le tableau en fonction de la mesure de distance dans l'ordre croissant
        tab_doc = sorted(tab_doc, key=lambda x: x[0])
        #On fait notre tableau de résultats
        res = []
        doc = self.corpus.id2doc
        #On boucle de 1 à n avec n le nombre de document qu'on veux
        for i in range(1,n+1):
            #On ajoute au résultats le document avec son id, son titre et son texte
            res.append(
                {
                    "id":tab_doc[-i][1], #On utilise -i car les mesures de distance sont ranger dans l'ordre croissant donc celle qui nous interressent sont à la fin
                    "titre": doc.get(tab_doc[-i][1]).get_titre(),
                    "texte": doc.get(tab_doc[-i][1]).get_texte()
                }
            )
        return pd.DataFrame(res)
            

    def info(self):
        print("Taille de vocab :", len(self.vocab))
        print("Nombre de documents :",self.corpus.ndoc)
        print("Taille de mat_TF :", self.mat_TF.size)

    def __str__(self):
        return "Corpus de "+str(self.corpus.ndoc)+" documents avec "+str(len(self.vocab))+" mot de vocabulaire différents"
