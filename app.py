import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la página maximizada
st.set_page_config(layout="wide", page_title="Control de Pedidos", page_icon="📊")

# Código para eliminar márgenes superiores
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Título discreto
st.caption("🚀 Panel de Control Visual (Modo de Prueba)")

# --- BOTÓN DE ACTUALIZAR ---
if st.button("🔄 Sincronizar y Actualizar Cuadro", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Conexión con Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
sheet_url = "https://docs.google.com/spreadsheets/d/1iITzBsZYVoFyvUb-Pvzn-nCCiF_Za7JaugetEZVuBZA/edit" 

@st.cache_data(ttl=5)
def cargar_datos(pestaña):
    df = conn.read(spreadsheet=sheet_url, worksheet=pestaña)
    df = df.fillna("") 
    
    if "Fecha de Envío" in df.columns:
        columnas = list(df.columns)
        indice = columnas.index("Fecha de Envío")
        df = df.iloc[:, :indice+1]
        
    return df.astype(str)

# Listados oficiales de opciones en español
opciones_urgencia = ["Alta", "Normal", "SOS"]
opciones_estado = [
    "Ingresado", "En corte", "En confección", "Proceso plancha", 
    "Proceso Ojal/Boton", "En revisión", "Empacado", "Esperando material", 
    "En Espera", "Cancelado", "Pasa a Inventario", "Completado", "De Inventario", 
    "Listo pero Cancelado", "Inventario Apto", "Inventario Multimarca", "Inventario Manuela"
]
opciones_enviado = ["Enviado", "No Enviado"]
opciones_medio = [
    "Pag Web", "Instagram", "Whatsapp", "Benditta", "Emprenditoria", 
    "Ideal Design", "Sandra Ayala", "Mar de Oro", "Ginebra", "La Rossada", 
    "Pikanela", "Muestra", "Canje", "Garantia", "Cambio", "Daniela Portillo", 
    "ByS group S.A.S", "Amorella", "Atelier"
]

# --- PESTAÑAS ---
tab_pedidos, tab_inventario = st.tabs(["📋 Pedidos", "📦 Pedido Inventario"])

def renderizar_interfaz(df, nombre_hoja):
    
    st.caption("Último documento creado:")
    if not df.empty:
        st.dataframe(df.tail(1), hide_index=True)
        
    # --- FILTRO POR DEFECTO ---
    # Filtramos para mostrar todo EXCEPTO Empacado y Cancelado
    if "Estado" in df.columns:
        df_filtrado = df[~df["Estado"].isin(["Empacado", "Cancelado"])]
    else:
        df_filtrado = df.copy()
        
    # --- FILTROS VISUALES ---
    with st.expander("🔍 Filtros de Búsqueda"):
        columnas_disponibles = df.columns.tolist()
        columnas_filtro = st.multiselect("Selecciona columnas para filtrar:", columnas_disponibles, key=f"cols_{nombre_hoja}")
        
        if columnas_filtro:
            for col in columnas_filtro:
                opciones_unicas = [x for x in df[col].unique() if str(x).strip() != ""]
                valores_seleccionados = st.multiselect(f"Opciones para '{col}':", opciones_unicas, key=f"val_{nombre_hoja}_{col}")
                if valores_seleccionados:
                    df_filtrado = df[df[col].isin(valores_seleccionados)]
                    
        st.caption(f"Resultados en pantalla: {len(df_filtrado)} filas.")

    # --- CONFIGURACIÓN DE COLUMNAS INTERACTIVAS (Estado, Enviado, Urgencia, Medio) ---
    configuracion_columnas = {}
    columnas_editables = []

    if "Estado" in df.columns:
        configuracion_columnas["Estado"] = st.column_config.SelectboxColumn("Estado", options=opciones_estado, required=True)
        columnas_editables.append("Estado")
    if "Enviado" in df.columns:
        configuracion_columnas["Enviado"] = st.column_config.SelectboxColumn("Enviado", options=opciones_enviado, required=True)
        columnas_editables.append("Enviado")
    if "Urgencia" in df.columns:
        configuracion_columnas["Urgencia"] = st.column_config.SelectboxColumn("Urgencia", options=opciones_urgencia, required=True)
        columnas_editables.append("Urgencia")
    if "Medio" in df.columns:
        configuracion_columnas["Medio"] = st.column_config.SelectboxColumn("Medio", options=opciones_medio, required=True)
        columnas_editables.append("Medio")

    # Bloqueamos el resto
    columnas_bloqueadas = [c for c in df.columns if c not in columnas_editables]

    cambios = st.data_editor(
        df_filtrado,
        disabled=columnas_bloqueadas,
        column_config=configuracion_columnas,
        hide_index=True,
        use_container_width=True,
        height=800, 
        key=f"editor_{nombre_hoja}"
    )

    if st.button(f"💾 Guardar Cambios en '{nombre_hoja}'", type="primary", use_container_width=True):
        st.success("Cambios registrados correctamente.")

# --- CARGA ---
with tab_pedidos:
    try:
        renderizar_interfaz(cargar_datos("Pedidos"), "Pedidos")
    except Exception as e:
        st.error(f"Error: {e}")

with tab_inventario:
    try:
        renderizar_interfaz(cargar_datos("Pedido Inventario"), "Pedido Inventario")
    except Exception as e:
        st.error(f"Error: {e}")
