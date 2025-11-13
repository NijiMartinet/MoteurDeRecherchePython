import praw
import urllib
import xmltodict
import pandas as pd
import os
from Corpus import Corpus
from Document import Document, RedditDocument, ArxivDocument, DocumentGenerator

docs = Corpus("bl")

if os.path.exists("test.csv"):
    docs.load("test")
else :
    #Se connecter sur Reddit
    reddit = praw.Reddit(client_id='chp-OSvcT2YNGYMdLRLTdw', client_secret='JDBMQbv6014x63VLUFbUb4dDX0-mTQ', user_agent='Blbl')

    #On va charger le CORPS de chaque subreddit en lien avec le machinLearning (en vrai que 10 c'est bien)
    hot_posts  = reddit.subreddit('all').hot(limit=100)
    for post in hot_posts:        
        texte=post.selftext.replace("\n"," ")
        titre=post.title
        date=post.created
        url=post.url
        auteur=post.author
        nbcomment = post.num_comments
        docs.add_document(DocumentGenerator.factory("Reddit", titre, auteur, date, url, texte, nbcomment))
    
    url = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=2'
    requete = urllib.request.urlopen(url)
    parsed=xmltodict.parse(requete.read().decode('utf-8'))
    for j in range(0,len(parsed['feed']['entry'])):
        texte=parsed['feed']['entry'][j]['summary'].replace("\n"," ")
        auteur=parsed['feed']['entry'][j]['author'][0]['name']
        coauteur = ""
        for i in range(1,len(parsed['feed']['entry'][j]['author'])):
            coauteur+=parsed['feed']['entry'][j]['author'][i]['name'] + "//"
        titre=parsed['feed']['entry'][j]['title']
        date=parsed['feed']['entry'][j]['published']
        url=parsed['feed']['entry'][j]['id']
        docs.add_document(DocumentGenerator.factory("Arxiv", titre, auteur, date, url, texte, coauteur))
    
    
    for i in docs.id2doc.copy():
        if type(docs.id2doc[i].texte) is not str :
            docs.rem_document(i)
        else : 
            nbcara = len(str(docs.id2doc[i].texte))
            if nbcara<20:
                docs.rem_document(i)

    #docs.save("test")
docs.concorde("electron")