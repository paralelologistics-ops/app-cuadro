import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración horizontal y compresión de márgenes (CSS)
st.set_page_config(layout="wide", page_title="Control de Pedidos", page_icon="📊")

# Este bloque de código invisible reduce drásticamente los espacios en blanco de la pantalla
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Título minúsculo
st.caption("🚀 Panel de Control Visual (Modo Demo)")

# --- BOTÓN DE ACTUALIZAR ---
if st.button("Actualizar Cuadro", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Conexión en modo lectura para la presentación
conn = st.connection("gsheets", type=GSheetsConnection)
sheet_url = "https://docs.google.com/spreadsheets/d/1iITzBsZYVoFyvUb-Pvzn-nCCiF_Za7JaugetEZVuBZA/edit" 

@st.cache_data(ttl=10)
def cargar_datos(pestaña):
    df = conn.read(spreadsheet=sheet_url, worksheet=pestaña)
    df = df.fillna("") 
    
    # Recortar la tabla para mostrar solo hasta "Fecha de Envío"
    if "Fecha de Envío" in df.columns:
        columnas = list(df.columns)
        indice = columnas.index("Fecha de Envío")
        df = df.iloc[:, :indice+1]
        
    return df.astype(str)

# 2. Listas de opciones
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

# Función para construir la interfaz
def renderizar_interfaz(df, nombre_hoja):
    
    # Texto muy pequeño para el último documento
    st.caption("Último documento creado:")
    if not df.empty:
        st.dataframe(df.tail(1), hide_index=True)
        
    # --- SISTEMA DE FILTROS EN MENÚ DESPLEGABLE ---
    with st.expander("🔍 Filtros"):
        columnas_disponibles = df.columns.tolist()
        
        columnas_filtro = st.multiselect(
            "1. Selecciona las columnas por las que deseas filtrar:", 
            columnas_disponibles, 
            key=f"cols_{nombre_hoja}"
        )
        
        df_filtrado = df.copy()
        
        if columnas_filtro:
            for col in columnas_filtro:
                opciones_unicas = [x for x in df[col].unique() if str(x).strip() != ""]
                valores_seleccionados = st.multiselect(
                    f"2. Elige las opciones para '{col}':", 
                    opciones_unicas, 
                    key=f"val_{nombre_hoja}_{col}"
                )
                
                if valores_seleccionados:
                    df_filtrado = df_filtrado[df_filtrado[col].isin(valores_seleccionados)]
                    
        st.caption(f"Mostrando {len(df_filtrado)} registros.")

    # --- CONFIGURACIÓN DE COLUMNAS EDITABLES ---
    configuracion_columnas = {}
    columnas_editables = []

    if "Estado" in df.columns:
        configuracion_columnas["Estado"] = st.column_config.SelectboxColumn("Estado", options=opciones_estado)
        columnas_editables.append("Estado")
    if "Urgencia" in df.columns:
        configuracion_columnas["Urgencia"] = st.column_config.SelectboxColumn("Urgencia", options=opciones_urgencia)
        columnas_editables.append("Urgencia")
    if "Enviado" in df.columns:
        configuracion_columnas["Enviado"] = st.column_config.SelectboxColumn("Enviado", options=opciones_enviado)
        columnas_editables.append("Enviado")
    if "Medio" in df.columns:
        configuracion_columnas["Medio"] = st.column_config.SelectboxColumn("Medio", options=opciones_medio)
        columnas_editables.append("Medio")
    if "Observaciones" in df.columns:
        configuracion_columnas["Observaciones"] = st.column_config.TextColumn("Observaciones")
        columnas_editables.append("Observaciones")

    # Bloquear el resto de las columnas
    columnas_bloqueadas = [c for c in df.columns if c not in columnas_editables]

    # Altura llevada a 800 para dominar la pantalla
    cambios = st.data_editor(
        df_filtrado,
        disabled=columnas_bloqueadas,
        column_config=configuracion_columnas,
        hide_index=True,
        use_container_width=True,
        height=800, 
        key=f"editor_{nombre_hoja}"
    )

    # Botón para guardar (Modo Demo)
    if st.button(f"💾 Guardar Cambios en {nombre_hoja}", type="primary", use_container_width=True):
        st.success(f"¡Simulación exitosa! En la versión final, los cambios de {nombre_hoja} actualizarán tu cuadro original en tiempo real.")

# --- CARGA DE DATOS POR PESTAÑA ---
with tab_pedidos:
    try:
        df_pedidos = cargar_datos("Pedidos")
        renderizar_interfaz(df_pedidos, "Pedidos")
    except Exception as e:
        st.error(f"Asegúrate de que la pestaña se llama 'Pedidos'. Detalle: {e}")

with tab_inventario:
    try:
        df_inv = cargar_datos("Pedido Inventario")
        renderizar_interfaz(df_inv, "Pedido Inventario")
    except Exception as e:
        st.error(f"Asegúrate de que la pestaña se llama 'Pedido Inventario'. Detalle: {e}")
