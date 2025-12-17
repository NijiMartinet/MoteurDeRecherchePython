import re
import string
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from numpy import dot
from numpy.linalg import norm

nltk.download('stopwords')
nltk.download('punkt_tab', quiet = True)


# Singleton afin de permettre la création d'un seul corpus
def singleton(cls) :
    instances = [None]
    def wrapper(*args, **kwargs) :
        if instances[0] is None :
            instances[0] = cls(*args, **kwargs)
        return instances[0]
    return wrapper

# Utilisation de mon cours d'ingénieurie des données
# On va tokenizer le texte
# Puis on enlève les signes de ponctuation
# Puis on enlève les stopwords
# Puis on enlève les mots trop court
# Puis on racinize pour garder la racine des mots
def clean_texte(texte) :
    # On split le texte
    vocab = nltk.word_tokenize(texte.lower()) 
    # On enlève tout les signes de ponctuation
    re_punc = re.compile('[%s]' % re.escape(string.punctuation))
    vocab = [re_punc.sub('', w) for w in vocab]
    # On filtre les stopwords (mot qui ne porte pas du sens)
    stop_words = set(stopwords.words('english'))
    vocab = [w for w in vocab if not w in stop_words]
    # On enlève les mots d'une lettre
    vocab = [word for word in vocab if len(word) > 1]
    # apply stemming using snowball
    vocab_stemmed = [SnowballStemmer('english').stem(word) for word in vocab]
    clean_text = " ".join(vocab_stemmed)
    return clean_text

def clean_texte2(texte) :
    # On split le texte
    vocab = nltk.word_tokenize(texte.lower()) 
    # On enlève tout les signes de ponctuation
    re_punc = re.compile('[%s]' % re.escape(string.punctuation))
    vocab = [re_punc.sub('', w) for w in vocab]
    # On filtre les stopwords (mot qui ne porte pas du sens)
    stop_words = set(stopwords.words('english'))
    vocab = [w for w in vocab if not w in stop_words]
    # On enlève les mots d'une lettre
    vocab = [word for word in vocab if len(word) > 1]
    # apply stemming using snowball
    vocab_stemmed = [SnowballStemmer('english').stem(word) for word in vocab]
    return vocab_stemmed

@singleton
class SearchEngine :

    def defTexte(self) :
        texte = []
        for doc in self.corpus.id2doc.values() :
            texte.append(clean_texte(doc.get_texte()))
        return texte

    def defVectorize(self) :
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer()
        vectorizer.fit(self.texte)
        return vectorizer

    # Fonction pour construire la variable vocab
    def defVocab(self) :
        return list(self.vectorizer.vocabulary_.keys())
    
    # Fonction pour définir la matrice mat_TFxIDF
    def defMat_TFxIDF(self) :
        return self.vectorizer.transform(self.texte)

    # Initialisation de la classe qui va utiliser les fonctions précédentes pour définir certain termes
    def __init__(self, corpus) :
        self.corpus = corpus
        self.texte = self.defTexte()
        self.vectorizer = self.defVectorize()
        self.vocab = self.defVocab()
        self.mat_TFxIDF = self.defMat_TFxIDF()

    def search(self, texte, n) :
        #On calcule le vecteur du texte
        vector = self.vectorizer.transform(clean_texte2(texte))
        #On force sa shape en (n,)
        vector = vector.toarray()
        vector = vector[0]
        # On crée un tableau qui comportera la mesure de distance et l'id du docuement
        tab_doc = []

        # Pour facilité, on récupère le dictionnaire des documents
        docs = self.corpus.id2doc

        # Pour chaque document
        for d in docs :
            # On récupère son vecteur TFxIDF
            vector_doc = self.mat_TFxIDF[d]
            vector_doc = vector_doc.toarray()
            vector_doc = vector_doc[0]
            # On calcule le cosinus
            cos = dot(vector,vector_doc) / (norm(vector) * norm(vector_doc))
            #On ajoute au tableau les informations
            tab_doc.append((cos,d))

        # On trie le tableau en fonction de la mesure de distance dans l'ordre croissant
        tab_doc = sorted(tab_doc, key = lambda x : x[0])
        # On fait notre tableau de résultats
        res = []
        
        # On boucle de 1 à n avec n le nombre de document qu'on veux (vu qu'on veux aller à n on met n+1)
        for i in range(1,n+1) :
            # On ajoute au résultats le document avec son id, son titre et son texte
            res.append({"id" :tab_doc[-i][1], 
                        "titre" : docs.get(tab_doc[-i][1]).get_titre(),
                        "texte" : docs.get(tab_doc[-i][1]).get_texte()}
                      )
            # On utilise -i car les mesures de distance sont ranger dans l'ordre croissant donc celle qui nous interressent sont à la fin
        return pd.DataFrame(res)
            
    def info(self) :
        print("Taille de vocab :", len(self.vocab))
        print("Nombre de documents :",self.corpus.ndoc)
        print("Taille de mat_TF :", self.mat_TF.size)

    def __str__(self) :
        return "Corpus de "+str(self.corpus.ndoc)+" documents avec "+str(len(self.vocab))+" mot de vocabulaire différents"