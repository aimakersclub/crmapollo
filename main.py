from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import requests
import json
from datetime import datetime

# Inicializar FastAPI
app = FastAPI(
    title="CRM Apollo API",
    description="API para envio de leads para o CRM Apollo",
    version="1.0.0"
)

# Modelos Pydantic para validação de dados
class CRMCredentials(BaseModel):
    """Credenciais para autenticação no CRM Apollo"""
    url: str = Field(..., description="URL identifier (ex: BRU)")
    user: str = Field(..., description="User identifier (ex: Ng==)")
    pipeline: str = Field(..., description="Pipeline ID (ex: 0)")
    token: str = Field(..., description="Token de autenticação")

class LeadData(BaseModel):
    """Dados do lead a ser enviado"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome completo do lead")
    email: EmailStr = Field(..., description="Email válido do lead")
    celular: str = Field(..., min_length=10, description="Número de celular com código do país")
    cpf_ou_cnpj: Optional[str] = Field(None, description="CPF ou CNPJ do lead")
    classificacao1: Optional[str] = Field(None, description="Primeira classificação")
    classificacao2: Optional[str] = Field(None, description="Segunda classificação")
    classificacao3: Optional[str] = Field(None, description="Terceira classificação")
    obs: Optional[str] = Field(None, description="Observações sobre o lead")
    platform: str = Field(default="API", description="Plataforma de origem do lead")

class LeadRequest(BaseModel):
    """Request completo com credenciais e dados do lead"""
    credentials: CRMCredentials
    lead_data: LeadData

class APIResponse(BaseModel):
    """Modelo de resposta da API"""
    success: bool
    message: str
    status_code: Optional[int] = None
    crm_response: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Endpoints da API

@app.get("/", response_model=dict)
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "CRM Apollo API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=dict)
async def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "CRM Apollo API"
    }

@app.post("/send-lead", response_model=APIResponse)
async def send_lead_to_crm(request: LeadRequest):
    """
    Envia um lead para o CRM Apollo
    """
    try:
        # URL da API do CRM Apollo
        crm_url = "https://api.crmapollo.com.br/webhooks/leads/create.php"
        
        # Parâmetros da URL
        params = {
            'url': request.credentials.url,
            'user': request.credentials.user,
            'pipeline': request.credentials.pipeline,
            'token': request.credentials.token
        }
        
        # Headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'CRM-Apollo-API/1.0.0'
        }
        
        # Converter dados do lead para dict
        lead_dict = request.lead_data.dict(exclude_none=True)
        
        # Fazer a requisição POST
        response = requests.post(
            crm_url,
            params=params,
            headers=headers,
            json=lead_dict,
            timeout=30  # Timeout de 30 segundos
        )
        
        # Verificar se a requisição foi bem-sucedida
        response.raise_for_status()
        
        # Tentar decodificar resposta como JSON
        try:
            crm_response_data = response.json()
        except json.JSONDecodeError:
            crm_response_data = {"raw_response": response.text}
        
        return APIResponse(
            success=True,
            message=f"Lead enviado com sucesso para o CRM Apollo",
            status_code=response.status_code,
            crm_response=crm_response_data
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Timeout ao conectar com CRM Apollo"
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erro de conexão com CRM Apollo"
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Erro HTTP do CRM Apollo: {e.response.status_code} - {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@app.post("/send-lead-simple", response_model=APIResponse)
async def send_lead_simple(
    # Credenciais como query parameters
    url: str,
    user: str,
    pipeline: str,
    token: str,
    # Dados do lead no body
    lead_data: LeadData
):
    """
    Endpoint simplificado - credenciais via query parameters e dados do lead no body
    """
    # Criar objeto de credenciais
    credentials = CRMCredentials(
        url=url,
        user=user,
        pipeline=pipeline,
        token=token
    )
    
    # Criar request completo
    request = LeadRequest(
        credentials=credentials,
        lead_data=lead_data
    )
    
    # Chamar a função principal
    return await send_lead_to_crm(request)

# Endpoint para testar com dados de exemplo
@app.post("/test-lead", response_model=APIResponse)
async def test_lead():
    """
    Endpoint para teste com dados de exemplo
    """
    test_request = LeadRequest(
        credentials=CRMCredentials(
            url="BRU",
            user="Ng==",
            pipeline="0",
            token="e106ef63d791eec2df9bfc4ab17d9f500a246fcf64dbac598da9ff231597232e"
        ),
        lead_data=LeadData(
            nome="Teste API",
            email="teste@api.com",
            celular="+5511999999999",
            cpf_ou_cnpj="123.456.789-00",
            classificacao1="Lead de Teste",
            obs="Lead criado para teste da API",
            platform="API-Test"
        )
    )
    
    return await send_lead_to_crm(test_request)

# Middleware para CORS (se necessário)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
