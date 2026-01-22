import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Configuração da Página
st.set_page_config(page_title="Comparador Vimacedo", layout="wide")
st.title("🔍 Comparador de Preços Vimacedo")

# Função para fazer o Scraping do site
@st.cache_data(ttl=3600) # Guarda os dados por 1 hora para ser rápido
def extrair_dados_vimacedo():
    options = Options()
    options.add_argument("--headless") # Roda sem abrir a janela do navegador
    driver = webdriver.Chrome(options=options)
    
    url = "https://vimacedo.com.br/tabela-de-precos/"
    driver.get(url)
    time.sleep(5) # Tempo para a tabela carregar
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    # Aqui buscamos a tabela específica no HTML do site
    produtos = []
    tabela = soup.find('table') # Ajustar o seletor conforme a estrutura real
    
    if tabela:
        for linha in tabela.find_all('tr')[1:]: # Pula o cabeçalho
            cols = linha.find_all('td')
            if len(cols) >= 3:
                produtos.append({
                    "Código": cols[0].text.strip(),
                    "Descrição": cols[1].text.strip(),
                    "Peso/Embalagem": cols[2].text.strip()
                })
    return pd.DataFrame(produtos)

# --- INTERFACE DO SITE ---

upload = st.file_uploader("Suba sua lista de códigos (Excel ou CSV)", type=['csv', 'xlsx'])

if upload:
    # Carrega lista do usuário
    if upload.name.endswith('.csv'):
        df_usuario = pd.read_csv(upload)
    else:
        df_usuario = pd.read_excel(upload)
    
    # Coluna de código deve se chamar 'Código'
    lista_codigos = df_usuario['Código'].astype(str).tolist()
    
    with st.spinner('Consultando site da Vimacedo...'):
        df_site = extrair_dados_vimacedo()
    
    # Lógica de Comparação
    resultado = []
    for codigo in lista_codigos:
        match = df_site[df_site['Código'] == codigo]
        
        if not match.empty:
            item = match.iloc[0].to_dict()
            item['Status'] = 'Encontrado'
            resultado.append(item)
        else:
            resultado.append({
                "Código": codigo,
                "Descrição": "NÃO LOCALIZADO NO SITE",
                "Peso/Embalagem": "-",
                "Status": "Não Encontrado"
            })
    
    df_final = pd.DataFrame(resultado)

    # Função para colorir a tabela
    def style_rows(row):
        if row['Status'] == 'Encontrado':
            return ['background-color: #d4edda; color: #155724'] * len(row) # Verde
        else:
            return ['background-color: #f8d7da; color: #721c24'] * len(row) # Vermelho

    st.subheader("Resultado da Comparação")
    st.dataframe(df_final.style.apply(style_rows, axis=1), use_container_width=True)