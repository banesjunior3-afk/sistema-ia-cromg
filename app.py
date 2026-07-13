import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="Sistema IA - CRO MG", page_icon="🏛️", layout="centered")

# Estilização da interface para leitura limpa
st.markdown("""
    <style>
        .stApp { background-color: #F4F6F8; }
        .main-header { text-align: center; color: #8B2635 !important; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 800; font-size: 32px; margin-bottom: 2px; }
        .sub-header { text-align: center; color: #8B2635 !important; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 600; font-size: 22px; margin-top: 0px; margin-bottom: 5px; }
        .system-badge { text-align: center; color: #6C757D; font-size: 14px; margin-bottom: 30px; }
        div.stButton > button:first-child { background-color: #8B2635 !important; color: white !important; border-radius: 6px !important; font-weight: bold !important; width: 100% !important; height: 48px !important; margin-top: 15px; }
        div.stButton > button:first-child:hover { background-color: #6B1D29 !important; }
        
        /* Melhorias na legibilidade das mensagens de chat */
        .stChatMessage { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 15px; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

api_key = os.getenv("OPENAI_API_KEY")

def carregar_contexto_setor(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return f.read()[:50000]
    return "Nenhum documento anexado para este setor."

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

    contexto_real = carregar_contexto_setor(arquivos_conhecimento[setor])

    if len(st.session_state.historico[setor]) == 0:
        if setor == "Licitações e Contratos":
            msg_inicial = (
                f"Olá, {st.session_state.perfil_nome}! Sou o especialista técnico do setor de Licitações e Contratos do CRO-MG.\n\n"
                "Como posso colaborar com suas demandas hoje? Escolha uma das frentes:\n\n"
                "🔹 **[1] ESCREVER** → Redigir termos de referência, editais ou minutas contratuais.\n"
                "🔹 **[2] REVISAR** → Auditar minutas, pareceres e conformidade com a Lei 14.133/21.\n"
                "🔹 **[3] CONSULTAR** → Cruzar dados e verificar valores em contratos ativos de 2026."
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

    # PROMPT AVANÇADO: TONALIDADE AMIGÁVEL, CORREÇÃO TÉCNICA ATIVA E TEXTO ESCANEÁVEL
    prompts_setores = {
        "Licitações e Contratos": (
            "Você é o Especialista Sênior em Licitações e Contratos do CRO-MG. Seu tom é de um colega de equipe amigável, "
            "proativo e tecnicamente rigoroso. Você deve prezar por uma formatação altamente limpa, espaçada e de fácil leitura em tela (use listas e negritos estrategicamente).\n\n"
            "REGRA DE OURO DA LICITAÇÃO: Se o usuário misturar conceitos jurídicos contraditórios (por exemplo, pedir um 'pregão eletrônico por inexibilidade'), "
            "você deve corrigi-lo imediatamente no início da resposta com elegância e clareza (ex: explicar amigavelmente que ou é Pregão por competição ou Inexigibilidade por inviabilidade de competição). "
            "Baseie-se exclusivamente nos dados reais do conselho fornecidos abaixo. Se não souber por falta de dados contextuais, diga que não localizou a informação nas bases oficiais de 2026.\n\n"
            f"CONTEXTO REAL DO SETOR:\n{contexto_real}"
        ),
        "Atos Normativos": (
            "Você é o Consultor Legislativo de Atos Normativos do CRO-MG. Seu tom é solícito, inteligente e focado em excelência documental. "
            "Apresente suas respostas estruturadas de forma muito escaneável, quebrando textos longos e usando espaçamento adequado.\n\n"
            "Se o usuário pedir uma estrutura que fira a técnica legislativa padrão do conselho, oriente-o amigavelmente sobre o formato correto antes de continuar. "
            "Baseie-se unicamente nas portarias e dados abaixo. Se faltarem dados, informe de forma direta.\n\n"
            f"CONTEXTO REAL DO SETOR:\n{contexto_real}"
        ),
        "Comunicação Institucional": (
            "Você é o Redator e Estrategista de Comunicação Sênior do CRO-MG. Seu tom é dinâmico, criativo, engajador e alinhado aos preceitos da autarquia. "
            "Apresente propostas de posts, campanhas e copys de forma totalmente visual e escaneável (com emoticons sutis, tópicos claros e divisão por canais).\n\n"
            "Nunca misture abordagens comerciais inadequadas para conselhos de classe. Baseie-se apenas na realidade fornecida abaixo.\n\n"
            f"CONTEXTO REAL DO SETOR:\n{contexto_real}"
        )
    }

    for msg in st.session_state.historico[setor]:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Digite sua mensagem para o especialista..."):
        st.session_state.historico[setor].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
            
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
                    temperature=0.2
                )
                resposta_ia = completions.choices[0].message.content
            except Exception as e:
                resposta_ia = f"💥 Erro na resposta da IA: {e}"
        
        st.session_state.historico[setor].append({"role": "assistant", "content": resposta_ia})
        with st.chat_message("assistant"): st.write(resposta_ia)
