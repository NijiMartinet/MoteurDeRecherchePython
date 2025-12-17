import re
import pandas as pd
from Document import DocumentGenerator
from Author import Author

# Singleton afin de permettre la création d'un seul corpus
def singleton(cls) :
    instances = [None]
    def wrapper(*args, **kwargs) :
        if instances[0] is None :
            instances[0] = cls(*args, **kwargs)
        return instances[0]
    return wrapper

@singleton
# Création de la class Corpus
class Corpus :
    # Constructeur de la class
    def __init__(self, nom) :
        self.nom = nom  # Nom du corpus
        self.id2aut = {}  # Dictionnaire des auteurs
        self.id2doc = {}  # Dictionnaire de document
        self.ndoc = 0  # Nombre de documents dans le corpus
        self.naut = 0  # Nombre d'auteurs dans le corpus
        self.iddocument = 0  # Identifiant des documents géré automatiquement
        self.texte = ""  # Texte de tout le corpus 
        self.vocabulaire = dict()  # Vocabulaire du corpus

    # Fonction augmente_id_document() qui permet d'augmenter l'identifiant des documents
    def augmente_id_document(self) :
        self.iddocument += 1

    def tri_document_titre(self) :
        # On trie le dictionnaire des documents par titre
        self.id2doc = dict(
            sorted(self.id2doc.items(), key = lambda item : item[1].get_titre())
        )

    def tri_document_date(self) :
        # On trie le dictionnaire des documents par date
        self.id2doc = dict(
            sorted(self.id2doc.items(), key = lambda item : item[1].get_date())
        )

    # Fonction add_document() qui permet d'ajouter un document au corpus
    def add_document(self, document) :
        self.id2doc[self.iddocument] = (
            document  # On ajoute le document au dictionnaire des documents avec comme id l'id généré
        )
        self.ndoc += 1  # On augmente le nombre de documents dans le corpus

        # On récupère l'auteur du document
        auteur = document.get_auteur()
        # Si l'auteur n'existe pas on le crée
        if auteur not in self.id2aut :
            self.id2aut[auteur] = Author(auteur)
            self.naut += 1
        # On ajoute le document à l'auteur
        self.id2aut[auteur].add(self.iddocument, document)

        # Si c'est un document Arxiv on gère les coauteurs
        # Premièrement on vérifie que le document est bien de type Arxiv
        if document.get_type() == "Arxiv" :
            # On récupère les coauteurs
            coauteurs = document.get_coauteur()
            # Si cette variable est différente de "Aucun", alors on récupère les coauteurs
            if coauteurs != "Aucun" :
                coauteurs = coauteurs.split(" et ")  # On crée une liste des coauteurs
                for co in coauteurs :
                    # On fait le même traitement que sur auteur -> s'il n'existe pas dans le corpus on le crée
                    if co not in self.id2aut :
                        self.id2aut[co] = Author(co)
                        self.naut += 1
                    # Puis on lui ajoute le document
                    self.id2aut[co].add(self.iddocument, document)
        self.augmente_id_document()  # On augmente l'identifiant du document

    # Fonction str() pour afficher les informations du corpus via print(corpus)
    def __str__(self) :
        return f"Nombre de documents :{self.ndoc}\nNombre d'auteur :{self.naut}"

    # Fonction rem_document() qui permet de retirer un document du corpus
    def rem_document(self, doc_id) :
        auteur = self.id2doc[doc_id].get_auteur()  # On récupère l'auteur du document

        # On enlève le document à l'auteur
        self.id2aut[auteur].production.pop(doc_id)
        self.id2aut[auteur].ndoc -= 1

        # Si l'auteur n'a plus de document on le retire du corpus
        if self.id2aut[auteur].ndoc == 0 :
            self.id2aut.pop(auteur)
            self.naut -= 1

        # Si c'est un document Arxiv on gère les coauteurs
        if self.id2doc[doc_id].get_type() == "Arxiv" :
            coauteurs = self.id2doc[doc_id].get_coauteur()
            if coauteurs != "Aucun" :
                coauteurs = coauteurs.split(" et ")
                for co in coauteurs :
                    self.id2aut[co].production.pop(doc_id)
                    self.id2aut[co].ndoc -= 1
                    if self.id2aut[co].ndoc == 0 :
                        self.id2aut.pop(co)
                        self.naut -= 1

        # On enlève le document du corpus
        self.id2doc.pop(doc_id)
        self.ndoc -= 1

    # Fonction to_dataframe() qui permet de convertir le corpus en DataFrame
    def to_dataframe(self) :
        data = []  # Création d'une liste vide pour stocker les données
        self.iddocument = 0 # On va remmetrre les identifiants dans l'ordre
        # On boucle sur chaque document du corpus (en récupérant son id et son objet document)
        for doc in self.id2doc.values() :
            # Si le document est de type Reddit on ajoute les informations spécifiques
            if doc.get_type() == "Reddit" :
                data.append(
                    {
                        "id" : self.iddocument,
                        "type" : doc.get_type(),
                        "titre" : doc.get_titre(),
                        "auteur" : doc.get_auteur(),
                        "date" : doc.get_date(),
                        "url" : doc.get_url(),
                        "texte" : doc.get_texte(),
                        "autre" : doc.get_nbcom(),
                    }
                )
            # Si le document est de type Arxiv on ajoute les informations spécifiques
            # On a choisi de mettre un "elif" si nous avons de nouveaux types de documents à ajouter dans le futur
            elif doc.get_type() == "Arxiv" :
                data.append(
                    {
                        "id" : self.iddocument,
                        "type" : doc.get_type(),
                        "titre" : doc.get_titre(),
                        "auteur" : doc.get_auteur(),
                        "date" : doc.get_date(),
                        "url" : doc.get_url(),
                        "texte" : doc.get_texte(),
                        "autre" : doc.get_coauteur(),
                    }
                )
            self.augmente_id_document()
        return pd.DataFrame(data)

    # Focntion save() qui permet de sauvegarder le corpus dans un fichier CSV
    def save(self, filename) :
        df = self.to_dataframe()  # On récupère le DataFrame du corpus et met les bons identifiants
        # On l'enregistre en format CSV avec comme séparateur une tabulation
        df.to_csv(f"{filename}.csv", index = False, sep = "\t")  
        print(f"Corpus sauvgardé dans {filename}.csv")


    # Fonction load() qui permet de charger un corpus à partir d'un fichier CSV
    def load(self, filename) :
        # On lit le fichier CSV
        df = pd.read_csv(f"{filename}.csv", sep = "\t")
        if 'type' in df.columns : #On connais le type du documents
            for i in range(len(df)) :
                self.add_document(DocumentGenerator.factory(type = df["type"][i],titre = df["titre"][i],auteur = df["auteur"][i],date = df["date"][i],url = df["url"][i],texte = df["texte"][i],autre = df["autre"][i]))
        else : #On ne connais pas le type -> c'est un discours
            for i in range(len(df)) :
                self.add_document(DocumentGenerator.factory(type = "Discours",auteur = df["speaker"][i],texte = df["text"][i],date = df["date"][i],titre = df["descr"][i],url = df["link"][i])) 

    def creation_texte_vocab(self) :
        for doc in self.id2doc.values() :
            self.texte+= doc.get_texte()+" "
            # Pensez à split avec la ponctuation, les chiffres, etc ...
            vocabulaire = vocabulaire_texte(doc.get_texte())
            for mot in vocabulaire :
                if mot not in self.vocabulaire :
                    self.vocabulaire[mot] = 1
                else :
                    self.vocabulaire[mot]+= 1

    def search(self, keyword) :
        # Si le texte n'a pas été créer, on le crée.
        if self.texte == "" :
            self.creation_texte_vocab()
        
        p = re.compile(keyword)
        textefound = p.finditer(self.texte)
        df = []
        for t in textefound :
            contexte_gauche = "..."+self.texte[t.start()-30 :t.start()]
            contexte_droit = self.texte[t.end() :t.end()+30]+"..."
            mot = self.texte[t.start() :t.end()]
            df.append({'contexte gauche' :contexte_gauche,'mot' :mot,'contexte droit' :contexte_droit})
        return df

    def concorde(self, keyword) :
        df = pd.DataFrame(self.search(keyword))
        print(df)

    def clear(self) :
        self.id2aut = {}  # Dictionnaire des auteurs
        self.id2doc = {}  # Dictionnaire de document
        self.ndoc = 0  # Nombre de documents dans le corpus
        self.naut = 0  # Nombre d'auteurs dans le corpus
        self.iddocument = 0  # Identifiant des documents géré automatiquement
        self.texte = ""  # Texte de tout le corpus 
        self.vocabulaire = dict()  # Vocabulaire du corpus




        





        

