import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="Sistema IA - CRO MG", page_icon="🏛️", layout="centered")

st.markdown("""
    <style>
        .stApp { background-color: #F4F6F8; }
        .main-header { text-align: center; color: #8B2635 !important; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 800; font-size: 32px; margin-bottom: 2px; }
        .sub-header { text-align: center; color: #8B2635 !important; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 600; font-size: 22px; margin-top: 0px; margin-bottom: 5px; }
        .system-badge { text-align: center; color: #6C757D; font-size: 14px; margin-bottom: 30px; }
        div.stButton > button:first-child { background-color: #8B2635 !important; color: white !important; border-radius: 6px !important; font-weight: bold !important; width: 100% !important; height: 48px !important; margin-top: 15px; }
        div.stButton > button:first-child:hover { background-color: #6B1D29 !important; }
        .stChatMessage { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

api_key = os.getenv("OPENAI_API_KEY")

# SISTEMA DE BUSCA ATIVA DE CHUNKS EM ARQUIVOS ILIMITADOS (RAG EM MEMÓRIA)
def buscar_contexto_relevante(nome_arquivo, termo_busca, default_se_vazio=""):
    """
    Lê o arquivo inteiro sem limites de tamanho, divide-o em blocos (chunks)
    e filtra de forma inteligente apenas os blocos que contêm relação com a busca do usuário.
    """
    if not os.path.exists(nome_arquivo):
        return "Nenhum documento anexado para este setor."
        
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        # Lê o arquivo completo, independente de quão gigante ele seja
        conteudo_completo = f.read()
        
    # Se o usuário ainda não pesquisou nada específico, mandamos o histórico geral ou os primeiros blocos
    if not termo_busca or len(termo_busca.strip()) < 3:
        return conteudo_completo[:100000] # Buffer inicial de navegação
        
    # Os arquivos salvos do Drive foram divididos por '---' no processador
    chunks = conteudo_completo.split("---")
    termos = [t.lower().strip() for t in termo_busca.split()]
    
    chunks_encontrados = []
    
    for chunk in chunks:
        chunk_lower = chunk.lower()
        # Se contiver qualquer uma das palavras pesquisadas relevantes (ex: 'elevador' ou 'juiz')
        if any(termo in chunk_lower for termo in termos if len(termo) > 2):
            chunks_encontrados.append(chunk.strip())
            
    if chunks_encontrados:
        # Retorna apenas os contratos correspondentes à pesquisa com seus metadados de fonte reais
        return "\n\n---\n\n".join(chunks_encontrados)
        
    return "Nenhum documento na base de dados correspondeu aos termos da sua pesquisa."

USUARIOS = {
    "licitacao_user": {"senha": "cro_lic_2026", "setor": "Licitações e Contratos", "tipo": "restrito"},
    "atos_user": {"senha": "cro_ato_2026", "setor": "Atos Normativos", "tipo": "restrito"},
    "comunicacao_user": {"senha": "cro_com_2026", "setor": "Comunicação Institucional", "tipo": "restrito"},
    "assessoria_gerencial": {"senha": "cro_ger_2026", "setor": "Todos", "tipo": "global"},
    "secretaria_executiva": {"senha": "cro_exec_2026", "setor": "Todos", "tipo": "global"}
}

if "logado" not in st.session_state: st.session_state.logado = False
if "setor" not in st.session_state: st.session_state.setor = None
if "perfil_nome" not in st.session_state: st.session_state.perfil_nome = None
if "historico" not in st.session_state: st.session_state.historico = {}

if not st.session_state.logado:
    st.markdown("<div class='main-header'>🏛️ CONSELHO REGIONAL DE ODONTOLOGIA</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>MINAS GERAIS</div>", unsafe_allow_html=True)
    st.markdown("<div class='system-badge'>Sistema Interno de Inteligência Artificial Avançada</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        with st.container(border=True):
            setor_selecionado = st.selectbox("Selecione o Setor que deseja acessar:", ["Licitações e Contratos", "Atos Normativos", "Comunicação Institucional"])
            usuario_input = st.text_input("Usuário / E-mail do Servidor:")
            senha_input = st.text_input("Senha de Acesso:", type="password")
            
            if st.button("AUTENTICAR NO SISTEMA"):
                if usuario_input in USUARIOS and USUARIOS[usuario_input]["senha"] == senha_input:
                    dados_user = USUARIOS[usuario_input]
                    if dados_user["tipo"] == "global" or dados_user["setor"] == setor_selecionado:
                        st.session_state.logado = True
                        st.session_state.setor = setor_selecionado
                        st.session_state.perfil_nome = usuario_input.replace("_", " ").title()
                        if setor_selecionado not in st.session_state.historico:
                            st.session_state.historico[setor_selecionado] = []
                        st.rerun()
                    else:
                        st.error(f"❌ Usuário restrito ao departamento de {dados_user['setor']}.")
                else:
                    st.error("❌ Credenciais inválidas.")
else:
    setor = st.session_state.setor
    
    with st.sidebar:
        st.markdown(f"### 👤 Servidor Autenticado")
        st.success(f"**Identidade:** {st.session_state.perfil_nome}")
        st.info(f"**Painel Ativo:**\n{setor}")
        if st.button("Efetuar Logout"):
            st.session_state.logado = False
            st.session_state.setor = None
            st.session_state.perfil_nome = None
            st.rerun()

    st.markdown(f"<h2>💼 Painel Operacional: {setor}</h2>", unsafe_allow_html=True)
    st.markdown("---")

    arquivos_conhecimento = {
        "Licitações e Contratos": "conhecimento_licitacoes.txt",
        "Atos Normativos": "conhecimento_atos.txt",
        "Comunicação Institucional": "conhecimento_comunicacao.txt"
    }

    if len(st.session_state.historico[setor]) == 0:
        if setor == "Licitações e Contratos":
            msg_inicial = (
                f"Olá, {st.session_state.perfil_nome}! Sou o especialista técnico do setor de Licitações e Contratos do CRO-MG.\n\n"
                "Como posso colaborar com suas demandas hoje? Escolha uma das frentes digitando o número correspondente:\n\n"
                "🔹 **[1] ESCREVER** → Redigir termos de referência, editais ou minutas contratuais.\n"
                "🔹 **[2] REVISAR** → Auditar minutas, pareceres e conformidade com a Lei 14.133/21.\n"
                "🔹 **[3] CONSULTAR** → Realizar levantamentos nos contratos ativos de 2026."
            )
        elif setor == "Atos Normativos":
            msg_inicial = (
                f"Olá, {st.session_state.perfil_nome}! Sou o consultor técnico de Atos Normativos do conselho.\n\n"
                "Qual deliberação vamos estruturar hoje?\n\n"
                "🔹 **[1] ESCREVER** → Redigir minutas de resoluções, portarias e decisões formais.\n"
                "🔹 **[2] REVISAR** → Analisar termos legislativos e padronização oficial.\n"
                "🔹 **[3] CONSULTAR** → Verificar precedentes, vigências e bases históricas de 2026."
            )
        else:
            msg_inicial = (
                f"Olá, {st.session_state.perfil_nome}! Sou o estrategista de Comunicação Institucional do CRO-MG.\n\n"
                "Qual conteúdo vamos planejar ou produzir?\n\n"
                "🔹 **[1] CALENDÁRIO DE PUBLICAÇÃO** → Desenvolver cronogramas e linhas editoriais.\n"
                "🔹 **[2] CRIAR CAMPANHA** → Modelar conceitos e estratégias de conscientização.\n"
                "🔹 **[3] DESENVOLVER COPY** → Escrever textos finais focados no público de odontologia."
            )
        st.session_state.historico[setor].append({"role": "assistant", "content": msg_inicial})

    for msg in st.session_state.historico[setor]:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Digite sua mensagem para o especialista..."):
        st.session_state.historico[setor].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        # Realiza a busca dinâmica de termos relevantes dentro de TODO o arquivo TXT sem limite de tamanho
        contexto_dinamico = buscar_contexto_relevante(arquivos_conhecimento[setor], prompt)
        
        prompts_setores = {
            "Licitações e Contratos": (
                "Você é o Especialista Sênior em Licitações e Contratos do CRO-MG. Seu tom de resposta é de um colega técnico, amigável e focado. "
                "Use listas e negritos estrategicamente para deixar os retornos organizados.\n\n"
                "REGRA CRÍTICA DE NAVEGAÇÃO DE MENU:\n"
                "1. Se o usuário digitar '1' ou pedir para 'ESCREVER': Pergunte qual documento ele quer formular e qual o objeto principal.\n"
                "2. Se o usuário digitar '2' ou pedir para 'REVISAR': Solicite que ele envie o trecho ou a minuta a ser analisada sob as diretrizes da Lei 14.133/21.\n"
                "3. Se o usuário digitar '3' ou pedir para 'CONSULTAR': **NUNCA apresente um contrato específico diretamente de primeira.** "
                "Em vez disso, responda exatamente o seguinte:\n"
                "'Excelente! Ativei o canal de buscas de contratos e convênios ativos do CRO-MG para 2026.\n\n"
                "Para eu buscar com precisão na nossa base de dados, me informe:\n"
                "• O **número do contrato** (Ex: 017/2026); ou\n"
                "• O **nome da empresa / instituição parceira** (Ex: ABRAHOF); ou\n"
                "• O **assunto/objeto** de interesse.\n\n"
                "O que deseja que eu pesquise agora?'\n\n"
                "4. Apenas após ele fornecer essa chave de busca específica, você deve ler a base de contexto injetada abaixo para formular a resposta técnica detalhada. "
                "Se os documentos retornados no contexto não trouxerem nenhuma informação sobre o termo pesquisado, admita de forma polida e profissional que não localizou aquele contrato específico na base, incentivando o usuário a tentar buscar por outra palavra-chave (como o nome da contratada).\n\n"
                f"CONTEXTO EXTRAÍDO DA BASE DE DADOS (DINÂMICO E SEM LIMITES):\n{contexto_dinamico}"
            ),
            "Atos Normativos": (
                "Você é o Consultor Legislativo de Atos Normativos do CRO-MG. Responda de forma clara, utilizando tópicos espaçados.\n\n"
                "REGRA DE NAVEGAÇÃO DE MENU:\n"
                "- Se digitar '1' ou 'ESCREVER': Pergunte sobre qual tema será a nova minuta de portaria, deliberação ou resolução.\n"
                "- Se digitar '2' ou 'REVISAR': Solicite o ato para que seja feita a devida revisão da técnica legislativa.\n"
                "- Se digitar '3' ou 'CONSULTAR': **NUNCA** mostre um ato direto. Responda orientando o usuário a pesquisar especificando o número da portaria/resolução ou o tema legislativo.\n\n"
                f"CONTEXTO EXTRAÍDO DA BASE DE DADOS (DINÂMICO E SEM LIMITES):\n{contexto_dinamico}"
            ),
            "Comunicação Institucional": (
                "Você é o Redator e Estrategista de Comunicação Sênior do CRO-MG. Formate seus retornos de forma visual, limpa e moderna.\n\n"
                "REGRA DE NAVEGAÇÃO DE MENU:\n"
                "- Se digitar '1': Pergunte qual o período ou o foco temático do calendário editorial.\n"
                "- Se digitar '2': Pergunte qual o tema ou objetivo da campanha institucional.\n"
                "- Se digitar '3': Solicite o escopo ou os pontos chaves para criar as legendas ou postagens.\n\n"
                f"CONTEXTO EXTRAÍDO DA BASE DE DADOS (DINÂMICO E SEM LIMITES):\n{contexto_dinamico}"
            )
        }
            
        if not api_key:
            resposta_ia = "⚠️ Erro: Chave `OPENAI_API_KEY` ausente."
        else:
            try:
                client = OpenAI(api_key=api_key)
                mensagens_api = [{"role": "system", "content": prompts_setores[setor]}]
                for msg in st.session_state.historico[setor]:
                    mensagens_api.append({"role": msg["role"], "content": msg["content"]})
                
                completions = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=mensagens_api,
                    temperature=0.1
                )
                resposta_ia = completions.choices[0].message.content
            except Exception as e:
                resposta_ia = f"💥 Erro na resposta da IA: {e}"
        
        st.session_state.historico[setor].append({"role": "assistant", "content": resposta_ia})
        with st.chat_message("assistant"): st.write(resposta_ia)
