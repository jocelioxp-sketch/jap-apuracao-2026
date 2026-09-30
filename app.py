import time
import base64
from io import BytesIO
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st
from config import REFRESH_SECONDS, MAX_CANDIDATES, OFFICES
from tse_client import TSEClient

st.set_page_config(page_title="JAP • Apuração 2026",page_icon="📊",layout="wide")
st.markdown("""<style>
.block-container{padding-top:1rem;max-width:1600px}
.jap-card{border:1px solid rgba(128,128,128,.25);border-radius:18px;padding:16px;min-height:250px}
div[data-testid="stMetric"]{border:1px solid rgba(128,128,128,.18);border-radius:12px;padding:10px}
</style>""",unsafe_allow_html=True)

logo=Path("assets/jap_logo.jpeg")
if logo.exists(): st.image(str(logo),width=330)
else: st.title("GRUPO JAP"); st.caption("Tecnologia & Inovação")
st.header("Apuração Eleições 2026")
demo_guto = st.query_params.get("demo","") == "guto"
if demo_guto:
    st.warning("MODO DEMONSTRAÇÃO • Os dados abaixo são fictícios e servem apenas para apresentar como será a apuração.")

st.caption("Acompanhamento eleitoral com dados oficiais do TSE.")

if "tracked" not in st.session_state: st.session_state.tracked=[]
if "viewer_name" not in st.session_state: st.session_state.viewer_name=""

with st.sidebar:
    st.header("Meu painel")
    st.session_state.viewer_name=st.text_input("Seu nome",value=st.session_state.viewer_name,placeholder="Digite seu nome")
    uf=st.selectbox("UF",["SP","AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SE","TO"])
    office_name=st.selectbox("Cargo",["Deputado Federal","Deputado Estadual","Deputado Distrital"])
    number=st.text_input("Número do candidato",max_chars=5,placeholder="Ex.: 2220")
    if st.button("Adicionar candidato",type="primary",use_container_width=True):
        if not number.strip().isdigit(): st.error("Informe somente o número do candidato.")
        elif len(st.session_state.tracked)>=MAX_CANDIDATES: st.error("O painel aceita até 4 candidatos.")
        else:
            item={"uf":uf,"office_name":office_name,"office":OFFICES[office_name],"number":number.strip()}
            if item not in st.session_state.tracked: st.session_state.tracked.append(item); st.rerun()
    if st.session_state.tracked:
        st.caption(f"{len(st.session_state.tracked)}/4 candidatos")
        if st.button("Limpar candidatos",use_container_width=True): st.session_state.tracked=[]; st.rerun()
    mode_label=st.radio("Fonte",["Oficial 2026","Simulado TSE"],index=0)
    mode="official" if mode_label.startswith("Oficial") else "simulation"
    auto=st.toggle("Atualização automática",value=True)
    st.divider()
    demo_guto=st.toggle("DEMO • Guto José",value=False,help="Exibe dados fictícios apenas para demonstração visual.")

client=TSEClient(mode)

@st.cache_data(ttl=REFRESH_SECONDS,show_spinner=False)
def get_scope(mode,uf,office):
    c=TSEClient(mode)
    scope="br" if str(office)=="1" else uf.lower()
    return c.fetch_result("br" if str(office)=="1" else uf,scope,office)

def get_candidate(item):
    try:
        p=get_scope(mode,item["uf"],item["office"])
        return client.find(p,item["number"])
    except: return None

if demo_guto:
    st.error("DEMONSTRAÇÃO — DADOS SIMULADOS. Os números abaixo não representam resultado eleitoral real.")
    st.session_state.viewer_name = "Demonstração JAP"
    demo_item={"uf":"SP","office_name":"Deputado Estadual","office":"7","number":"20620"}
    st.subheader("GUTO JOSÉ")
    st.caption("20620 • Deputado Estadual • SP")
    d1,d2,d3,d4=st.columns(4)
    d1.metric("Votos simulados","80.000")
    d2.metric("Apuração simulada","98,7%")
    d3.metric("UF","SP")
    d4.metric("Situação","Demonstração")
    st.progress(0.987,text="98,7% da apuração simulada")
    st.caption("No dia da eleição, este bloco será alimentado pelos arquivos oficiais do TSE.")

if st.session_state.viewer_name:
    st.write(f"Painel de **{st.session_state.viewer_name}**")

if demo_guto:
    st.subheader("Demonstração • Deputado Estadual/SP")
    demo_cols=st.columns(4)
    with demo_cols[0]:
        st.image("guto_demo.JPG", use_container_width=True)
        st.subheader("GUTO JOSÉ")
        st.caption("20620 • Deputado Estadual • SP")
        st.metric("Votos", "80.000")
        st.metric("Seções totalizadas", "99,2%")
        st.progress(0.992)
    st.caption("SIMULAÇÃO: 80.000 votos e 99,2% de totalização são números fictícios usados exclusivamente para demonstração.")
    st.subheader("Exemplo de detalhamento municipal")
    demo_df=pd.DataFrame([
        {"Município":"Carapicuíba","Votos":32000},
        {"Município":"São Paulo","Votos":18000},
        {"Município":"Osasco","Votos":11000},
        {"Município":"Barueri","Votos":7000},
        {"Município":"Cotia","Votos":5000},
        {"Município":"Outros municípios","Votos":7000},
    ])
    st.dataframe(demo_df,use_container_width=True,hide_index=True)
elif not st.session_state.tracked:
    st.info("Adicione de 1 a 4 candidatos no menu lateral para montar seu painel.")
else:
    cols=st.columns(4)
    for i,col in enumerate(cols):
        with col:
            if i<len(st.session_state.tracked):
                item=st.session_state.tracked[i]; r=get_candidate(item)
                if r:
                    photo=client.photo_url(item["uf"],r["sqcand"],item["office"])
                    if photo:
                        try: st.image(photo,use_container_width=True)
                        except: pass
                    st.subheader(r["name"] or f'Candidato {item["number"]}')
                    st.caption(f'{item["number"]} • {item["office_name"]} • {item["uf"]}')
                    st.metric("Votos",f'{r["votes"]:,}'.replace(",","."))
                    if r.get("pct") not in ("",None): st.metric("%",str(r["pct"]))
                else:
                    st.subheader(f'Candidato {item["number"]}')
                    st.caption(f'{item["office_name"]} • {item["uf"]}')
                    st.metric("Votos","—"); st.caption("Aguardando resultado do TSE.")
                if st.button("Remover",key=f"rm{i}",use_container_width=True):
                    st.session_state.tracked.pop(i);st.rerun()

st.divider()
st.header("Acompanhamento incluído")
base_uf=st.session_state.tracked[0]["uf"] if st.session_state.tracked else uf

def election_table(title,uf,office):
    st.subheader(title)
    try:
        p=get_scope(mode,uf,office); data=client.candidates(p)
        if data:
            df=pd.DataFrame(data)[["name","number","votes","pct"]].rename(columns={"name":"Candidato","number":"Número","votes":"Votos","pct":"%"})
            st.dataframe(df,use_container_width=True,hide_index=True)
        else: st.info("Aguardando dados.")
    except: st.info("Aguardando disponibilização pelo TSE.")

c1,c2=st.columns(2)
with c1: election_table("Presidente • Brasil","BR",OFFICES["Presidente"])
with c2: election_table(f"Governador • {base_uf}",base_uf,OFFICES["Governador"])
st.divider()
election_table(f"Senado • {base_uf} — duas vagas",base_uf,OFFICES["Senador"])

st.caption("Fonte: Tribunal Superior Eleitoral (TSE). O painel público não atribui resultados eleitorais à atuação da JAP.")
st.caption(f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
if auto:
    time.sleep(REFRESH_SECONDS);st.rerun()
