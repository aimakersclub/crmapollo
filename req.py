import requests
import json

def enviar_lead_crm():
    # URL da API
    url = "https://api.crmapollo.com.br/webhooks/leads/create.php"
    
    # Parâmetros da URL
    params = {
        'url': 'BRU',
        'user': 'Ng==',
        'pipeline': '0',
        'token': 'e106ef63d791eec2df9bfc4ab17d9f500a246fcf64dbac598da9ff231597232e'
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Dados do lead
    data = {
        "nome": "Nao é o Jim Lovellll",
        "email": "jim.lovell@uol.com.br",
        "celular": "+555591626113",
        "cpf_ou_cnpj": "123.456.789-58",
        "classificacao1": "Imóveis 400k e Parcela 1500",
        "classificacao2": "Aluguel 1200 e financiamento",
        "classificacao3": "Lead de publicidade BOT",
        "obs": "Espaço reservado para perguntas e respostas realizadas com bot ou interações com chat.",
        "platform": "Google"
    }
    
    try:
        # Fazer a requisição POST
        response = requests.post(
            url,
            params=params,
            headers=headers,
            json=data  # Automaticamente converte para JSON e define Content-Type
        )
        
        # Verificar se a requisição foi bem-sucedida
        response.raise_for_status()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Se a resposta for JSON, pode decodificar
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        except:
            print("Resposta não é um JSON válido")
            
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

def enviar_lead_personalizado(nome, email, celular, cpf_cnpj=None, 
                            classificacao1=None, classificacao2=None, 
                            classificacao3=None, obs=None, platform="Google"):
    """
    Função para enviar leads personalizados
    """
    url = "https://api.crmapollo.com.br/webhooks/leads/create.php"
    
    params = {
        'url': 'BRU',
        'user': 'Ng==',
        'pipeline': '0',
        'token': 'e106ef63d791eec2df9bfc4ab17d9f500a246fcf64dbac598da9ff231597232e'
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Dados obrigatórios
    data = {
        "nome": nome,
        "email": email,
        "celular": celular,
        "platform": platform
    }
    
    # Adicionar campos opcionais se fornecidos
    if cpf_cnpj:
        data["cpf_ou_cnpj"] = cpf_cnpj
    if classificacao1:
        data["classificacao1"] = classificacao1
    if classificacao2:
        data["classificacao2"] = classificacao2
    if classificacao3:
        data["classificacao3"] = classificacao3
    if obs:
        data["obs"] = obs
    
    try:
        response = requests.post(url, params=params, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"Lead enviado com sucesso! Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar lead: {e}")
        return None

# Executar a função
if __name__ == "__main__":
    print("Enviando lead para CRM Apollo...")
    resultado = enviar_lead_crm()
    
    if resultado:
        print("✅ Requisição enviada com sucesso!")
    else:
        print("❌ Falha ao enviar requisição")
    
    print("\n" + "="*50 + "\n")
    
    # Exemplo de uso da função personalizada
    print("Exemplo de envio personalizado:")
    enviar_lead_personalizado(
        nome="Maria Silva",
        email="maria.silva@gmail.com",
        celular="+5511987654321",
        cpf_cnpj="987.654.321-00",
        classificacao1="Lead Premium",
        obs="Cliente interessado em imóvel de alto padrão"
    )
