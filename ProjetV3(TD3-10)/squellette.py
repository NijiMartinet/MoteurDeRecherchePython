import praw
import urllib
import xmltodict
import pandas as pd
import os
from Corpus import Corpus
from Document import DocumentGenerator
from SearchEngine import SearchEngine

docs = Corpus("discours_US")

if os.path.exists("discours_US.csv"):
    docs.load("discours_US")
else:
    # Se connecter sur Reddit
    reddit = praw.Reddit(
        client_id="chp-OSvcT2YNGYMdLRLTdw",
        client_secret="JDBMQbv6014x63VLUFbUb4dDX0-mTQ",
        user_agent="Blbl",
    )

    # On va charger le CORPS de chaque subreddit en lien avec le machinLearning (en vrai que 10 c'est bien)
    hot_posts = reddit.subreddit("all").hot(limit=100)
    for post in hot_posts:
        texte = post.selftext.replace("\\n", " ")
        titre = post.title
        # Transforme la date en format date
        date = pd.to_datetime(post.created, unit="s").date()
        url = post.url
        auteur = post.author
        nbcomment = post.num_comments
        # Insert le document au corpus
        docs.add_document(DocumentGenerator.factory("Reddit", titre, auteur, date, url, texte, nbcomment))

    url = "http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=20"
    requete = urllib.request.urlopen(url)
    parsed = xmltodict.parse(requete.read().decode("utf-8"))
    for j in range(0, len(parsed["feed"]["entry"])):
        texte = parsed["feed"]["entry"][j]["summary"].replace("\\n", " ")
        
        # Vu qu'il existe des co-auteur, on crée une variable avec la liste des auteurs
        auteur_list = parsed["feed"]["entry"][j]["author"]

        # Si on obtient une liste => Liste d'auteur avec plusieurs auteurs
        if type(auteur_list) == list:
            auteur = parsed["feed"]["entry"][j]["author"][0]["name"]
            coauteur = ""
            for i in range(1, len(auteur_list)):
                coauteur += parsed["feed"]["entry"][j]["author"][i]["name"] + " et "
            coauteur = coauteur[:-4]  # Enlever le dernier " et "
        # Sinon -> Un seul auteur
        else:
            auteur = parsed["feed"]["entry"][j]["author"]["name"]
            coauteur = "Aucun"
        
        titre = parsed["feed"]["entry"][j]["title"]
        # Transforme la date en format date
        date = pd.to_datetime(parsed["feed"]["entry"][j]["published"]).date()
        url = parsed["feed"]["entry"][j]["id"]
        # Insert le document au corpus
        docs.add_document(
            DocumentGenerator.factory("Arxiv", titre, auteur, date, url, texte, coauteur))

    # On repasse dans tout les documents
    # Etant données que nous allons supprimer des documents nous sommes obliger de passer par une copie de la liste des id
    for i in docs.id2doc.copy():
        # Si le texte n'est pas de type string on supprime le document
        if type(docs.id2doc[i].texte) is not str:
            docs.rem_document(i)
        else:
            nbcara = len(str(docs.id2doc[i].texte))
            # Si le document n'a pas assez de caractère on le supprime
            if nbcara < 20:
                docs.rem_document(i)

    # On enregiste le document crée
    docs.save("test")

#docs.concorde("electron")


print(docs)
print(docs.id2doc)


