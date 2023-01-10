if (typeof GrafoBases !== 'undefined'){

    console.error("Classe GrafoBases já foi definida")

}else{

    console.log ("Criando classe GrafoBases");

    class GrafoBases extends HTMLElement {
        


        //Cores usadas para cada tipo de dados
        static INFORMACOES_TIPO_DADO = {
            "texto":{"cor":"#ffff99","titulo":"Campo Texto"},
            "decimal":{"cor":"#66ccff","titulo":"Campo Decimal"},
            "inteiro":{"cor":"#99ff66","titulo":"Campo Inteiro"},
            "bytes":{"cor":"#ff0066","titulo":"Campo Bytes"}
        }

        

        //https://stackoverflow.com/questions/5560248/programmatically-lighten-or-darken-a-hex-color-or-rgb-and-blend-colors
        static pSBC=(p,c0,c1,l)=>{
            let r,g,b,P,f,t,h,i=parseInt,m=Math.round,a=typeof(c1)=="string";
            if(typeof(p)!="number"||p<-1||p>1||typeof(c0)!="string"||(c0[0]!='r'&&c0[0]!='#')||(c1&&!a))return null;
            if(!this.pSBCr)this.pSBCr=(d)=>{
                let n=d.length,x={};
                if(n>9){
                    [r,g,b,a]=d=d.split(","),n=d.length;
                    if(n<3||n>4)return null;
                    x.r=i(r[3]=="a"?r.slice(5):r.slice(4)),x.g=i(g),x.b=i(b),x.a=a?parseFloat(a):-1
                }else{
                    if(n==8||n==6||n<4)return null;
                    if(n<6)d="#"+d[1]+d[1]+d[2]+d[2]+d[3]+d[3]+(n>4?d[4]+d[4]:"");
                    d=i(d.slice(1),16);
                    if(n==9||n==5)x.r=d>>24&255,x.g=d>>16&255,x.b=d>>8&255,x.a=m((d&255)/0.255)/1000;
                    else x.r=d>>16,x.g=d>>8&255,x.b=d&255,x.a=-1
                }return x};
            h=c0.length>9,h=a?c1.length>9?true:c1=="c"?!h:false:h,f=this.pSBCr(c0),P=p<0,t=c1&&c1!="c"?this.pSBCr(c1):P?{r:0,g:0,b:0,a:-1}:{r:255,g:255,b:255,a:-1},p=P?p*-1:p,P=1-p;
            if(!f||!t)return null;
            if(l)r=m(P*f.r+p*t.r),g=m(P*f.g+p*t.g),b=m(P*f.b+p*t.b);
            else r=m((P*f.r**2+p*t.r**2)**0.5),g=m((P*f.g**2+p*t.g**2)**0.5),b=m((P*f.b**2+p*t.b**2)**0.5);
            a=f.a,t=t.a,f=a>=0||t>=0,a=f?a<0?t:t<0?a:a*P+t*p:0;
            if(h)return"rgb"+(f?"a(":"(")+r+","+g+","+b+(f?","+m(a*1000)/1000:"")+")";
            else return"#"+(4294967296+r*16777216+g*65536+b*256+(f?m(a*255):0)).toString(16).slice(1,f?undefined:-2)
        }


        constructor(){
            super();
            this.mostrarDetalheCampos = false;
        }



        connectedCallback(){
            this.shadow = this.attachShadow({mode: 'open'});
            let template = document.createElement("template");
            template.innerHTML = `
                <style>
                    .ocupar_area_total{    
                        width: 100%;
                        height: 100%;
                    }
                    
                    /*
                    #divGrafo{
                        background-color: black;
                    }
                    */
                </style>
                <div id="divElemento" class="ocupar_area_total">
                    <div id="divConteudo" class="ocupar_area_total">
                        <div class="ocupar_area_total container-fluid" id="divGrafo" style="display:block;height:100%">
                        </div>
                    </div>
                </div>                  
            `;

            let elemento = template.content.cloneNode(true);
            this.shadow.appendChild(elemento);

            setTimeout(()=>{                        
                this.vis = true;
                this.renderizar();
            });
        }



        renderizar(){
            if (this.vis && this.dados && !this.grafo && !this.gerandoGrafo){
                this.gerarGrafo();
            }
        }



        static get observedAttributes() {
            return ['mostrar-detalhes', 'dados'];
        }



        attributeChangedCallback(nomeAtributo, valorAntigo, novoValor) {

            if (nomeAtributo.localeCompare("dados") == 0){
                let dados = JSON.parse(novoValor);

                if (dados.src){ 
                    this.src = dados.src;

                    fetch(this.src)
                        .then(retorno => retorno.json())
                        .then(json => {
                            this.dados = json;
                            this.renderizar();
                        })
                        .catch (e => alert (e));

                }else{
                    this.dados = dados;
                    this.renderizar();
                }

            }else if (nomeAtributo.localeCompare("mostrar-detalhes") == 0){
                this.mostrarDetalheCampos = JSON.parse(novoValor);
            }            
        } 


    gerarGrafo (){

            this.gerandoGrafo = true;

            if (this.vis && this.dados){


                this.idGrafo = 0;
                let elementosGrafo = this.transformarDadosEmGrafo();

                /*
                let options = {
                    physics: {
                        stabilization: false,                    
                    }
                };
                */
                const options = {
                    "edges": {
                    "smooth": {
                        "forceDirection": "none"
                    }
                    },
                    "physics": {
                    "forceAtlas2Based": {
                        "springLength": 100
                    },
                    "minVelocity": 0.75,
                    "solver": "forceAtlas2Based",
                    "timestep": 0.51                  
                    }
                }

                this.elementosGrafo = elementosGrafo;
                this.grafo = new vis.Network (this.shadow.querySelector("#divGrafo"), this.elementosGrafo, options);            

                this.grafo.on ("click", parametros => {
                    console.dir(parametros);
                    this.dispatchEvent(new UltimaEvento(UltimaEvento.EVENTO_SELECAO_OBJETO, parametros));
                });

                this.gerandoGrafo = false;

                //window.requestAnimationFrame(this.animarGrafo.bind(this));
            }
        }

        animarGrafo(timestamp){
            if (!this.inicio) this.inicio = timestamp;
            this.elementosGrafo.nodes.update(
                this.elementosGrafo.nodes.get().map(no => {        
                    no.color = ((Math.random() < 0.5) ?"red" :"blue");
                    return no;
                })
            );
            
            window.requestAnimationFrame(this.animarGrafo.bind(this));
        }



        transformarDadosEmGrafo (){

            let sistemas_renderizados = {};
            let campos_renderizados = {};

            let elementosGrafo = {nodes:new vis.DataSet(), edges:new vis.DataSet()};

            console.log (`transformarDadosEmGrafo`);

            Object.entries(this.dados.bases).forEach(entrada => {                    

                let [nome_base, base] = entrada;            

                console.log(`${nome_base}`);

                let id_sistema = `sistema_${base.sistema}`;

                if (!sistemas_renderizados[id_sistema]){
                    let no_sistema = {
                        label: base.sistema,
                        id: id_sistema,                
                        size:45,
                        font:{
                            size: 32,
                            color:"black"
                        },             
                        color: "black",   
                        shape: "dot"
                    };
                    elementosGrafo.nodes.add(no_sistema);
                    sistemas_renderizados[id_sistema] = true;
                }

                let titulo_base = (base.titulo ? base.titulo : base.nome);

                let log_numero_maximo_regitros = Math.max(...Object.entries(base.campos).map(campo => campo[1].log_quantidade_registros));

                let no_base = {
                    label: titulo_base,
                    id: `${id_sistema}_base_${base.nome}`,                
                    size:log_numero_maximo_regitros * 3,
                    font:{
                        size: 32,
                        color:"black",                        
                    },
                    color:{
                        background:"white",
                        border:"black"
                    },
                    group: base.nome,
                    shape: "dot"
                };
                elementosGrafo.nodes.add(no_base);

                let ligacao_sistema = {
                    to: no_base.id,
                    from: id_sistema               
                }
                elementosGrafo.edges.add(ligacao_sistema);

                Object.entries(base.campos).forEach(entradaCampo => {

                    let [nome_campo, campo] = entradaCampo; 

                    let metadados_tipo_dado = GrafoBases.INFORMACOES_TIPO_DADO[campo.tipo_dado];
                    let cor_base = (metadados_tipo_dado ? metadados_tipo_dado.cor : "#000000");                    

                    
                    let escuro_maximo = -0.6;
                    let cor = GrafoBases.pSBC (escuro_maximo*campo.taxa_variacao, cor_base);
                    let cor_registros_unicos = GrafoBases.pSBC (escuro_maximo, cor_base);


                    if (!campos_renderizados[campo.nome]){
                        let no_campo = {
                            label: campo.nome,
                            id: campo.nome,
                            size: campo.log_quantidade_registros*3,
                            font:{
                                size: 27,
                                color: "black"
                            },
                            group:base.nome,
                            shape: "dot",                            
                            color:{
                                background:cor,
                                border:GrafoBases.pSBC (-0.25, cor)
                            }                       
                        };
                        elementosGrafo.nodes.add(no_campo);
                        campos_renderizados[campo.nome] = true;
                    }

                    if (campo.nuvem_palavras_base64 && this.mostrarDetalheCampos){

                        let no_nuvem_palavras = {                        
                            id:`${no_base.id}-${campo.nome}-nuvem_palavras`,
                            shape:"circularImage",
                            image: campo.nuvem_palavras_base64,                    
                            size: 30,
                            group: base.nome                    
                        }
                        elementosGrafo.nodes.add(no_nuvem_palavras);

                        elementosGrafo.edges.add({
                            from: no_base.id,
                            to: no_nuvem_palavras.id, 
                            width: campo.log_quantidade_registros                       
                        });

                        elementosGrafo.edges.add({
                            to: campo.nome,
                            from: no_nuvem_palavras.id,   
                            width: campo.log_quantidade_registros                     
                        });


                    }else{                        

                        elementosGrafo.edges.add({
                            from: no_base.id,
                            to: campo.nome,

                            width: campo.log_quantidade_registros,                           
                            color:{
                                color: cor_base
                            }
                        });

                        elementosGrafo.edges.add({
                            from: no_base.id,
                            to: campo.nome,
                            width: campo.log_quantidade_registros_unicos,
                            color:{
                                color:cor_registros_unicos
                            },
                            shadow:{
                              enabled: false,
                              color: 'rgba(0,0,0,0.5)',
                              size:10,
                              x:5,
                              y:5
                            }
                        });
                    }
                });                           
            });

            return elementosGrafo;
        }
    }

    if (!customElements.get('grafo-bases')){
        customElements.define('grafo-bases', GrafoBases);
    }else{
        console.error("Elemento grafo-bases já foi definido")
    }    
}
