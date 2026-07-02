import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración horizontal y compresión de márgenes (CSS)
st.set_page_config(layout="wide", page_title="Control de Pedidos", page_icon="📊")

# Bloque de diseño para eliminar espacios en blanco innecesarios arriba
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

# Conexión con tu ID de Sheets real
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

# Opciones asignadas para las listas desplegables
opciones_urgencia = ["Alta", "Normal", "SOS"]
opciones_estado = [
    "Ingresado", "En corte", "En confección", "Proceso plancha", 
    "Proceso Ojal/Boton", "En revisión", "Empacado", "Esperando material", 
    "En Espera", "Cancelado", "Pasa a Inventario", "Completado", "De Inventario", 
    "Listo pero Cancelado", "Inventario Apto", "Inventario Multimarca", "Inventario Manuela"
]
opciones_enviado = ["Enviado", "No Enviado"]

# --- PESTAÑAS ---
tab_pedidos, tab_inventario = st.tabs(["📋 Pedidos", "📦 Pedido Inventario"])

# Función para construir la interfaz
def renderizar_interfaz(df, nombre_hoja):
    
    # Vista del último registro en miniatura
    st.caption("Último documento creado:")
    if not df.empty:
        st.dataframe(df.tail(1), hide_index=True)
        
    # --- SISTEMA DE FILTROS (Solo para visualización) ---
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

    # --- MEJORA: CONFIGURACIÓN EXCLUSIVA DE LAS 4 COLUMNAS EDITABLES ---
    configuracion_columnas = {}
    columnas_editables = []

    if "Estado" in df.columns:
        configuracion_columnas["Estado"] = st.column_config.SelectboxColumn("Estado", options=opciones_estado)
        columnas_editables.append("Estado")
        
    if "Enviado" in df.columns:
        configuracion_columnas["Enviado"] = st.column_config.SelectboxColumn("Enviado", options=opciones_enviado)
        columnas_editables.append("Enviado")
        
    if "Urgencia" in df.columns:
        configuracion_columnas["Urgencia"] = st.column_config.SelectboxColumn("Urgencia", options=opciones_urgencia)
        columnas_editables.append("Urgencia")
        
    if "Orden" in df.columns:
        # Genera las opciones dinámicamente con los valores existentes en la columna "Orden"
        opciones_orden = sorted(list(set([x for x in df["Orden"].unique() if str(x).strip() != ""])))
        configuracion_columnas["Orden"] = st.column_config.SelectboxColumn("Orden", options=opciones_orden)
        columnas_editables.append("Orden")

    # Bloquear absolutamente todo el resto de columnas del cuadro
    columnas_bloqueadas = [c for c in df.columns if c not in columnas_editables]

    # El cuadro abarca 800 píxeles de alto para dominar la pantalla
    cambios = st.data_editor(
        df_filtrado,
        disabled=columnas_bloqueadas,
        column_config=configuracion_columnas,
        hide_index=True,
        use_container_width=True,
        height=800, 
        key=f"editor_{nombre_hoja}"
    )

    # Botón de Guardar simulado para la presentación
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
