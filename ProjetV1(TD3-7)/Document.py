# Le nom d'une class commence toujours par une majuscule
from datetime import datetime

class Document:
    # On commence toujours pas self les fct d'une class en python qui fait directement référence à l'objet qu'on est entrain de créer
    def __init__(self, type, titre, auteur, date, url, texte):  # Constructeur d'une class en Python
        self.type = type
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte

    # Méthode appelé via un print(Document)
    def __str__(self):
        return f"Document :{self.titre}"

    def afficher_infos(self):
        print(f"Type : {self.type}")
        print(f"Titre : {self.titre}")
        print(f"Auteur : {self.auteur}")
        print(f"Date : {self.date}")
        print(f"URL : {self.url}")
        print(f"Texte : {self.texte[:100]}...")  # Permet d'afficher uniquement les 100 premiers caractères

    # Getters et Setters
    def get_titre(self):
        return self.titre

    def set_titre(self, titre):
        self.titre = titre

    def get_auteur(self):
        return self.auteur

    def set_auteur(self, auteur):
        self.auteur = auteur

    def get_date(self):
        return self.date

    def set_date(self, date):
        self.date = date

    def get_url(self):
        return self.url

    def set_url(self, url):
        self.url = url

    def get_texte(self):
        return self.texte

    def set_texte(self, texte):
        self.texte = texte


class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nbcom):
        super().__init__("Reddit", titre, auteur, date, url, texte)
        self.nbcom = nbcom

    def get_nbcom(self):
        return self.nbcom

    def set_nbcom(self, nbcom):
        self.nbcom = nbcom

    def __str__(self):
        return f"Document Reddit :{self.titre}\nNombre de commentaire :{self.nbcom}"

    def get_type(self):
        return self.type


class ArxivDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, coauteur):
        super().__init__("Arxiv", titre, auteur, date, url, texte)
        self.coauteur = coauteur

    def get_coauteur(self):
        return self.coauteur

    def set_coauteur(self, coauteur):
        self.coauteur = coauteur

    def __str__(self):
        return f"Document Arxiv :{self.titre}\nNombre de co-auteur :{self.coauteur.len}"

    def get_type(self):
        return self.type


class DocumentGenerator:
    # Renvoie une instance de la classe Document en fonction du type
    @staticmethod
    def factory(type, titre, auteur, date, url, texte, autre):
        if type == "Reddit":
            return RedditDocument(titre, auteur, date, url, texte, autre)
        if type == "Arxiv":
            return ArxivDocument(titre, auteur, date, url, texte, autre)
