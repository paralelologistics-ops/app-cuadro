import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la página maximizada
st.set_page_config(layout="wide", page_title="Control de Pedidos", page_icon="📊")

# Estilos: Logo redondo, colores y limpieza de márgenes
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    header { visibility: hidden; }
    /* Estilo del Logo */
    .logo-img {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #f0f0f0;
    }
    </style>
    """, unsafe_allow_html=True)

# Logo y Título
st.markdown(f'''
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        <img src="https://static.wixstatic.com/media/d0ce54_32d30a8159fd44d4a26c62563d7bfc38~mv2.jpg" class="logo-img">
        <h3>Panel de Control - Paralelo</h3>
    </div>
''', unsafe_allow_html=True)

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

# Listados oficiales
opciones_urgencia = ["Alta", "Normal", "SOS"]
opciones_estado = ["Ingresado", "En corte", "En confección", "Proceso plancha", "Proceso Ojal/Boton", "En revisión", "Empacado", "Esperando material", "En Espera", "Cancelado", "Pasa a Inventario", "Completado", "De Inventario", "Listo pero Cancelado", "Inventario Apto", "Inventario Multimarca", "Inventario Manuela"]
opciones_enviado = ["Enviado", "No Enviado"]
opciones_medio = ["Pag Web", "Instagram", "Whatsapp", "Benditta", "Emprenditoria", "Ideal Design", "Sandra Ayala", "Mar de Oro", "Ginebra", "La Rossada", "Pikanela", "Muestra", "Canje", "Garantia", "Cambio", "Daniela Portillo", "ByS group S.A.S", "Amorella", "Atelier"]

# --- PESTAÑAS ---
tab_pedidos, tab_inventario = st.tabs(["📋 Pedidos", "📦 Pedido Inventario"])

def renderizar_interfaz(df, nombre_hoja):
    st.caption("Último documento creado:")
    if not df.empty:
        st.dataframe(df.tail(1), hide_index=True)
        
    # --- FILTRO INICIAL AUTOMÁTICO ---
    df_filtrado = df.copy()
    if "Estado" in df.columns:
        df_filtrado = df_filtrado[~df_filtrado["Estado"].isin(["Empacado", "Cancelado"])]
        
    # --- FILTROS VISUALES MEJORADOS ---
    with st.expander("🔍 Filtros de Búsqueda"):
        cols_a_filtrar = st.multiselect("Selecciona columnas para filtrar:", df.columns.tolist(), key=f"cols_{nombre_hoja}")
        
        for col in cols_a_filtrar:
            opciones_unicas = [x for x in df[col].unique() if str(x).strip() != ""]
            valores = st.multiselect(f"Selecciona valores para {col}:", opciones_unicas, key=f"sel_{nombre_hoja}_{col}")
            if valores:
                df_filtrado = df_filtrado[df_filtrado[col].isin(valores)]
                    
    st.caption(f"Resultados en pantalla: {len(df_filtrado)} filas.")

    # --- CONFIGURACIÓN DE COLUMNAS ---
    config = {
        "Estado": st.column_config.SelectboxColumn("Estado", options=opciones_estado, required=True),
        "Enviado": st.column_config.SelectboxColumn("Enviado", options=opciones_enviado, required=True),
        "Urgencia": st.column_config.SelectboxColumn("Urgencia", options=opciones_urgencia, required=True),
        "Medio": st.column_config.SelectboxColumn("Medio", options=opciones_medio, required=True)
    }

    # Editor
    cambios = st.data_editor(
        df_filtrado,
        column_config=config,
        disabled=[c for c in df.columns if c not in config.keys()],
        hide_index=True,
        use_container_width=True,
        height=800, 
        key=f"editor_{nombre_hoja}"
    )

    if st.button(f"💾 Guardar Cambios en '{nombre_hoja}'", type="primary", use_container_width=True):
        st.success("Cambios procesados.")

# --- CARGA ---
with tab_pedidos:
    try: renderizar_interfaz(cargar_datos("Pedidos"), "Pedidos")
    except Exception as e: st.error(f"Error: {e}")

with tab_inventario:
    try: renderizar_interfaz(cargar_datos("Pedido Inventario"), "Pedido Inventario")
    except Exception as e: st.error(f"Error: {e}")
