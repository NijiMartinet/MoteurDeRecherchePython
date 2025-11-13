import pandas as pd
from Document import Document, RedditDocument, ArxivDocument
from Author import Author

def singleton(cls):
    instances = [None]
    def wrapper(*args, **kwargs):
        if instances[0] is None:
            instances[0] = cls(*args, **kwargs)
        return instances[0]
    return wrapper

@singleton
class Corpus :
    def __init__(self,nom) :
        self.nom = nom
        self.id2aut = {} #Dictionnaire des auteurs
        self.id2doc = {} #Dictionnaire de document
        self.ndoc = 0
        self.naut = 0
        self.iddocument = 0

    def augmente_id_document(self):
        self.iddocument+=1

    def add_document(self, document):
        self.augmente_id_document()
        self.id2doc[self.iddocument] = document
        self.ndoc+=1
        
        auteur = document.get_auteur()
        #Si l'auteur n'existe pas on le crée
        if auteur not in self.id2aut:
            self.id2aut[auteur]=Author(auteur)
            self.naut+=1

        #On ajoute le document à l'auteur
        self.id2aut[auteur].add(self.iddocument,document)

    def __str__(self):
        stri = f"Nombre de documents :"+str(self.ndoc)+f"\nNombre d'auteur :"+ str(self.naut)
        return stri

    def rem_document(self, doc_id):
        auteur = self.id2doc[doc_id].auteur

        #On enlève le document à l'auteur
        self.id2aut[auteur].production.pop(doc_id)
        self.id2aut[auteur].ndoc-=1
        if self.id2aut[auteur].ndoc == 0:
            self.id2aut.pop(auteur)
            self.naut-=1
        self.id2doc.pop(doc_id)
        self.ndoc-=1

    def to_dataframe(self):
        data=[]
        for doc_id, doc in self.id2doc.items():
            if doc.get_type() == "Reddit":
                data.append({
                    'id':doc_id,
                    'type':doc.get_type(),
                    'titre':doc.get_titre(),
                    'auteur':doc.get_auteur(),
                    'date':doc.get_date(),
                    'url':doc.get_url(),
                    'texte':doc.get_texte(),
                    'autre':doc.get_nbcom(),
                    'taille_texte':len(doc.get_texte())
                })
            else:
                data.append({
                    'id':doc_id,
                    'type':doc.get_type(),
                    'titre':doc.get_titre(),
                    'auteur':doc.get_auteur(),
                    'date':doc.get_date(),
                    'url':doc.get_url(),
                    'texte':doc.get_texte(),
                    'autre':doc.get_coauteur(),
                    'taille_texte':len(doc.get_texte())
                })
        return pd.DataFrame(data)
      
    def save(self, filename):
        df=self.to_dataframe()
        df.to_csv(f"{filename}.csv",index=False,sep="\t")
        print(f"Corpus sauvgardé dans {filename}.csv")

    def load(self, filename):
        df=pd.read_csv(f"{filename}.csv",sep="\t")
        for i in range(len(df)):
            if df["type"][i]=="Reddit":
                self.add_documentReddit(df["titre"][i],df["auteur"][i],df["date"][i],df["url"][i],df["texte"][i],df["autre"][i])
            else:
                self.add_documentArxiv(df["titre"][i],df["auteur"][i],df["date"][i],df["url"][i],df["texte"][i],df["autre"][i])