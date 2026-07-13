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
        div.stButton > button:first-child {
            background-color: #8B2635 !important;
            color: white !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            width: 100% !important;
            height: 48px !important;
            margin-top: 15px;
        }
        div.stButton > button:first-child:hover { background-color: #6B1D29 !important; }
    </style>
""", unsafe_allow_html=True)

api_key = os.getenv("OPENAI_API_KEY")

# Banco de dados de usuários atualizado com os novos perfis solicitados
USUARIOS = {
    # Perfis Operacionais de Setor Único
    "licitacao_user": {"senha": "cro_lic_2026", "setor": "Licitações e Contratos", "tipo": "restrito"},
    "atos_user": {"senha": "cro_ato_2026", "setor": "Atos Normativos", "tipo": "restrito"},
    "comunicacao_user": {"senha": "cro_com_2026", "setor": "Comunicação Institucional", "tipo": "restrito"},
    
    # Novos Perfis Estratégicos com Acesso Amplo
    "assessoria_gerencial": {"senha": "cro_ger_2026", "setor": "Todos", "tipo": "global"},
    "secretaria_executiva": {"senha": "cro_exec_2026", "setor": "Todos", "tipo": "global"}
}

if "logado" not in st.session_state:
    st.session_state.logado = False
if "setor" not in st.session_state:
    st.session_state.setor = None
if "perfil_nome" not in st.session_state:
    st.session_state.perfil_nome = None
if "historico" not in st.session_state:
    st.session_state.historico = {}

if not st.session_state.logado:
    st.markdown("<div class='main-header'>🏛️ CONSELHO REGIONAL DE ODONTOLOGIA</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>MINAS GERAIS</div>", unsafe_allow_html=True)
    st.markdown("<div class='system-badge'>Sistema Interno de Inteligência Artificial Avançada</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 5, 1])
    
    with col2:
        with st.container(border=True):
            st.write("") 
            
            setor_selecionado = st.selectbox(
                "Selecione o Setor que deseja acessar nesta sessão:", 
                ["Licitações e Contratos", "Atos Normativos", "Comunicação Institucional"]
            )
            
            usuario_input = st.text_input("Usuário / E-mail do Servidor:")
            senha_input = st.text_input("Senha de Acesso:", type="password")
            
            if st.button("AUTENTICAR NO SISTEMA"):
                if usuario_input in USUARIOS and USUARIOS[usuario_input]["senha"] == senha_input:
                    dados_user = USUARIOS[usuario_input]
                    
                    # Validação: Se for global, deixa passar para o setor escolhido. Se for restrito, exige o setor correto.
                    if dados_user["tipo"] == "global" or dados_user["setor"] == setor_selecionado:
                        st.session_state.logado = True
                        st.session_state.setor = setor_selecionado
                        st.session_state.perfil_nome = usuario_input.replace("_", " ").title()
                        if setor_selecionado not in st.session_state.historico:
                            st.session_state.historico[setor_selecionado] = []
                        st.rerun()
                    else:
                        st.error(f"❌ O seu usuário está restrito ao departamento de {dados_user['setor']}.")
                else:
                    st.error("❌ Credenciais inválidas. Tente novamente.")

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
        st.markdown("---")
        st.markdown("### ⏳ Consultas do Setor")
        for idx, msg in enumerate(st.session_state.historico[setor]):
            if msg["role"] == "user":
                st.text(f"💬 Q{idx+1}: {msg['content'][:25]}...")

    st.markdown(f"<h2>💼 Painel Operacional: {setor}</h2>", unsafe_allow_html=True)
    st.markdown("---")

    prompts_setores = {
        "Licitações e Contratos": "Você é o Assistente Jurídico Especialista no setor de Licitações e Contratos do CRO MG. Baseie-se nos documentos de 2026. Atue em ESCREVER, REVISAR ou CONSULTAR no tom oficial.",
        "Atos Normativos": "Você é o Consultor Legislativo especialista em Atos Normativos do CRO MG. Baseie-se nas portarias, resoluções e decisões de 2026. Atue em ESCREVER, REVISAR ou CONSULTAR no padrão do conselho.",
        "Comunicação Institucional": "Você é o Diretor de Comunicação e Copywriter Sênior do CRO MG. Ofereça os serviços de CALENDÁRIO DE PUBLICAÇÃO, CRIAR CAMPANHA ou DESENVOLVER COPY de acordo com a linguagem do conselho em 2026."
    }

    if setor == "Licitações e Contratos":
        st.markdown("💡 *Funções disponíveis: **Escrever** (minutas/contratos), **Revisar** (auditoria legal) ou **Consultar** (valores/prazos).*")
    elif setor == "Atos Normativos":
        st.markdown("💡 *Funções disponíveis: **Escrever** (portarias/resoluções), **Revisar** (redação oficial) ou **Consultar** (vigências/precedentes).*")
    elif setor == "Comunicação Institucional":
        st.markdown("💡 *Funções disponíveis: **Calendário de Publicação**, **Criar Campanha** ou **Desenvolver Copy**.*")

    for msg in st.session_state.historico[setor]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Digite sua instrução para a IA do conselho..."):
        st.session_state.historico[setor].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
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
                    temperature=0.3
                )
                resposta_ia = completions.choices[0].message.content
            except Exception as e:
                resposta_ia = f"💥 Erro na resposta da IA: {e}"
        
        st.session_state.historico[setor].append({"role": "assistant", "content": resposta_ia})
        with st.chat_message("assistant"):
            st.write(resposta_ia)
