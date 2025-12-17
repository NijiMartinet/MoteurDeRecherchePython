# Création de la class des auteurs
class Author :
    # Constructeur de la class
    def __init__(self, name) :
        self.name = name  # Nom de l'auteur
        self.ndoc = 0  # Nombre de documents produits par l'auteur
        self.production = {}  # Dictionnaire des documents produits par l'auteur

    # Fonction add() qui permet d'ajouter un document à la production de l'auteur
    def add(self, doc_id, document) :
        self.production[doc_id] = document
        self.ndoc += 1

    # Fonction str() pour afficher les informations de l'auteur via print(auteur)
    def __str__(self) :
        return f"Auteur : {self.name} - {self.ndoc} document(s)"

    # Fonction repr() pour faire une chaîne de caractères qui sert de représentation à la class
    def __repr__(self) :
        return f"Auteur(name = {self.name}, ndoc = {self.ndoc})"

    # Fonction get_taille_moyenne_documents() qui retourne la taille moyenne (nombre de caractère moyen) des documents produits par l'auteur
    def get_taille_moyenne_documents(self) :
        if self.ndoc == 0 :
            return 0
        total_cara = sum(len(doc.texte) for doc in self.production.values())
        return total_cara / self.ndoc

    # Fonction get_nombre_documents() qui retourne le nombre de documents produits par l'auteur
    def get_nombre_documents(self) :
        return self.ndoc
