def extrair_dados_vimacedo():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Adicionamos o Service para garantir que ele encontre o driver instalado pelo packages.txt
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.core.os_manager import ChromeType

    try:
        # Tenta usar o driver do sistema (instalado via packages.txt)
        driver = webdriver.Chrome(options=options)
    except:
        # Fallback caso precise baixar manualmente (mais lento)
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
            options=options
        )
    
    url = "https://vimacedo.com.br/tabela-de-precos/"
    driver.get(url)
    time.sleep(8) # Aumentei um pouco para garantir o carregamento em servidores lentos
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    # Restante da lógica da tabela...
    produtos = []
    # O site da Vimacedo usa uma tabela dentro de um iframe ou div específica. 
    # Vou sugerir uma busca mais ampla por <tr>:
    linhas = soup.find_all('tr')
    
    for linha in linhas:
        cols = linha.find_all('td')
        if len(cols) >= 3:
            produtos.append({
                "Código": cols[0].text.strip(),
                "Descrição": cols[1].text.strip(),
                "Peso/Embalagem": cols[2].text.strip()
            })
            
    return pd.DataFrame(produtos)
