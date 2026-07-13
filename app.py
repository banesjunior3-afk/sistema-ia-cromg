import streamlit as st
import os
from openai import OpenAI

# Configuração da Página
st.set_page_config(page_title="Sistema IA - CRO MG", page_icon="🏛️", layout="centered")

# Injeção de CSS para espelhar a identidade visual do CRO-MG
st.markdown("""
    <style>
        .stApp { background-color: #F8F9FA; }
        .login-box {
            background-color: #FFFFFF;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            border-top: 5px solid #8B2635;
        }
        div.stButton > button:first-child {
            background-color: #8B2635 !important;
            color: white !important;
            border-radius: 4px !important;
            border: none !important;
            font-weight: bold !important;
            width: 100% !important;
            height: 45px !important;
        }
        div.stButton > button:first-child:hover { background-color: #6B1D29 !important; }
        h1, h2, h3 { color: #8B2635 !important; font-family: 'Helvetica Neue', Arial, sans-serif; text-align: center; }
        .subtitle { text-align: center; color: #555555; font-size: 14px; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# Recupera a API Key das Variáveis de Ambiente do Railway
api_key = os.getenv("OPENAI_API_KEY")

# Banco de dados de usuários embutido
USUARIOS = {
    "licitacao_user": {"senha": "cro_lic_2026", "setor": "Licitações e Contratos"},
    "atos_user": {"senha": "cro_ato_2026", "setor": "Atos Normativos"},
    "comunicacao_user": {"senha": "cro_com_2026", "setor": "Comunicação Institucional"}
}

if "logado" not in st.session_state:
    st.session_state.logado = False
if "setor" not in st.session_state:
    st.session_state.setor = None
if "historico" not in st.session_state:
    st.session_state.historico = {}

# ----------------------------------------------------
# TELA DE LOGIN
# ----------------------------------------------------
if not st.session_state.logado:
    st.markdown("<h1>🏛️ CONSELHO REGIONAL DE ODONTOLOGIA</h1>", unsafe_allow_html=True)
    st.markdown("<h3>MINAS GERAIS</h3>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Sistema Interno de Inteligência Artificial Avançada</p>", unsafe_allow_html=True)
    
    st.image("https://www.cromg.org.br/wp-content/themes/cro-mg-theme/assets/images/logo.png", width=180)
    
    with st.container():
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        setor_selecionado = st.selectbox("Selecione o seu Setor de Atuação:", list(set(u['setor'] for u in USUARIOS.values())))
        usuario_input = st.text_input("Usuário / E-mail do Servidor:")
        senha_input = st.text_input("Senha de Acesso:", type="password")
        
        if st.button("AUTENTICAR NO SISTEMA"):
            if usuario_input in USUARIOS and USUARIOS[usuario_input]["senha"] == senha_input:
                if USUARIOS[usuario_input]["setor"] == setor_selecionado:
                    st.session_state.logado = True
                    st.session_state.setor = setor_selecionado
                    if setor_selecionado not in st.session_state.historico:
                        st.session_state.historico[setor_selecionado] = []
                    st.rerun()
                else:
                    st.error("❌ O usuário informado não pertence a este setor.")
            else:
                st.error("❌ Credenciais inválidas.")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# AMBIENTE OPERACIONAL (PÓS-LOGIN)
# ----------------------------------------------------
else:
    setor = st.session_state.setor
    
    with st.sidebar:
        st.markdown(f"### 👤 Servidor Autenticado")
        st.info(f"**Setor:** {setor}\n**Escopo:** Transparência 2026")
        if st.button("Efetuar Logout"):
            st.session_state.logado = False
            st.session_state.setor = None
            st.rerun()
        st.markdown("---")
        st.markdown("### ⏳ Histórico de Consultas")
        for idx, msg in enumerate(st.session_state.historico[setor]):
            if msg["role"] == "user":
                st.text(f"💬 Q{idx+1}: {msg['content'][:25]}...")

    st.markdown(f"<h2>💼 Painel Operacional: {setor}</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # Definição das Personas e Instruções do Sistema com base nas validações anteriores
    prompts_setores = {
        "Licitações e Contratos": "Você é o Assistente Jurídico Especialista no setor de Licitações e Contratos do CRO MG. Sua base de conhecimento e parâmetros estilísticos espelham estritamente os documentos de 2026. Responda sob as óticas de ESCREVER, REVISAR ou CONSULTAR mantendo a identidade humana dos documentos do conselho.",
        "Atos Normativos": "Você é o Consultor Legislativo especialista em Atos Normativos do CRO MG. Baseie-se apenas em portarias, resoluções e decisões de 2026. Atue em ESCREVER, REVISAR ou CONSULTAR seguindo estritamente a padronização oficial do conselho.",
        "Comunicação Institucional": "Você é o Diretor de Comunicação e Copywriter Sênior do CRO MG. Seu tom é informativo, preventivo e sério. Ofereça os serviços de CALENDÁRIO DE PUBLICAÇÃO, CRIAR CAMPANHA ou DESENVOLVER COPY de acordo com a identidade do conselho de 2026."
    }

    # Exibição do chat na tela
    for msg in st.session_state.historico[setor]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Digite o comando..."):
        st.session_state.historico[setor].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        if not api_key:
            resposta_ia = "⚠️ Erro: A chave OPENAI_API_KEY não foi configurada nas variáveis de ambiente do Railway."
        else:
            try:
                client = OpenAI(api_key=api_key)
                # Constrói o histórico formatado para enviar à API
                mensagens_api = [{"role": "system", "content": prompts_setores[setor]}]
                for msg in st.session_state.historico[setor]:
                    mensagens_api.append({"role": msg["role"], "content": msg["content"]})
                
                completions = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=mensagens_api,
                    temperature=0.3
                )
                resposta_ia = completions.choices[0].message.content
            except Exception as e:
                resposta_ia = f"💥 Erro na chamada da OpenAI: {e}"
        
        st.session_state.historico[setor].append({"role": "assistant", "content": resposta_ia})
        with st.chat_message("assistant"):
            st.write(resposta_ia)
