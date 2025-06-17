import streamlit as st
import pandas as pd
import io
# import psycopg2 # Removido, não é mais necessário
from datetime import datetime
import time
import requests
import json

# --- Configuração da API Thorpe (Extrema - EX) ---
TOKEN_URL_THORPE_EX = 'https://apiextrema.thorpe.com.br/v2/token'
API_PEDIDOS_BASE_URL_THORPE_EX = 'http://apiextrema.thorpe.com.br/v2/pedidos/'
AUTH_PAYLOAD_THORPE_EX = { "usuario": "intengage", "senha": "QE2S0w2o" }
TOKEN_HEADERS_THORPE = { 'Content-Type': 'application/json' }

# --- Configuração da API Thorpe (Espírito Santo - ES) ---
TOKEN_URL_THORPE_ES = 'https://apies.thorpe.com.br/v2/token'
API_PEDIDOS_BASE_URL_THORPE_ES = 'https://apies.thorpe.com.br/v2/pedidos/'
AUTH_PAYLOAD_THORPE_ES = { "usuario": "intengagees", "senha": "QE2S0w2o" }

# --- NOVA CONFIGURAÇÃO DA API CONTROLADORIA ---
API_CONTROLADORIA_URL = "http://209.14.71.180:3000/controladoria-rafael"
API_CONTROLADORIA_HEADERS = {
    'Authorization': 'Bearer engage@secure2024',
    'Content-Type': 'application/json'
}

# --- Funções Auxiliares da API Thorpe (Extrema - EX) ---
def obter_token_thorpe_ex():
    try:
        response = requests.post(TOKEN_URL_THORPE_EX, headers=TOKEN_HEADERS_THORPE, json=AUTH_PAYLOAD_THORPE_EX, timeout=15)
        response.raise_for_status()
        token_data = response.json(); token = token_data.get('token')
        if not token: st.error("(API Thorpe-EX) Token não encontrado na resposta."); return None
        return token
    except requests.exceptions.RequestException as e: st.error(f"(API Thorpe-EX) Erro ao obter token: {e}"); return None
    except json.JSONDecodeError as e_json:
        error_text = response.text if 'response' in locals() and hasattr(response, 'text') else "---"
        st.error(f"(API Thorpe-EX) Erro JSON (token): {error_text} ({e_json})"); return None

@st.cache_data(ttl=600)
def obter_token_thorpe_ex_cached():
    st.info("(API Thorpe-EX) Obtendo token de autenticação...")
    token = obter_token_thorpe_ex()
    if token: st.success("(API Thorpe-EX) Token obtido!")
    else: st.error("(API Thorpe-EX) Falha ao obter token.")
    return token

def consultar_pedido_thorpe_ex(token, numero_pedido_original_api):
    if not token: return None
    url_pedido = f"{API_PEDIDOS_BASE_URL_THORPE_EX}{numero_pedido_original_api}"
    headers_pedido = { 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json' }
    response_obj = None
    try:
        response_obj = requests.get(url_pedido, headers=headers_pedido, timeout=15)
        response_obj.raise_for_status(); return response_obj.json()
    except requests.exceptions.HTTPError as e:
        if response_obj is not None and response_obj.status_code == 404: return None
        error_text_response = response_obj.text if response_obj and hasattr(response_obj, 'text') else '---'
        error_message = f"(API Thorpe-EX) Erro HTTP pedido {numero_pedido_original_api}: {e}. Resp: {error_text_response}"
        if response_obj is not None and response_obj.status_code == 401:
            error_message = f"(API Thorpe-EX) Erro Auth (401) pedido {numero_pedido_original_api}. Token expirado?"
        st.warning(error_message); return None
    except requests.exceptions.RequestException as e: st.warning(f"(API Thorpe-EX) Erro requisição pedido {numero_pedido_original_api}: {e}"); return None
    except json.JSONDecodeError as e_json:
        error_text_response = response_obj.text if response_obj and hasattr(response_obj, 'text') else "---"
        st.warning(f"(API Thorpe-EX) Erro JSON pedido {numero_pedido_original_api}: {error_text_response} ({e_json})"); return None

# --- Funções Auxiliares da API Thorpe (Espírito Santo - ES) ---
def obter_token_thorpe_es():
    try:
        response = requests.post(TOKEN_URL_THORPE_ES, headers=TOKEN_HEADERS_THORPE, json=AUTH_PAYLOAD_THORPE_ES, timeout=15)
        response.raise_for_status()
        token_data = response.json(); token = token_data.get('token')
        if not token: st.error("(API Thorpe-ES) Token não encontrado na resposta."); return None
        return token
    except requests.exceptions.RequestException as e: st.error(f"(API Thorpe-ES) Erro ao obter token: {e}"); return None
    except json.JSONDecodeError as e_json:
        error_text = response.text if 'response' in locals() and hasattr(response, 'text') else "---"
        st.error(f"(API Thorpe-ES) Erro JSON (token): {error_text} ({e_json})"); return None

@st.cache_data(ttl=600)
def obter_token_thorpe_es_cached():
    st.info("(API Thorpe-ES) Obtendo token de autenticação...")
    token = obter_token_thorpe_es()
    if token: st.success("(API Thorpe-ES) Token obtido!")
    else: st.error("(API Thorpe-ES) Falha ao obter token.")
    return token

def consultar_pedido_thorpe_es(token, numero_pedido_original_api):
    if not token: return None
    url_pedido = f"{API_PEDIDOS_BASE_URL_THORPE_ES}{numero_pedido_original_api}"
    headers_pedido = { 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json' }
    response_obj = None
    try:
        response_obj = requests.get(url_pedido, headers=headers_pedido, timeout=15)
        response_obj.raise_for_status(); return response_obj.json()
    except requests.exceptions.HTTPError as e:
        if response_obj is not None and response_obj.status_code == 404: return None
        error_text_response = response_obj.text if response_obj and hasattr(response_obj, 'text') else '---'
        error_message = f"(API Thorpe-ES) Erro HTTP pedido {numero_pedido_original_api}: {e}. Resp: {error_text_response}"
        if response_obj is not None and response_obj.status_code == 401:
            error_message = f"(API Thorpe-ES) Erro Auth (401) pedido {numero_pedido_original_api}. Token expirado?"
        st.warning(error_message); return None
    except requests.exceptions.RequestException as e: st.warning(f"(API Thorpe-ES) Erro requisição pedido {numero_pedido_original_api}: {e}"); return None
    except json.JSONDecodeError as e_json:
        error_text_response = response_obj.text if response_obj and hasattr(response_obj, 'text') else "---"
        st.warning(f"(API Thorpe-ES) Erro JSON pedido {numero_pedido_original_api}: {error_text_response} ({e_json})"); return None

# --- Função Genérica para Extrair Status (usada por ambas APIs Thorpe) ---
def extrair_status_recente_thorpe_generico(dados_pedido_api, id_original_excel_para_api):
    status_base_default = "---"
    data_default = "---"

    status_atual = status_base_default
    data_atual = data_default

    if dados_pedido_api:
        eventos = []
        historico_status_lista = dados_pedido_api.get("historicoStatus", [])
        for item in historico_status_lista:
            if item.get("data") and item.get("status"):
                try: dt_obj = pd.to_datetime(item["data"]); eventos.append({"data_hora_obj": dt_obj, "status": item["status"]})
                except Exception: pass

        informacoes_rastreio_dict = dados_pedido_api.get("informacoesRastreio", {})
        rastreio_lista = informacoes_rastreio_dict.get("rastreio", [])
        for item in rastreio_lista:
            if item.get("dataHora") and item.get("status"):
                try: dt_obj = pd.to_datetime(item["dataHora"]); eventos.append({"data_hora_obj": dt_obj, "status": item["status"]})
                except Exception: pass
        
        if eventos:
            eventos.sort(key=lambda x: x["data_hora_obj"], reverse=True)
            evento_mais_recente = eventos[0]
            status_atual = evento_mais_recente['status']
            data_atual = evento_mais_recente["data_hora_obj"].strftime('%d/%m/%Y %H:%M:%S')
        else: 
            status_atual = "Sem eventos de status/rastreio utilizáveis na API Thorpe"
    
    return {
        "ID Original Excel": str(id_original_excel_para_api),
        "Status Base": status_atual, 
        "Data Status Base": data_atual
    }

# --- Função para Buscar Dados Combinados das APIs Thorpe ---
def buscar_dados_thorpe_combinado_api(lista_ids_originais_excel: list, token_ex_valido: str, token_es_valido: str):
    st.info(f"(API Thorpe Combinado) Consultando {len(lista_ids_originais_excel)} pedido(s)...")
    all_api_data = []
    api_status_message = st.empty()

    placeholder_not_found = "---" 
    status_sem_eventos = "Sem eventos de status/rastreio utilizáveis na API Thorpe"

    for i, pedido_id_original in enumerate(lista_ids_originais_excel):
        api_status_message.info(f"(API Thorpe Combinado) Processando pedido {i+1}/{len(lista_ids_originais_excel)}: {pedido_id_original}...")
        time.sleep(0.05) 

        status_final = placeholder_not_found
        data_status_final = placeholder_not_found
        dados_brutos_ex = None
        
        if token_ex_valido:
            dados_brutos_ex = consultar_pedido_thorpe_ex(token_ex_valido, pedido_id_original)
        
        info_ex_dict = extrair_status_recente_thorpe_generico(dados_brutos_ex, pedido_id_original)
        status_ex_base = info_ex_dict["Status Base"]
        data_ex_base = info_ex_dict["Data Status Base"]

        tentar_es = False
        if dados_brutos_ex is None or status_ex_base == placeholder_not_found or status_ex_base == status_sem_eventos:
            tentar_es = True

        if tentar_es:
            if token_es_valido:
                dados_brutos_es = consultar_pedido_thorpe_es(token_es_valido, pedido_id_original)
                info_es_dict = extrair_status_recente_thorpe_generico(dados_brutos_es, pedido_id_original)
                status_es_base = info_es_dict["Status Base"]
                data_es_base = info_es_dict["Data Status Base"]

                if status_es_base == placeholder_not_found:
                    status_final = placeholder_not_found 
                else: 
                    status_final = f"{status_es_base} - ES"
                data_status_final = data_es_base
            else: 
                if status_ex_base == placeholder_not_found:
                    status_final = placeholder_not_found
                else: 
                    status_final = f"{status_ex_base} - EX (ES indisponível)"
                data_status_final = data_ex_base
        else: 
            if status_ex_base == placeholder_not_found: 
                status_final = placeholder_not_found
            else:
                status_final = f"{status_ex_base} - EX"
            data_status_final = data_ex_base
            
        all_api_data.append({
            "ID Original Excel": str(pedido_id_original), 
            "Status Thorpe": status_final,
            "Data Status Thorpe": data_status_final
        })

    api_status_message.empty()
    if not all_api_data:
        st.warning("(API Thorpe Combinado) Nenhum dado das APIs Thorpe.")
        return pd.DataFrame(columns=["ID Original Excel", "Status Thorpe", "Data Status Thorpe"])

    df_api = pd.DataFrame(all_api_data)
    return df_api


def preparar_id_para_bd(pedido_id_excel):
    id_str = str(pedido_id_excel)
    id_sem_canc = id_str.replace('_CANC', '')
    id_final_para_bd = id_sem_canc
    if len(id_sem_canc) == 11:
        if id_sem_canc.endswith("01") or id_sem_canc.endswith("02") or id_sem_canc.endswith("03"):
            id_final_para_bd = id_sem_canc[:-2]
    return id_final_para_bd

st.set_page_config(page_title="Consulta de Pedidos", page_icon="🔍", layout="wide")
st.title("Consulta Massiva de Pedidos - Sysemp e Thorpe") 
st.markdown("""
Esta aplicação permite carregar um arquivo Excel com números de pedidos para buscar informações
no banco de dados Sysemp e nas APIs Thorpe, unindo os resultados em uma única tabela.
A consulta à API tentará a API Extrema (EX) e a API do Espírito Santo (ES).
O status final indicará a origem da informação (`- EX` ou `- ES`) caso um status específico seja encontrado.
**Instruções:**
1.  Prepare um arquivo Excel (`.xlsx` ou `.xls`).
2.  Na barra lateral, carregue o arquivo e selecione a coluna dos pedidos.
3.  Clique em "PROCESSAR CONSULTA".
* Os pedidos da Via Varejo precisam estar no modelo do portal, geralmente terminando em 01, 02 ou 03.
""") 
st.sidebar.header("Configurações da Consulta")
st.sidebar.subheader("1. Carregar Arquivo")
uploaded_file = st.sidebar.file_uploader("Escolha seu arquivo Excel:", type=["xlsx", "xls"], key="excel_uploader")
df_excel_carregado = None
coluna_de_pedidos_selecionada = None
if uploaded_file:
    try:
        st.sidebar.info(f"Arquivo '{uploaded_file.name}' carregado.")
        engine = 'openpyxl' if uploaded_file.name.endswith('xlsx') else 'xlrd'
        df_excel_carregado = pd.read_excel(uploaded_file, engine=engine)
        if df_excel_carregado is not None and not df_excel_carregado.empty:
            colunas_disponiveis = df_excel_carregado.columns.tolist()
            st.sidebar.subheader("2. Configurar Coluna")
            default_index = 0
            for opt_idx, col_name in enumerate(colunas_disponiveis): 
                if 'pedido' in col_name.lower() or 'pedidos' in col_name.lower():
                    default_index = opt_idx; break
            coluna_de_pedidos_selecionada = st.sidebar.selectbox("Coluna dos pedidos:", colunas_disponiveis, index=default_index)
            st.sidebar.success(f"Coluna '{coluna_de_pedidos_selecionada}' selecionada.")
        else: st.sidebar.warning("Excel vazio ou sem colunas."); uploaded_file = None
    except Exception as e: st.sidebar.error(f"Erro ao ler Excel: {e}"); uploaded_file = None
st.sidebar.subheader("3. Iniciar Processo")
process_button = st.sidebar.button("PROCESSAR CONSULTA")


# --- NOVA FUNÇÃO PARA BUSCAR DADOS DA API DA CONTROLADORIA (COM AJUSTE) ---
def buscar_dados_controladoria_api(lista_pedidos_limpos_api: list):
    """
    Busca os dados dos pedidos na API da Controladoria e renomeia as colunas para o padrão do Sysemp.
    """
    if not lista_pedidos_limpos_api:
        st.warning("(API Controladoria) Nenhum ID de pedido para buscar na API.")
        return pd.DataFrame()

    df_api = pd.DataFrame()
    payload = {"pedidos": lista_pedidos_limpos_api}
    
    try:
        st.info(f"(API Controladoria) Conectando e buscando {len(lista_pedidos_limpos_api)} IDs...")
        response = requests.post(API_CONTROLADORIA_URL, headers=API_CONTROLADORIA_HEADERS, json=payload, timeout=90) # Timeout aumentado
        response.raise_for_status()
        
        dados_api = response.json()
        if not dados_api: # Verifica se a API retornou uma lista vazia
            st.warning("(API Controladoria) Nenhum registro encontrado para os IDs consultados.")
            return pd.DataFrame()
            
        df_api = pd.DataFrame(dados_api)

        # AJUSTE: Mapeia e renomeia as colunas do JSON da API para o padrão esperado pelo script
        column_mapping = {
            'canal_venda': '|Sysemp| Canal de Venda',
            'transportadora': '|Sysemp| Transportadora',
            'data_pedido': '|Sysemp| Data do Pedido',
            'data_emissao': '|Sysemp| Data Emissão',
            'data_expedicao': '|Sysemp| Data de Expedição',
            'numero_pedido_limpo': 'N° Pedido Limpo DB',  # Chave para o merge
            'validacao_pedido': '|Sysemp| Validação Pedido',
            'validacao_faturamento': '|Sysemp| Validação Faturamento',
            'ultimo_andamento': '|Sysemp| Último Andamento'
        }
        df_api.rename(columns=column_mapping, inplace=True)
        
        # Garante que as colunas de data sejam do tipo datetime para ordenação
        date_cols_api = ["|Sysemp| Data do Pedido", "|Sysemp| Data Emissão", "|Sysemp| Data de Expedição"]
        for col_date in date_cols_api:
            if col_date in df_api.columns:
                df_api[col_date] = pd.to_datetime(df_api[col_date], errors='coerce')

        st.success(f"(API Controladoria) {len(df_api)} registros recebidos com sucesso.")

    except requests.exceptions.HTTPError as http_err:
        st.error(f"(API Controladoria) Erro HTTP: {http_err} - {response.text}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"(API Controladoria) Erro na requisição: {req_err}")
    except json.JSONDecodeError:
        st.error(f"(API Controladoria) Erro: A resposta da API não é um JSON válido. Resposta: {response.text}")
    except Exception as e:
        st.error(f"(API Controladoria) Erro inesperado: {e}")
        
    return df_api


# --- Main Processing Block ---
if process_button:
    if uploaded_file and df_excel_carregado is not None and coluna_de_pedidos_selecionada:
        try:
            st.subheader("1. Preparando IDs dos Pedidos do Excel")
            df_base_pedidos = df_excel_carregado[[coluna_de_pedidos_selecionada]].copy()
            df_base_pedidos.rename(columns={coluna_de_pedidos_selecionada: "ID Original Excel"}, inplace=True)
            df_base_pedidos.dropna(subset=["ID Original Excel"], inplace=True)
            df_base_pedidos["ID Original Excel"] = df_base_pedidos["ID Original Excel"].astype(str).str.strip().str.upper()
            df_base_pedidos = df_base_pedidos[df_base_pedidos["ID Original Excel"] != '']
            df_base_pedidos.drop_duplicates(subset=["ID Original Excel"], inplace=True, keep='first')

            df_base_pedidos["ID_para_Consulta_API"] = df_base_pedidos["ID Original Excel"].apply(preparar_id_para_bd).str.upper()
            
            if df_base_pedidos.empty:
                st.warning("Nenhum pedido válido extraído do Excel.")
            else:
                st.success(f"Extraídos {len(df_base_pedidos)} pedidos únicos do Excel.")
                
                lista_ids_originais_api_thorpe = df_base_pedidos["ID Original Excel"].unique().tolist()
                lista_ids_limpos_api_controladoria = df_base_pedidos["ID_para_Consulta_API"].unique().tolist()

                df_resultados_sysemp_api = pd.DataFrame()
                if lista_ids_limpos_api_controladoria:
                    # Chama a função da API
                    df_resultados_sysemp_api = buscar_dados_controladoria_api(lista_ids_limpos_api_controladoria)
                    if not df_resultados_sysemp_api.empty and "N° Pedido Limpo DB" in df_resultados_sysemp_api.columns:
                        df_resultados_sysemp_api["N° Pedido Limpo DB"] = df_resultados_sysemp_api["N° Pedido Limpo DB"].astype(str).str.upper()
                else:
                    st.info("(API Controladoria) Nenhum ID válido para consultar a API após o tratamento de sufixos.")

                token_ex_valido = obter_token_thorpe_ex_cached()
                token_es_valido = obter_token_thorpe_es_cached()

                df_resultados_thorpe_api = pd.DataFrame()
                if (token_ex_valido or token_es_valido) and lista_ids_originais_api_thorpe:
                    df_resultados_thorpe_api = buscar_dados_thorpe_combinado_api(lista_ids_originais_api_thorpe, token_ex_valido, token_es_valido)
                    if not df_resultados_thorpe_api.empty and "ID Original Excel" in df_resultados_thorpe_api.columns:
                        df_resultados_thorpe_api["ID Original Excel"] = df_resultados_thorpe_api["ID Original Excel"].astype(str).str.upper()
                elif not (token_ex_valido or token_es_valido):
                    st.error("(API Thorpe Combinado) Tokens inválidos para ambas APIs (EX e ES). Consulta abortada.")
                
                df_final_combinado = df_base_pedidos.copy()

                cols_sysemp_api_esperadas = [
                    "|Sysemp| Canal de Venda", "|Sysemp| Transportadora",
                    "|Sysemp| Data do Pedido", "|Sysemp| Data Emissão", "|Sysemp| Data de Expedição",
                    "|Sysemp| Validação Pedido", "|Sysemp| Validação Faturamento", "|Sysemp| Último Andamento"
                ]
                cols_api_thorpe_combinadas = ["Status Thorpe", "Data Status Thorpe"]

                if not df_resultados_sysemp_api.empty and "N° Pedido Limpo DB" in df_resultados_sysemp_api.columns:
                    # O merge agora pode criar múltiplas linhas por pedido original, o que está correto com base na resposta da API
                    df_final_combinado = pd.merge(df_final_combinado, df_resultados_sysemp_api,
                                                  left_on="ID_para_Consulta_API", right_on="N° Pedido Limpo DB", how="left")
                    if "N° Pedido Limpo DB" in df_final_combinado.columns:
                        del df_final_combinado["N° Pedido Limpo DB"]
                else: 
                    for col_db in cols_sysemp_api_esperadas:
                        if col_db not in df_final_combinado.columns: df_final_combinado[col_db] = pd.NaT if "Data" in col_db else "---"
                
                if not df_resultados_thorpe_api.empty and "ID Original Excel" in df_resultados_thorpe_api.columns:
                    df_final_combinado = pd.merge(df_final_combinado, df_resultados_thorpe_api,
                                                  on="ID Original Excel", how="left")
                else:
                    for col_api in cols_api_thorpe_combinadas:
                         if col_api not in df_final_combinado.columns: df_final_combinado[col_api] = "---"
                
                df_final_combinado.rename(columns={"ID Original Excel": "|Sysemp| N° do Pedido"}, inplace=True)
                
                if "ID_para_Consulta_API" in df_final_combinado.columns:
                    del df_final_combinado["ID_para_Consulta_API"]

                colunas_finais_ordenadas = [
                    "|Sysemp| N° do Pedido", "|Sysemp| Canal de Venda", "|Sysemp| Transportadora",
                    "|Sysemp| Data do Pedido", "|Sysemp| Data Emissão", "|Sysemp| Data de Expedição",
                    "|Sysemp| Validação Pedido", "|Sysemp| Validação Faturamento", "|Sysemp| Último Andamento",
                    "Status Thorpe", "Data Status Thorpe"
                ]
                
                df_final_display = df_final_combinado.reindex(columns=colunas_finais_ordenadas)
                # Preencher NaNs textuais com "---"
                for col in df_final_display.columns:
                    if df_final_display[col].dtype == 'object':
                        df_final_display[col].fillna("---", inplace=True)
                
                # --- INÍCIO DA ORDENAÇÃO ---
                if not df_final_display.empty and '|Sysemp| Data Emissão' in df_final_display.columns:
                    df_final_display.sort_values(
                        by=['|Sysemp| N° do Pedido', '|Sysemp| Data Emissão'],
                        ascending=[True, True], 
                        inplace=True,
                        na_position='last' 
                    )
                # --- FIM DA ORDENAÇÃO ---

                # Formatar colunas de data para exibição APÓS a ordenação
                date_cols_to_format_for_display = ["|Sysemp| Data do Pedido", "|Sysemp| Data Emissão", "|Sysemp| Data de Expedição"]
                for col_date in date_cols_to_format_for_display:
                    if col_date in df_final_display.columns:
                        if pd.api.types.is_datetime64_any_dtype(df_final_display[col_date]):
                            df_final_display[col_date] = df_final_display[col_date].dt.strftime('%d/%m/%Y').fillna("---")
                        else: 
                            df_final_display[col_date] = df_final_display[col_date].astype(str).replace('NaT', '---').fillna("---")


                # --- INÍCIO DO BLOCO DE RESUMO ---
                if not df_final_display.empty:
                    st.markdown("---") 
                    st.subheader("📊 Resumo Geral dos Pedidos Consultados:")

                    col1_resumo, col2_resumo = st.columns(2)

                    with col1_resumo:
                        st.markdown("##### Por Validação Faturamento:")
                        contagem_faturamento = df_final_display['|Sysemp| Validação Faturamento'].value_counts()
                        
                        ordem_faturamento = [
                            'Pedido', 
                            'Nota Fiscal de Venda',
                            'Nota Fiscal de Devolução',
                            'Nota Fiscal de Reenvio',
                            'Nota Fiscal de Venda Cancelada',
                            'Nota Fiscal de Devolução Cancelada',
                            'Nota Fiscal com Erro de Transmissão',
                            '---' 
                        ]
                        contagem_faturamento = contagem_faturamento.reindex(ordem_faturamento, fill_value=0)

                        for status, contagem in contagem_faturamento.items():
                            if status not in ['---', 'Pedido'] and contagem > 0: 
                                st.markdown(f"<li>{status}: <strong>{contagem}</strong></li>", unsafe_allow_html=True)

                    with col2_resumo:
                        st.markdown("##### Por Canal de Venda:")
                        df_pedidos_filtrado = df_final_display[df_final_display['|Sysemp| Validação Faturamento'] == 'Pedido']
                        
                        if not df_pedidos_filtrado.empty:
                            contagem_canal_venda_pedidos = df_pedidos_filtrado['|Sysemp| Canal de Venda'].value_counts()
                            for canal, contagem in contagem_canal_venda_pedidos.items():
                                if canal != '---' and contagem > 0:
                                    st.markdown(f"<li>{canal}: <strong>{contagem}</strong></li>", unsafe_allow_html=True)
                        else:
                            st.markdown("_(Nenhum item com status 'Pedido' para este resumo)_")
                    st.markdown("---") 
                # --- FIM DO BLOCO DE RESUMO ---

                st.subheader("Resultados Finais Combinados") 
                if not df_final_display.empty:
                    st.dataframe(df_final_display, hide_index=True, use_container_width=True)
                    
                    @st.cache_data
                    def convert_df_to_excel(df_to_convert):
                        df_excel = df_to_convert.copy()
                        for col_date_excel in date_cols_to_format_for_display:
                            if col_date_excel in df_excel.columns and pd.api.types.is_datetime64_any_dtype(df_excel[col_date_excel]):
                                df_excel[col_date_excel] = df_excel[col_date_excel].dt.strftime('%d/%m/%Y')
                        df_excel.fillna("---", inplace=True)

                        output_buffer = io.BytesIO()
                        with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                            df_excel.to_excel(writer, index=False, sheet_name='Resultados_Combinados')
                        return output_buffer.getvalue()

                    excel_data = convert_df_to_excel(df_final_display)
                    current_date_str = datetime.now().strftime("%d.%m.%Y")
                    filename = f"resultados_combinados_{current_date_str}.xlsx"
                    st.download_button(label="Baixar Resultado .xlsx", data=excel_data, file_name=filename, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                else:
                    if lista_ids_limpos_api_controladoria or lista_ids_originais_api_thorpe : st.info("Nenhum resultado final para exibir após os merges.")

        except Exception as e:
            st.error(f"Ocorreu um erro geral no processamento: {e}")
            import traceback
            st.error(traceback.format_exc())
    elif not uploaded_file: st.warning("Carregue um arquivo Excel.")
    elif not coluna_de_pedidos_selecionada : st.warning("Selecione a coluna de pedidos.")
    else: st.warning("Verifique o arquivo e a seleção da coluna.")
else:
    st.info("Aguardando upload, configuração e clique em 'PROCESSAR CONSULTA'.")

st.markdown("---")
st.caption("Desenvolvido para consulta otimizada de pedidos - Controladoria.EngageEletro")