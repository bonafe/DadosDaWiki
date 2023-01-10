import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import colorsys
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import uuid
import base64
import io
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from string import Template
from IPython.core.display import HTML
import json
from urllib.request import urlopen



class VisualizadorDataFrames:

    
    #Cores usadas para cada tipo de dados
    INFORMACOES_TIPO_DADO = {
        "texto":{"cor":"#ffff99","titulo":"Texto"},
        "decimal":{"cor":"#66ccff","titulo":"Decimal"},
        "inteiro":{"cor":"#99ff66","titulo":"Inteiro"},
        "bytes":{"cor":"#ff0066","titulo":"Bytes"}
    }

    DTYPE_CLASS_NAME_PARA_TIPO_DADO = {
        ('object','bytes'): "bytes",
        ('object','str'): "texto",
        ('object','int'): "inteiro",
        ('object','float'): "decimal",
        ('object','Decimal'): "decimal",
        ('float64','float64'): "decimal",
        ('int32','int32'): "inteiro",
        ('int64','int64'): "inteiro"
    }
    
    
    
    def __init__(self, dfs):                        
         
        self.prepararGrafoBases()
            
        if type(dfs) == list:
            
            self.dfs = dfs
                
        elif isinstance(dfs, pd.DataFrame):
        
            self.dfs = [dfs]
        
            
        #Dicionário com as métricas de cada DataFrame
        self.dfs_metricas = {}
            
            
        #Inicializa as os Dataframes de métricas a partir dos dados dos Dataframes originais
        for df in self.dfs:                        
            
            #Inicializa o atributo name do Dataframe caso não tenha sido atribuido anteriormente          
            if not hasattr(df,'name'):
                
                #Gera um nome usando o método uuid.uuid1(): "make a UUID based on the host ID and current time"
                #https://docs.python.org/3/library/uuid.html
                df.name = str(uuid.uuid1())
                
            #Atualiza o Dataframe de Métricas correspondente ao atributo name deste Dataframe com suas métricas
            self.dfs_metricas[df.name] = self.gerarMetricas(df)   
                      
        
        
    def exibirGrafoBases(self, metadados, mostrarDetalhes=False):
        
        display(
            HTML(
                self.html_template.substitute({
                    'script_grafo_bases':self.html_grafo_bases,
                    'dados':json.dumps(metadados),
                    'mostrarDetalhes': 'true' if mostrarDetalhes else 'false'
                })
            )
        )
                
            
                
    def prepararGrafoBases(self):
        
        #TODO: Os arquivos da biblioteca do vis.js e GrafoBases.js estão sendo chamados a partir da web
        #O ideal era que fossem chamados localmente, entretanto ao mudar o local do notebook que está instanciado esta classe
        #a localização relativa do arquivo muda. Para ter um caminho fixo optou-se por colocamos na web (github.io)
        #Verificar como fazer para usar caminhos relativos ou criar um "bundle" com todo conteúdo dos arquivos JS
        
        display(HTML("""
        <script>
            require.config({
                paths: {
                    vis: 'https://bonafe.github.io/CienciaDadosPython/src/componentes/html/bibliotecas/vis-network.min'
                }
            });
        </script>
        """))

        #with open('./html/GrafoBases.js') as f:
        #    self.html_grafo_bases = " ".join(f.readlines())
        
        self.html_grafo_bases = urlopen("https://bonafe.github.io/CienciaDadosPython/src/componentes/html/GrafoBases.js").read().decode("utf-8") 

        self.html_template = Template('''    
            <script>
                require(["vis"], function(vis) {
                    $script_grafo_bases
                });
            </script>    
            <div style="background-color:white;width:100%; height:500px">
                <grafo-bases dados='$dados' class="secao_principal" mostrar-detalhes="$mostrarDetalhes"></grafo-bases>  
            </div>
        ''')
                
    
    
    @staticmethod 
    def ajustar_luminosidade(cor, quantidade=0.5):
        
        try:
            c = mc.cnames[cor]
        except:
            c = cor                    
            
        c = colorsys.rgb_to_hls(*mc.to_rgb(c))
        
        return colorsys.hls_to_rgb(c[0], max(0, min(1, quantidade * c[1])), c[2])
    
    
    
    @staticmethod
    def dtype_nome_classe_para_tipo_dado (dtype, nome_classe):
        
        if (str(dtype), str(nome_classe)) in VisualizadorDataFrames.DTYPE_CLASS_NAME_PARA_TIPO_DADO:
            
            return VisualizadorDataFrames.DTYPE_CLASS_NAME_PARA_TIPO_DADO.get((str(dtype), str(nome_classe)))                
        
        else:
            
            retorno = f'dtype: {dtype} - nome_classe: {nome_classe} - NÃO ENCONTRADO'
            
            return retorno
    
    
    
    @staticmethod
    def informacoes_tipo_dado (tipo_dado):                
        
        if tipo_dado in VisualizadorDataFrames.INFORMACOES_TIPO_DADO:
            
            return VisualizadorDataFrames.INFORMACOES_TIPO_DADO.get(tipo_dado)                
        
        else:                        
            
            retorno = {'cor':'#000000', 'titulo':f'Tipo Dado: {tipo_dado} - NÃO ENCONTRADO'}                        
            
            return retorno

        
        
    def gerarMetricas (self, df):

        df_metricas = pd.DataFrame()
        
        
        df_metricas["quantidade_registros"] = df.count().to_frame()[0]

        df_metricas["quantidade_registros_unicos"] = df.nunique().to_frame()[0]       

        df_metricas["taxa_variacao"] = df_metricas["quantidade_registros_unicos"] / df_metricas["quantidade_registros"]        
        df_metricas["taxa_variacao"].fillna(0, inplace=True)        
        
        df_metricas["log_quantidade_registros"] = np.log(df_metricas["quantidade_registros"])            
        df_metricas["log_quantidade_registros"].replace([np.inf, -np.inf], np.nan, inplace=True)
        df_metricas["log_quantidade_registros"].fillna(0, inplace=True)

        df_metricas["log_quantidade_registros_unicos"] = np.log(df_metricas["quantidade_registros_unicos"])            
        df_metricas["log_quantidade_registros_unicos"].replace([np.inf, -np.inf], np.nan, inplace=True)
        df_metricas["log_quantidade_registros_unicos"].fillna(0, inplace=True)
        
        df_metricas["taxa_variacao_log"] = df_metricas["log_quantidade_registros_unicos"] / df_metricas["log_quantidade_registros"]
        df_metricas["taxa_variacao_log"].replace([np.inf, -np.inf], np.nan, inplace=True)
        df_metricas["taxa_variacao_log"].fillna(0, inplace=True)

        df_metricas = pd.concat([df_metricas, VisualizadorDataFrames.tipo_dados(df)], axis=1)
    
        
        df_metricas.sort_values("quantidade_registros_unicos", inplace=True)
        
        return df_metricas
    
    
            
    def exibirMetricas(self, nome_dataframe, log, figsize=(16,12)):
        
        df_metricas = self.dfs_metricas[nome_dataframe]
        
        campo_quantidade_registros = "quantidade_registros"
        campo_quantidade_registros_unicos = "quantidade_registros_unicos"
        campo_taxa_variacao = "taxa_variacao"
                
        ylabel = 'Qtd. Registros'
        label_contagem = 'Qtd. Total de Registros'
        label_unicos = 'Qtd. Total de Registros Únicos'
        label_variacao = 'Taxa de Variação (Únicos//Total)'        
        
        
        if log:
                
            campo_quantidade_registros = "quantidade_registros_log"
            campo_quantidade_registros_unicos = "quantidade_registros_unicos_log"
            campo_taxa_variacao = "taxa_variacao_log"
                
            ylabel = f'Log {ylabel}'
            label_contagem = f'Log {label_contagem}'
            label_unicos = f'Log {label_unicos}'
            label_variacao = f'Taxa de Variação (Log Únicos//Log Total)'
               
                
        X_axis = np.arange(len(df_metricas.index))
                
        fig = None
                
        fig = plt.figure(figsize=figsize)                                    
            
        ax = fig.add_subplot(111)

        fig.patch.set_facecolor("white")
        
        ax.set_title('Métricas das quantidades de registros nos campos')
        ax.set_xlabel('Nome do campo')
        ax.set_ylabel(ylabel)
        
        ax.set_xticks(X_axis, labels=df_metricas.index)
        #plt.setp(ax.get_xticklabels(), rotation=45, ha="right", va='bottom', rotation_mode="anchor")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    
        plt.bar(
            X_axis,
            df_metricas[campo_quantidade_registros],
            width=0.8,                        
            linewidth=2,
            label=label_contagem,
            color=df_metricas["cor_tipo_dado"],
            edgecolor = df_metricas.apply (
                lambda linha : VisualizadorDataFrames.ajustar_luminosidade(linha["cor_tipo_dado"]),
                axis=1
            )            
        )                        
        
        cor_unicos = (0/255, 0/255, 0/255, 0.45)
        
        plt.bar(
            X_axis - 0.2, 
            df_metricas[campo_quantidade_registros_unicos],
            width=0.4,
            edgecolor = "black",
            label=label_unicos,
            color=cor_unicos
        )
        
        #TODO: quando tem o mesmo valor está sobrepondo
        #for barras in ax.containers:
        #    ax.bar_label(barras)

        
        #Para colocar outro eixo y no mesmo gráfico
        axVariacao = ax.twinx()

        
        cor_variacao = (240/255, 96/255, 0/255, 0.75)
        
        axVariacao.set_ylabel('Taxa de Variação')

        plt.bar(
            X_axis + 0.2, 
            df_metricas[campo_taxa_variacao],
            width=0.3,
            edgecolor = "black",            
            label=label_variacao,
            color=cor_variacao
        )


        """
        data_table = plt.table(
            cellText=[["1","2","3"], ["4", "5", "6"], ["7", "8", "9"]],
            rowLabels=["L1","L2","L3"],
            colLabels=["C1","C2","C3"],
            rowColours=["red","green","blue"],
            colWidths=[0.25, 0.25, 0.25],
            loc='bottom'
        )

        data_table.scale(1, 2)
        data_table.set_fontsize(12)
        """                                 
        
        axVariacao.set_ylim([0,1])
        

        handles, labels = ax.get_legend_handles_labels()
        handlesV, labelsV = axVariacao.get_legend_handles_labels()                
        
        elementos_legenda = []
        
        
        for chave in self.INFORMACOES_TIPO_DADO:            
            elementos_legenda.append(
                Patch(
                    facecolor=VisualizadorDataFrames.INFORMACOES_TIPO_DADO[chave]["cor"], 
                    edgecolor='b', 
                    label=VisualizadorDataFrames.INFORMACOES_TIPO_DADO[chave]["titulo"]
                )
            )
        
        
        elementos_legenda += [
            Patch(facecolor=cor_unicos, edgecolor='b', label=label_unicos),
            Patch(facecolor=cor_variacao, edgecolor='b', label=label_variacao)
        ]
        
        #axVariacao.legend(handles=elementos_legenda, loc='lower right', borderaxespad=0)
        axVariacao.legend(handles=elementos_legenda, loc='lower center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
        
        
        plt.tight_layout()
        
        #ax.yaxis.set_ticks_position("right")
        #axVariacao.yaxis.set_ticks_position("left")
                
        #plt.show()
        
        
        
    @staticmethod
    def gerar_nuvem_palavras(texto):
        return WordCloud(max_font_size=50, max_words=100, background_color="white").generate(texto)
        
        
        
    #Os dataframes precisam ter a propriedade name correspondente a chave do dicionario metadados
    def gerarMetadados (self, metadados={}):    

        novos_metadados = {"bases":{}}

        for df in self.dfs:

            if (df.name in novos_metadados):
                raise(f'Atenção: Nome do DataFrame repetido: {df.name}')
                
            else:

                #Cria novos metadados para este DataFrame
                novos_metadados["bases"][df.name] = {
                    "nome": df.name,                    
                    "campos": {}
                } 
                                                        
                if df.name in metadados:
                    
                    #Adiciona os metadados passados como parâmetros para função
                    novos_metadados["bases"][df.name] = {**novos_metadados["bases"][df.name], ** metadados[df.name]}
                
                novos_metadados["bases"][df.name]["campos"] = self.dfs_metricas[df.name].to_dict("index")
                
                for chave, campo in novos_metadados["bases"][df.name]["campos"].items():
                    
                    campo["nome"] = chave
                    
                    if campo["tipo_dado"] == 'texto':
                                                
                        texto_coluna = ' '.join(map(lambda e: str(e), df[chave].tolist()))
                        nuvem_palavras = None
                        
                        
                        #TODO: Voltar Nuvem Palavras                        
                        #try:
                        #    nuvem_palavras = VisualizadorDataFrames.gerar_nuvem_palavras(texto_coluna)
                        #    
                        #except ValueError as error:                        
                            #contagem = df[chave].value_counts()
                            #contagem.index = contagem.index.map(str)
                            #nuvem_palavras = WordCloud().generate_from_frequencies(contagem)
                        nuvem_palavras = VisualizadorDataFrames.gerar_nuvem_palavras("teste")
                            
                        buffer_nuvem_palavras = io.BytesIO()
                        nuvem_palavras.to_image().save(buffer_nuvem_palavras, 'png')
                        campo["nuvem_palavras_base64"] = f'data:image/png;base64,{base64.b64encode(buffer_nuvem_palavras.getvalue()).decode("utf-8")}'
                        
                    
        return novos_metadados
        
        

    @staticmethod
    def tipo_dados(df):            
                        
        df_tipo_dados =  pd.DataFrame()
        
        
        #Nome do dtype da coluna
        df_tipo_dados["dtype_coluna"] = df.dtypes.to_frame()[0].map(str)

        
        #Nome da classe do primeiro elemento daquela coluna
        df_tipo_dados["nome_classe"] = pd.Series(
            [
                df.iat[0, indice_coluna].__class__.__name__ 
                    for indice_coluna in range(df.shape[1])
            ],
            index = df_tipo_dados.index
        )
        
        
        #Cria uma nova coluna tipo_dados com o tipo do dado corresponde ao par DTYPE_COLUNA e NOME_CLASSE
        # no dicionário DTYPE_CLASS_NAME_CORES_TIPO_DADO
        df_tipo_dados["tipo_dado"] = df_tipo_dados.apply (
            lambda linha : VisualizadorDataFrames.dtype_nome_classe_para_tipo_dado (linha["dtype_coluna"], linha["nome_classe"]),
            axis=1
        )
        
        
        #Cria uma nova coluna com a cor do tipo_dado calculado
        df_tipo_dados["cor_tipo_dado"] = df_tipo_dados.apply (
            lambda linha : VisualizadorDataFrames.informacoes_tipo_dado(linha["tipo_dado"])["cor"],
            axis=1
        )  
        
        
        #Cria uma nova coluna com o título do tipo_dado calculado
        df_tipo_dados["titulo_tipo_dado"] = df_tipo_dados.apply (
            lambda linha : VisualizadorDataFrames.informacoes_tipo_dado(linha["tipo_dado"])["titulo"],
            axis=1
        )  
        
        
        #Retorna o DataFrame com os novos campos
        return df_tipo_dados
    
    
    