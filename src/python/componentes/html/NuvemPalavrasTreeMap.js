

if (typeof NuvemPalavrasTreeMap !== 'undefined'){

    console.error("Classe NuvemPalavrasTreeMap já foi definida")

}else{

    console.log ("Criando classe NuvemPalavrasTreeMap");

    class NuvemPalavrasTreeMap extends HTMLElement{



        constructor(){
            super();        
        }



        connectedCallback() {
            this.shadow = this.attachShadow({mode: 'open'});
            let template = document.createElement("template");
            template.innerHTML = `                        
                <style>
                    #treeMap{                        
                        width: 100%;
                        height: 100%;
                    }

                    .node_treemap_d3js {
                        border: solid 1px rgb(0, 0, 0);
                        font: 10px sans-serif;
                        line-height: 12px;                        
                        /*todo: melhorar css do ElementoNuvemPalavrasTreeMap para não poder deixar aqui como overflow auto*/
                        /*overflow: auto;*/
                        /*forçando não aparecer scroll caso a imagem da nuvem de palavras pegue algum espaço extra*/
                        overflow: hidden;
                        position: absolute;
                        text-indent: 2px;
                    }
                    
                    .container_treemap_d3js {
                        opacity: 0;      
                        height: 100%;
                        width: 100%;
                        animation: opacityOn .52s normal forwards step-end;
                        animation-delay: 0s;
                    }

                    @keyframes opacityOn {
                        0% {
                            opacity: 0.15;
                        }
                        25%{
                            opacity: 0.25;
                        }
                        50%{
                            opacity: 0.5;
                        }
                        75%{
                            opacity: 0.75;
                        }
                        100% {
                            opacity: 1;
                        }
                    }
                    
                    #conteudo{                                                
                        width:100%;
                        height:100%;
                        display:flex;
                        flex-direction:column;
                    }                                              

                    .preencher-espaco{
                        flex-grow:1;                        
                    }

                    #cabecalho{                               
                        width: 100%;                        
                        padding: 3px;
                        background-color: rgb(38, 80, 136);
                        color: white;                                                                   
                        gap: 100px;
                        display: flex;                                          
                        align-items: center;
                        justify-content: center;
                    }

                    #informacoes_nuvem_treemap{
                        display:flex;
                        flex-direction: row;
                        justify-content: center;
                        align-items: center;
                        gap: 25px;          
                        flex-grow:1;              
                    }

                    #titulo{
                        font-size: xx-large;                        
                    }                    
                    #qtd_registros{
                        font-size: medium;
                    }
                    .controle{
                        padding: 25px;
                        font-size: xx-large;
                        font-weight: bolder;
                        cursor: pointer;
                        filter: invert(42%) sepia(50%) saturate(2819%) hue-rotate(165deg) brightness(99%) contrast(102%);
                        transition: filter 2s ease-out;
                    }
                    .controle:hover{
                        filter: grayscale(100%) brightness(40%) sepia(100%) hue-rotate(-50deg) saturate(600%) contrast(0.8);
                    }
                </style>
                <div id='conteudo'>                                                            
                    <header id="cabecalho">
                        <div id='informacoes_nuvem_treemap'>
                            <div><span id='titulo'>Título do Cluster</span></div>                        
                            <div><span id='qtd_registros'>4000 registros</span></div>
                        </div>                        
                        <div>                            
                            <span id="btnFullScreen" class="controle">[+]</span>
                            <span id="btnVoltar" class="controle">[-]</span>
                        </div>
                    </header>                                      
                    <div id='treeMap'></div>                    
                </div>                
            `;

            let elemento = template.content.cloneNode(true);
            this.shadow.appendChild(elemento);

            setTimeout(()=>{                        
                this.container = this.shadow.querySelector("#treeMap");
                this.btnFullscreen = this.shadow.querySelector("#btnFullScreen");
                this.btnVoltar = this.shadow.querySelector("#btnVoltar");
                
                this.btnVoltar.style.display = "none";

                this.btnFullscreen.addEventListener("click", () => {                    
                    this.requestFullscreen().then(()=>{
                        this.fullScreen = true;       
                        this.btnVoltar.style.display = "inline";                 
                        this.btnFullscreen.style.display = "none";
                    });                                                              
                });

                this.btnVoltar.addEventListener("click", () => {
                    document.exitFullscreen();
                    this.fullScreen = false;    
                    this.btnVoltar.style.display = "none";                 
                    this.btnFullscreen.style.display = "inline"; 
                });                          

                this.atualizarDimensoes();                        
                this.observar();
                this.carregado = true;
                this.renderizar();
            });
        }



        renderizar(){
            if (this.dados && this.carregado){

                this.shadow.querySelector("#titulo").textContent = this.dados["titulo"];
                this.shadow.querySelector("#qtd_registros").textContent = this.dados["qtd_registros"] + " registros";

                if (!this.divD3){                    
                    this.criarTreeMap();
                }else{
                    this.enterUpdateExit();
                }
            }        
        }


        criarTreeMap(){

            d3.select(this.container).selectAll("div").remove();
        
            this.divD3 = d3.select(this.container).append("div")
                .style("position", "relative")
                .style("width", (this.widthTreemap + this.marginTreemap.left + this.marginTreemap.right) + "px")
                .style("height", (this.heightTreemap + this.marginTreemap.top + this.marginTreemap.bottom) + "px")
                .style("left", this.marginTreemap.left + "px")
                .style("top", this.marginTreemap.top + "px");
            
            this.enterUpdateExit();  
        }



        enterUpdateExit(){

            this.treemap = d3.treemap().size([this.widthTreemap, this.heightTreemap]);                                

            const root = d3.hierarchy(this.dados.nuvens, (d) => d.elementos)
                
                //Valor do elemento para cálculo da área do TreeMap
                .sum( d => d.qtd_registros)

                //Ordem dos elementos no Treemap
                .sort((a, b) => (b.data.qtd_registros - a.data.qtd_registros));         

            this.node = this.divD3.selectAll(".node_treemap_d3js").data(this.treemap(root).leaves(), d => d.data.id);                                      

            //EXIT
            this.node.exit().remove();
            
            let novosNos = this.node
                //ENTER
                .enter()
                    .append("elemento-nuvem-palavras-treemap")                    
                        .attr("class", "node_treemap_d3js container_treemap_d3js")
                        .attr("titulo",(d) => d.data.titulo)                    
                        .attr("qtd_registros",(d) => d.data.qtd_registros)     
                        .attr("imagem_base64",(d) => d.data.imagem_base64)                    
                        .style("left", (d) => d.x0 + "px")
                        .style("top", (d) => d.y0 + "px")
                        .style("width", (d) => Math.max(0, d.x1 - d.x0 - 1) + "px")
                        .style("height", (d) => Math.max(0, d.y1 - d.y0  - 1) + "px");
    
            this.node
                //UPDATE
                .transition().duration(500)
                    .style("left", d => {
                        //console.log (`******* ATUALIZANDO elemento-treemap: ${d.data.id} (ordem: ${d.data.ordem})`);
                        return `${d.x0}px`;
                    })
                    .style("top", d => `${d.y0}px`)
                    .style('width', d => `${Math.max(0, d.x1 - d.x0 -1)}px`)
                    .style('height', d => `${Math.max(0, d.y1 - d.y0 -1)}px`);                                    
        }



        atualizarTreeMap(){

            this.enterUpdateExit();
        }



        atualizarDimensoes(){
            if (this.container){
                this.marginTreemap = {top: 0, right: 0, bottom: 0, left: 0};
                this.widthTreemap = this.container.clientWidth - this.marginTreemap.left - this.marginTreemap.right;
                this.heightTreemap = this.container.clientHeight - this.marginTreemap.top - this.marginTreemap.bottom;
                //this.colorTreemap = d3.scaleOrdinal().range(d3.schemeCategory20c);
            }
        }



        processarNovasDimensoes(largura, altura){

            //console.info (`--------------------------------> ATUALIZOU DIMENSÕES DO CONTAINER TREEMAP`);

            this.atualizarDimensoes();
            this.renderizar();
        }



        observar(){
            this.resizeObserver = new ResizeObserver(elementos =>{
                elementos.forEach(elemento => {      
                    if (this.processarNovasDimensoes){
                        this.processarNovasDimensoes (elemento.target.clientWidth, elemento.target.clientHeight);
                    }
                });
            });
                            
            this.resizeObserver.observe(this);              
        }


        static get observedAttributes() {
            return ['dados'];
        }



        attributeChangedCallback(nomeAtributo, valorAntigo, novoValor) {


            if (nomeAtributo.localeCompare("dados") == 0){

                this.dados = JSON.parse(novoValor);

                this.renderizar();
            }
        }
    }
    if (!customElements.get('nuvem-palavras-treemap')){
        customElements.define('nuvem-palavras-treemap', NuvemPalavrasTreeMap);
    }else{
        console.error("Elemento nuvem-palavras-treemap já foi definido")
    }
}



if (typeof ElementoNuvemPalavrasTreeMap !== 'undefined'){

    console.error("Classe NuvemPalavrasTreeMap já foi definida")
        
}else{

    class ElementoNuvemPalavrasTreeMap extends HTMLElement{

        constructor(){
            super();        
        }


        connectedCallback() {
            this.shadow = this.attachShadow({mode: 'open'});
            let template = document.createElement("template");
            template.innerHTML = `
                <style>
                    #conteudo{                                                
                        width:100%;
                        height:100%;
                        display:flex;
                        flex-direction:column;
                        cursor: pointer;
                    }                          
                    #imagem{                                                                                              
                        width:100%;
                        height:calc(100% - 30px);
                    }

                    .preencher-espaco{
                        flex-grow:1;                        
                    }

                    #cabecalho{                               
                        width: 100%;
                        height: 30px;
                        padding: 3px;
                        background-color:  rgb(50, 102, 160);
                        color: white;                                                                   

                        display: flex;                                          
                        align-items: center;
                        justify-content: center;
                    }

                    #informacoes_nuvem{
                        display:flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        gap: 5px;
                        flex-grow:1;
                    }

                    #titulo{
                        font-size: medium;
                        white-space: nowrap;
                        text-overflow: ellipsis;
                    }                    
                    #qtd_registros{
                        font-size: small;
                        white-space: nowrap;
                        text-overflow:"";
                    }                    
                </style>
                <div id='conteudo'>                                                            
                    <header id="cabecalho">
                        <div id='informacoes_nuvem'>
                            <div><span id='titulo'>Título</span></div>                        
                            <div><span id='qtd_registros'>0</span></div>
                        </div>                                                
                    </header>                                      
                    <img id='imagem'></img>                    
                </div>
            `;

            let elemento = template.content.cloneNode(true);
            this.shadow.appendChild(elemento);

            setTimeout(()=>{            
                this.container = this.shadow.querySelector("#conteudo");

                this.container.addEventListener("click", () => {   
                    if (!this.fullScreen){
                        this.requestFullscreen().then(()=>{
                            this.fullScreen = true;                                   
                        });                                                              
                    }else{
                        document.exitFullscreen();
                        this.fullScreen = false;                        
                    }
                });         

                this.carregado = true;            
                this.renderizar();
            });
        }

        renderizar(){
            if (this.titulo &&  this.qtd_registros && this.imagem_base64 && this.carregado){
                this.shadow.querySelector("#titulo").textContent = this.titulo;
                this.shadow.querySelector("#qtd_registros").textContent = this.qtd_registros + " registros";
                this.shadow.querySelector("#imagem").src = this.imagem_base64;
            }
        }

        

        static get observedAttributes() {
            return ['titulo','qtd_registros', 'imagem_base64'];
        }



        attributeChangedCallback(nomeAtributo, valorAntigo, novoValor) {


            if (nomeAtributo.localeCompare("titulo") == 0){

                this.titulo = novoValor;

                this.renderizar();

            }else if (nomeAtributo.localeCompare("qtd_registros") == 0){

                this.qtd_registros = novoValor;
    
                this.renderizar();

            }else if (nomeAtributo.localeCompare("imagem_base64") == 0){

                this.imagem_base64 = novoValor;

                this.renderizar();
            }
        }
    }        
    if (!customElements.get('elemento-nuvem-palavras-treemap')){
        customElements.define('elemento-nuvem-palavras-treemap', ElementoNuvemPalavrasTreeMap);
    }else{
        console.error("Elemento elemento-nuvem-palavras-treemap já foi definido")
    }
}