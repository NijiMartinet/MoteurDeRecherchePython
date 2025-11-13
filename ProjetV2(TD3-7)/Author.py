class Author:
    #La définition de la class commence tjs par un constructeur
    def __init__(self, name):
        self.name=name
        self.ndoc=0
        self.production={} #aura des obj de class Document

    def add(self, doc_id, document):
        self.production[doc_id]=document
        self.ndoc += 1

    def __str__(self):
        return f"Auteur: {self.name} - {self.ndoc} document(s)"

    def __repr__(self):
        return f"Auteur(name={self.name}, ndoc={self.ndoc})"
    
    def get_taille_moyenne_documents(self):
        if self.ndoc==0:
            return 0
        total_cara = sum(len(doc.texte) for doc in self.production.values())
        return total_cara/self.ndoc
    
    def get_nombre_documents(self):
        return self.ndoc