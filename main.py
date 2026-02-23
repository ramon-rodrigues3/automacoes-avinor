from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import requests
import bitrix

app = FastAPI()

@app.post("/validar-cadastro")
async def validar_cadastro(id: str):
    try:
        card = bitrix.deal_get(id)
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Erro HTTP ao conectar com Bitrix24: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Erro de conexão ao Bitrix24: {err}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao Bitrix24: {err}")
    
    etapa = card.get('STAGE_ID')
    id_empresa = card.get('COMPANY_ID')

    if not id_empresa:
        return JSONResponse(
            {
                "error": {
                    "code": "MISSING_REQUIRED_FIELD",
                    "message": "O negócio não possui código da empresa.",
                }
            }, 
            status_code=400
        )

    if etapa != "C4:WON":
        return JSONResponse(
            {
                "error": {
                    "code": "UNEXPECTED_COLUMN",
                    "message": "O negócio não está na coluna esperada.",
                }
            }, 
            status_code=400
        )
    
    equivalentes = bitrix.deal_list({"CATEGORY_ID": "2", "=COMPANY_ID": id_empresa, "STAGE_ID": "C2:EXECUTING"}, [])

    if not equivalentes:
        return JSONResponse(
            {
                "error": {
                    "code": "PARTIAL_SUCESS",
                    "message": "O negócio foi processado, mas não foi encontrado um equivalente",
                }
            }, 
            status_code=200
        )
    
    equivalente = equivalentes[0]
    equivalente_id = equivalente.get('ID')

    bitrix.deal_update(equivalente_id, 
        {
            "STAGE_ID": "C2:UC_P7EWZH"
        }
    )

    return JSONResponse(
        {
            "status": "success",
            "message": "O negócio equivalente foi atualizado com sucesso.",
        },
        status_code=200
    )

@app.post("/reprovar-cadastro")
async def reprovar_cadastro(id: str):
    try:
        card = bitrix.deal_get(id)
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=500, detail=f"Erro HTTP ao conectar com Bitrix24: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Erro de conexão ao Bitrix24: {err}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao Bitrix24: {err}")
    
    etapa = card.get('STAGE_ID')
    id_empresa = card.get('COMPANY_ID')
    motivo = card.get('UF_CRM_1771605448121')
    if not id_empresa:
        return JSONResponse(
            {
                "error": {
                    "code": "MISSING_REQUIRED_FIELD",
                    "message": "O negócio não possui código da empresa.",
                }
            }, 
            status_code=400
        )

    if etapa != "C4:LOSE":
        return JSONResponse(
            {
                "error": {
                    "code": "UNEXPECTED_COLUMN",
                    "message": "O negócio não está na coluna esperada.",
                }
            }, 
            status_code=400
        )
    
    equivalentes = bitrix.deal_list({"CATEGORY_ID": "2", "=COMPANY_ID": id_empresa, "STAGE_ID": "C2:EXECUTING"}, [])

    if not equivalentes:
        return JSONResponse(
            {
                "error": {
                    "code": "PARTIAL_SUCESS",
                    "message": "O negócio foi processado, mas não foi encontrado um equivalente",
                }
            }, 
            status_code=200
        )
    
    equivalente = equivalentes[0]
    equivalente_id = equivalente.get('ID')

    bitrix.deal_update(equivalente_id, 
        {
            "STAGE_ID": "C2:LOSE",
            "UF_CRM_1771605448121": motivo
        }
    )

    return JSONResponse(
        {
            "status": "success",
            "message": "O negócio equivalente foi atualizado com sucesso.",
        },
        status_code=200
    )