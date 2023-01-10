import os
from os import listdir
from os.path import isfile, join

import re

import numpy as np

from datetime import datetime

import json

import math

import pandas as pd

from IPython.display import display, Markdown

from kneed import KneeLocator

import nltk
from nltk.stem import *
from nltk.corpus import stopwords

import seaborn as sns

from sklearn.decomposition import TruncatedSVD

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

from gensim.parsing.preprocessing import remove_stopwords

import base64
import io

from IPython.core.display import HTML
from string import Template

from urllib.request import urlopen

import unidecode



class FerramentasLinguagemNatural:

    
    
    #Inicialização das variáveis estáticas
    stemmer = nltk.stem.RSLPStemmer()
    
    nltk.download('stopwords',  quiet=True) 
        
                            
            
    @staticmethod
    def prepararTexto(texto):            
        
        texto_sem_digitos =  re.sub('[0-9]', '', texto)
        
        texto_sem_acentos = unidecode.unidecode(texto_sem_digitos)
        
        itens = texto_sem_acentos.replace('\n', ' ').replace('.',' ').replace(':', ' ').split(' ')
        
        pontuacao = ['', '//', '-', ',', ';']
        
        for x in pontuacao:
            
            for n in range(itens.count(x)):
                itens.remove(x)
                
        l_palavras = []
        
        for palavra in itens:
            palavra = palavra.lower()
            palavra_stem = FerramentasLinguagemNatural.stemmer.stem(palavra)
            l_palavras.append(palavra_stem)

        return ' '.join(map(str, l_palavras))
    
    
    
    #A primeira forma de gerar uma nuvem de palavras a partir de uma Series do Pandas
    @staticmethod
    def gerarNuvemPalavras(series):        
        
        #Junta a Series inteira como string separada por espaço
        palavras = series.str.cat(sep=' ')

        # gera uma wordcloud usando generate (generate from text)
        nuvemPalavras = WordCloud(stopwords=FerramentasLinguagemNatural.stopwords_portugues,
                              background_color="white",
                              width=1200, height=600).generate(palavras)
        
        return nuvemPalavras
    
    
    
    @staticmethod
    def removerStopWordsTexto(texto, stopwords):
                        
        palavras = texto.split()

        palavrasResultantes  = [palavra for palavra in palavras if palavra.lower() not in stopwords]
        texto_resultado = ' '.join(palavrasResultantes)

        return texto_resultado
    
    
    
    @staticmethod
    def exibirCorpora(df, coluna):               
                        
        display(Markdown(f'# <center>Corpora da coluna *{coluna}*</center>'))        
        
        display(Markdown(f'Número de registros: ***{df[coluna].shape[0]}***'))        
            
        #Mostrar número de palavras
        quantidade_palavras = []
            
        for i in range(df[coluna].shape[0]):    
            try:
                quantidade_palavras.append(len(df[coluna].iloc[i].split(' ')))
            except:
                continue
        
        df_numero_palavras = pd.DataFrame(quantidade_palavras, columns = ['quantidade_palavras'])        
        
        #Mostrar distribuição do tamanho do texto na coluna        
        FerramentasLinguagemNatural.exibirHistograma(df_numero_palavras, 'quantidade_palavras', 'Distribuição da quantidade de palavras', 'Quantidade de palavras')        
        FerramentasLinguagemNatural.exibirMetricas(df_numero_palavras, f'Métricas da quantidade de palavras')
                
                                     
        FerramentasLinguagemNatural.exibirNuvemPalavras(df, coluna)                
        plt.show()
        
        quantidade_linhas = 25
        quantidade_colunas = 5
        
        dicionario = FerramentasLinguagemNatural.gerarDicionario (df[coluna])
        
        FerramentasLinguagemNatural.exibirHistograma(dicionario, 'contagem', 'Distribuição do número de ocorrências das palavras', 'Quantidade de ocorrências')
        FerramentasLinguagemNatural.exibirMetricas(dicionario, f'Métricas do número de ocorrência das palavras')
        FerramentasLinguagemNatural.mostrarTabelaIndicePalavras(dicionario, 'palavra', 'contagem', 'Número de ocorrências de cada palavra', False, quantidade_linhas, quantidade_colunas)        
        FerramentasLinguagemNatural.mostrarTabelaIndicePalavras(dicionario, 'palavra', 'contagem', 'Número de ocorrências de cada palavra', True, quantidade_linhas, quantidade_colunas)
        FerramentasLinguagemNatural.mostrarTabelaIndicePalavras(dicionario, 'palavra', 'tamanho', 'Tamanho de cada palavra', False, quantidade_linhas, quantidade_colunas)        
        FerramentasLinguagemNatural.mostrarTabelaIndicePalavras(dicionario, 'palavra', 'tamanho', 'Tamanho de cada palavra', True, quantidade_linhas, quantidade_colunas)
        
        
        
    @staticmethod   
    def gerarDicionario(serie):
                
        #Efetua contagem das palavras
        CV = CountVectorizer()

        #Remove o valores nulos da Serie e cria a matriz de contagem de cada palavra
        matriz_contagens = CV.fit_transform(serie.dropna())        
        
        #As features fo CountVectorizer são cada palavra individualmente
        df_dicionario = pd.DataFrame(CV.get_feature_names(), columns = ['palavra'])
        df_dicionario['contagem'] = matriz_contagens.sum(axis = 0).tolist()[0]
        df_dicionario['tamanho'] = df_dicionario['palavra'].str.strip().str.len()                        
        
        return df_dicionario
               
        
        
    @staticmethod         
    def exibirDicionario(df):
        display(df.info())
        display(df.sort_values('contagem', ascending=False).head(20))
        
        
        
    @staticmethod               
    def extenderListaParaVersaoStemm(lista_palavras):                
        
        lista_completa = []        
        
        #Mostra a contagem de palavras removendo stopwords
        for palavra in lista_palavras:            
            
            lista_completa.append(palavra)
            
            palavra_stem = FerramentasLinguagemNatural.stemmer.stem(palavra)            
            lista_completa.append(palavra_stem)        
        
        return lista_completa
        
                
        
    @staticmethod
    def removerStopWordsDicionario(dicionario, stopwords):
            
        #Adicionar a versão Stemm da stopword
        stopwords = FerramentasLinguagemNatural.extenderListaParaVersaoStemm(stopwords)
        
        #Adiciona as stopwords padrão
        stopwords.extend(FerramentasLinguagemNatural.stopwords_portugues)                    

        for palavra in stopwords:            
            df_remove = dicionario[dicionario["palavra"] == palavra]
            dicionario.drop (labels = df_remove.index, inplace = True)
                
        return dicionario
    
    
        
    @staticmethod
    def gerarListaEmColunas (lista, quantidade_linhas, quantidade_colunas):

        retorno = []

        for indice in range(quantidade_linhas):

            registro = []

            for coluna in range(quantidade_colunas):
                try:
                    registro.append(f'{lista[indice + (quantidade_linhas * coluna)]}')
                except:
                    registro.append("")

            retorno.append(registro)

        return retorno


    
    @staticmethod     
    def aplicarStem(df, coluna):
        coluna_stem = f'{coluna}_stem'
        df[coluna_stem] = df[coluna].apply(FerramentasLinguagemNatural.stemm_port)
        return (df, coluna_stem)
        
        
        
    @staticmethod
    def exibirNuvemPalavras(df, coluna):                
                
        display(Markdown(f'## <center>Palavras encontradas na coluna *{coluna}*</center>'))
            
        fig, ax_nuvem = plt.subplots(figsize=(16, 6))
        plt.imshow(FerramentasLinguagemNatural.gerarNuvemPalavras(df[coluna]), aspect='equal')                             
        plt.axis('off')         
            
            
                  
    @staticmethod              
    def exibirHistograma(df, campo, titulo, label):
        #plt.sca(ax_histograma)         
        fig, ax_histograma = plt.subplots(figsize=(16, 6))
        sns.histplot(df[campo], kde = False)
        plt.title(titulo, fontsize=16, fontweight='bold')
        ax_histograma.set_xlabel(label, fontsize=12, fontweight='bold')
        ax_histograma.set_ylabel('Quantidade de registros', fontsize=12, fontweight='bold')   
        plt.show()   
                    
        
        
    @staticmethod
    def exibirMetricas(df, titulo):
        #plt.sca(ax_metricas)        
        
        df_metricas = df.describe().transpose()
        
        fig, ax_metricas = plt.subplots(figsize=(16, 2))
        plt.title(titulo, fontsize=16, fontweight='bold')
        tabela = plt.table(
            cellText = df_metricas.values,
            colLabels=df_metricas.columns,
            cellLoc='left',
            loc='center')
        
        plt.axis('off')
        plt.show()   
        
        
        
    @staticmethod
    def mostrarTabelaIndicePalavras (df, campo_palavra, campo_indice, titulo, crescente, quantidade_linhas, quantidade_colunas):
        
        str_crescente = "crescente"
        
        if not crescente:
            str_crescente = "decrescente"
        
        df_sort = df.sort_values(campo_indice, ascending=crescente, inplace=False)                
        df_sort['resultado'] = df_sort[campo_indice].astype(str) + " - " + df_sort[campo_palavra]                                
        registros = df_sort.head(quantidade_linhas*quantidade_colunas)['resultado'].to_list()        
            
        fig, ax_distribuicao_palavras_decrescente = plt.subplots(figsize=(16, 6))
        #plt.sca(ax_distribuicao_palavras_decrescente)                        
        plt.title(f'{titulo} ({str_crescente})', fontsize=16, fontweight='bold')
        
        tabela = plt.table(
            cellText = FerramentasLinguagemNatural.gerarListaEmColunas(registros, quantidade_linhas, quantidade_colunas),
            cellLoc='left',
            loc='center')
        #tabela.auto_set_font_size(False)
        #tabela.set_fontsize(12)    
        plt.axis('off')
        plt.show()                            
    
   

    @staticmethod
    def carregarOpcoesTfidfVectorizer(opcoes):
        
        #Carrega o valor padrão do parâmetro ngram_range
        ngram_range = (1, 1)

        #Carrega o valor padrão do parâmetro max_df
        max_df = 1.0

        #Carrega o valor padrão do parâmetro min_df
        min_df = 1

        #Carrega o valor padrão do parâmetro max_features
        max_features = None

        stopwords = None
        
        if ('stopwords' in opcoes):
            
            stopwords = opcoes['stopwords']
            
            
        stopwords = FerramentasLinguagemNatural.carregarStopwords(stopwords)
            
        

        if ('TfidfVectorizer' in opcoes):

            #Caso tenha sido enviado o parametro ngram_range nas opções
            if ('ngram_range' in opcoes['TfidfVectorizer']):

                ngram_range = opcoes['TfidfVectorizer']['ngram_range']


            #Caso tenha sido enviado o parametro max_df nas opções
            if ('max_df' in opcoes['TfidfVectorizer']):

                max_df = opcoes['TfidfVectorizer']['max_df']


            #Caso tenha sido enviado o parametro min_df nas opções
            if ('min_df' in opcoes['TfidfVectorizer']):

                min_df = opcoes['TfidfVectorizer']['min_df']


            #Caso tenha sido enviado o parametro max_features nas opções
            if ('max_features' in opcoes['TfidfVectorizer']):

                max_features = opcoes['TfidfVectorizer']['max_features']
    
    
        return [ngram_range, max_df, min_df, max_features, stopwords]
    
    
    
    @staticmethod
    def carregarStopwords(lista_stopwords):
        
        #Carrega as stopwords padrão
        stopwords_ampliada = FerramentasLinguagemNatural.stopwords_portugues
                        
        #Caso tenha sido enviada uma lista de stopword nas opcoes
        if lista_stopwords is not None:

            #Adiciona a nova lista de stopwords e sua versão com Stemming
            stopwords_ampliada.extend (FerramentasLinguagemNatural.extenderListaParaVersaoStemm(lista_stopwords))  

        return stopwords_ampliada
    
    
    
    @staticmethod    
    def gerarMatrizTFIDF(lista_texto, opcoes):                                                                                   
        
        #Prepara o texto deixando em minúsculo, tirando acentos e números e fazendo Stemming das palavras
        lista_texto_processado = list(map (lambda item: FerramentasLinguagemNatural.prepararTexto(item), lista_texto))
        

        [ngram_range, max_df, min_df, max_features, stopwords] = FerramentasLinguagemNatural.carregarOpcoesTfidfVectorizer(opcoes)


        vectorizer = TfidfVectorizer(stop_words=stopwords, ngram_range=ngram_range, max_df=max_df, min_df=min_df, max_features=max_features)            

        fittedVectorizer = vectorizer.fit(lista_texto_processado)

        matrizTFIDF = fittedVectorizer.transform(lista_texto_processado)                        

        return matrizTFIDF, fittedVectorizer
            
            
            
    @staticmethod
    def carregarOpcoesKMeans(opcoes):                
        
        quantidade_clusters = 10
        
        if ('KMeans' in opcoes):
            if ('quantidade_clusters' in opcoes['KMeans']):
                quantidade_clusters = opcoes['KMeans']['quantidade_clusters']
                
        return [quantidade_clusters]                
            
    
                    
    @staticmethod
    def gerarCluster(df, coluna_texto, opcoes):
            
        #Remove os registros da coluna de texto com valor nulo
        lista_texto = df[df[coluna_texto].notna()][coluna_texto].unique() 
                        
            
        #Transforma a lista com o textos dos registros em uma matriz TFIDF
        matrizTFIDF, fittedVectorizer = FerramentasLinguagemNatural.gerarMatrizTFIDF (lista_texto, opcoes)        
                                        
        
        [quantidade_clusters] = FerramentasLinguagemNatural.carregarOpcoesKMeans(opcoes) 
        
        
        #Efetua a clusterização        
        modelo = KMeans(n_clusters=quantidade_clusters, init='k-means++', max_iter=300, n_init=10, random_state = 1)
        
        modelo.fit(matrizTFIDF)        
        
        coluna_cluster = f'{coluna_texto}_cluster_{quantidade_clusters}'
        
        df_cluster = pd.DataFrame(list(zip(lista_texto, modelo.labels_)),columns=[coluna_texto, coluna_cluster])
        
        df = pd.merge (df,  df_cluster,  how="left", on=coluna_texto)
        
        return [df, coluna_cluster, modelo, fittedVectorizer]
    
    
    
    @staticmethod
    def metodoDoCotovelo(df, coluna_texto, opcoes):
            
        #Remove os registros da coluna de texto com valor nulo
        lista_texto = df[df[coluna_texto].notna()][coluna_texto].unique() 
            
            
        stopwords = None
        
        if 'stopwords' in opcoes:
            
            stopwords = opcoes['stopwords']
            
        #Transforma a lista com o textos dos registros em uma matriz TFIDF
        matrizTFIDF, fittedVectorizer = FerramentasLinguagemNatural.gerarMatrizTFIDF (lista_texto, stopwords)
        
        
        sse = []
        
        [quantidade_maxima_clusters] = FerramentasLinguagemNatural.carregarOpcoesKMeans(opcoes) 
        
        for quantidade_clusters in range(1, quantidade_maxima_clusters):
            
            #display (f'Gerando cluster {quantidade_clusters} de {quantidade_maxima_clusters}')
            
            kmeans = KMeans(n_clusters=quantidade_clusters, init='k-means++', max_iter=300, n_init=10, random_state=1)
            kmeans.fit(matrizTFIDF)
            sse.append(kmeans.inertia_)

        kl = KneeLocator(range(1, quantidade_maxima_clusters), sse, curve="convex", direction="decreasing")
        display (f'Número ideal de clusteres: {kl.elbow}')
            
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.suptitle(f'Método do Cotovelo: {coluna_texto}', fontsize=20)
        plt.grid(b=True)
        plt.plot(range(1, quantidade_maxima_clusters), sse)
        plt.xticks(range(1, quantidade_maxima_clusters))
        plt.xlabel("Número de Clusters")
        plt.ylabel("SSE")
        plt.show()                
    
            
    
    @staticmethod
    def gerarStringOpcoesCluster (opcoes):
                
            
        [quantidade_clusters] = FerramentasLinguagemNatural.carregarOpcoesKMeans(opcoes)
                
        string_KMeans = f'qtd-clusters({quantidade_clusters})'
        
        
        [ngram_range, max_df, min_df, max_features] = FerramentasLinguagemNatural.carregarOpcoesTfidfVectorizer(opcoes)
        
        string_TfidfVectorizer = f'ngram-range{ngram_range}_max-df({max_df})_min-df({min_df})_max-features({max_features})'
        
        
        return [string_KMeans, string_TfidfVectorizer]
    
    
    
    #TODO: verificar se texto é Array ou String (agora só aceita String mas retorna Array com apenas uma posição)
    @staticmethod
    def classificarUsandoModelo(texto, modelo, fittedVectorizer):
        
        matrizTFIDF = fittedVectorizer.transform([texto])                                                        
        
        return modelo.predict(matrizTFIDF)
        
        
        
    @staticmethod
    def exibirClusters(df, coluna, coluna_cluster, titulo, treemap=True, lista_stopwords=None, imagens_separadas=False):
            
            #Carrega as stopwords padrão e amplia a lista de stopwords caso tenham sido enviadas na opções
            stopwords_ampliada = FerramentasLinguagemNatural.carregarStopwords(lista_stopwords)
            
            quantidade_clusters = df[coluna_cluster].nunique()
            
            quantidade_total_registros = df[coluna_cluster].count()
            
            
            dados = {"elementos":[]}
                                
            for cluster_atual in range(0, quantidade_clusters):
                
                df_cluster_atual = df[df[coluna_cluster] == cluster_atual]
            
                quantidade_registros_cluster_atual = df_cluster_atual[coluna_cluster].count()
            
                texto = df_cluster_atual[coluna].str.cat(sep=' ')
                
                texto = texto.lower()
            
                texto = ' '.join([palavra for palavra in texto.split()])
                
                nuvem_palavras = WordCloud(
                    stopwords=stopwords_ampliada,
                    max_font_size=50, 
                    max_words=100, 
                    background_color="white").generate(texto)                            

                textos = df[df[coluna_cluster] == cluster_atual][coluna]                        
                        
                elemento = {
                    "id":cluster_atual,
                    "titulo": f'Cluster {cluster_atual}',
                    "qtd_registros": int(quantidade_registros_cluster_atual),
                    "percentual_registros": float(quantidade_registros_cluster_atual / quantidade_total_registros)
                }
                
                if (treemap):                    
                    buffer = io.BytesIO()
                    nuvem_palavras.to_image().save(buffer, 'png')
                    elemento["imagem_base64"] = f'data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode("utf-8")}'                     
                else:
                    elemento["imagem"] = nuvem_palavras
                    
                dados["elementos"].append(elemento)                                                        
                    
                    
            if (treemap):
                
                dados_str = json.dumps({
                    "titulo":titulo,
                    "qtd_registros": str(quantidade_total_registros),
                    "nuvens":dados
                })
                display(HTML(FerramentasLinguagemNatural.html_template.substitute({'script_nuvem_palavras_treemap':FerramentasLinguagemNatural.html_nuvem_palavras_treemap, 'dados':dados_str})))

                
                
            else:                                                                
                
                dados["elementos"].sort (reverse=True, key= lambda elemento: elemento["qtd_registros"])                                
                
                if not imagens_separadas:
                
                    #TODO: Não está exibindo na orde correta
                    quantidade_colunas = 4
                    quantidade_linhas = int(math.ceil(quantidade_clusters / quantidade_colunas))

                    fig = plt.figure(figsize=(16,24))

                    fig.suptitle("Nuvem de palavras dos Clusters", fontsize=20)                

                    for elemento in dados["elementos"]:

                        ax = fig.add_subplot(quantidade_linhas, quantidade_colunas, elemento["id"]+1)
                        ax.set_title(f'{elemento["titulo"]} ({("%.1f" % (elemento["percentual_registros"]*100))}% - {elemento["qtd_registros"]} registros)')
                        plt.imshow(elemento["imagem"], interpolation="bilinear")
                        ax.axis("off")

                    fig.tight_layout(pad=1.5)
                    fig.patch.set_facecolor('white')

                    plt.show()                                                            


                else:

                    for elemento in dados["elementos"]:                                                
                        
                        fig, ax = plt.subplots(figsize=(5, 4))
                        ax.set_title(f'{elemento["titulo"]} ({("%.1f" % (elemento["percentual_registros"]*100))}% - {elemento["qtd_registros"]} registros)')
                        fig.patch.set_facecolor('white')
                        plt.imshow(elemento["imagem"], interpolation="bilinear")                            
                        plt.axis('off')                    
                        plt.show() 
                     
        
        
        
    @staticmethod
    def prepararNuvemPalavrasTreemap():
        
        display(HTML("""
        <script>
            require.config({
                paths: {
                    d3: 'https://bonafe.github.io/CienciaDadosPython/src/componentes/html/bibliotecas/d3.v5.min'
                }
            });
        </script>
        """))

        FerramentasLinguagemNatural.html_nuvem_palavras_treemap = urlopen("https://bonafe.github.io/CienciaDadosPython/src/componentes/html/NuvemPalavrasTreeMap.js").read().decode("utf-8") 

            
        FerramentasLinguagemNatural.html_template = Template('''    
            <script>
                require(["d3"], function(d3) {
                    $script_nuvem_palavras_treemap
                });
            </script>    
            <div style="background-color:black;width:100%; height:500px">
                <nuvem-palavras-treemap dados='$dados' class="secao_principal"></nuvem-palavras-treemap-->  
            </div>
        ''')
        
        
FerramentasLinguagemNatural.prepararNuvemPalavrasTreemap()

#Inicializa as stopwords em português com as stopwords do pacote nltk
#Extende as stopwords para a versão das palavras com Stemming
#Dessa forma elas podem ser usadas sobre textos onde já se aplicou Stemming
FerramentasLinguagemNatural.stopwords_portugues = FerramentasLinguagemNatural.extenderListaParaVersaoStemm(nltk.corpus.stopwords.words('portuguese'))
