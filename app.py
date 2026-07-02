import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración horizontal (wide) y en español
st.set_page_config(layout="wide", page_title="Control de Pedidos", page_icon="📊")

st.title("🚀 Panel de Control Visual")

# --- BOTÓN DE ACTUALIZAR ---
# Modificado para que diga exactamente lo solicitado
if st.button("Actualizar Cuadro", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.divider()

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)
# ¡RECUERDA PEGAR TU ENLACE REAL ABAJO!
sheet_url = "https://docs.google.com/spreadsheets/d/TU_ID_DE_CUADRO_REAL/edit" 

@st.cache_data(ttl=10)
def cargar_datos(pestaña):
    df = conn.read(spreadsheet=sheet_url, worksheet=pestaña)
    # Reemplazar valores nulos (None) por espacios en blanco
    df = df.fillna("") 
    # Asegurar que todo se lea como texto para evitar errores visuales
    return df.astype(str)

# 2. Listas de opciones exactas solicitadas
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

# --- PESTAÑAS (Nombre corregido) ---
tab_pedidos, tab_inventario = st.tabs(["📋 Pedidos", "📦 Pedido Inventarios"])

# Función para construir la interfaz de cada hoja de forma idéntica
def renderizar_interfaz(df, nombre_hoja):
    
    # Mostrar siempre el último registro en la parte superior para seguimiento del consecutivo
    st.subheader("Último documento creado")
    if not df.empty:
        st.dataframe(df.tail(1), hide_index=True)
        
    st.divider()
    
    # --- SISTEMA DE FILTROS MÚLTIPLES ---
    st.subheader("🔍 Filtros Dinámicos")
    columnas_disponibles = df.columns.tolist()
    
    # 1. Escoger por cuál columna filtrar
    columnas_filtro = st.multiselect(
        "1. Selecciona las columnas por las que deseas filtrar:", 
        columnas_disponibles, 
        key=f"cols_{nombre_hoja}"
    )
    
    df_filtrado = df.copy()
    
    # 2. Escoger las opciones dentro de cada columna
    if columnas_filtro:
        for col in columnas_filtro:
            # Extraer solo las opciones que existan y no estén en blanco
            opciones_unicas = [x for x in df[col].unique() if str(x).strip() != ""]
            valores_seleccionados = st.multiselect(
                f"2. Elige las opciones para '{col}':", 
                opciones_unicas, 
                key=f"val_{nombre_hoja}_{col}"
            )
            
            # Aplicar filtro simultáneo
            if valores_seleccionados:
                df_filtrado = df_filtrado[df_filtrado[col].isin(valores_seleccionados)]
                
    st.info(f"Mostrando {len(df_filtrado)} registros en pantalla.")

    # --- CONFIGURACIÓN DE COLUMNAS EDITABLES ---
    configuracion_columnas = {}
    columnas_editables = []

    # Validamos que las columnas existan en la hoja para convertirlas en listas desplegables
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

    # Bloquear el resto de las columnas para evitar daños a los datos de tus formularios
    columnas_bloqueadas = [c for c in df.columns if c not in columnas_editables]

    st.subheader("Tabla de Edición")
    
    cambios = st.data_editor(
        df_filtrado,
        disabled=columnas_bloqueadas,
        column_config=configuracion_columnas,
        hide_index=True,
        use_container_width=True,
        key=f"editor_{nombre_hoja}"
    )

    # Botón para guardar
    if st.button(f"💾 Guardar Cambios en {nombre_hoja}", type="primary", use_container_width=True):
        df.update(cambios)
        conn.update(spreadsheet=sheet_url, worksheet=nombre_hoja, data=df)
        st.success(f"¡Los datos de {nombre_hoja} se actualizaron en tu cuadro original!")
        st.cache_data.clear()
        st.rerun()

# --- CARGA DE DATOS POR PESTAÑA ---
with tab_pedidos:
    try:
        df_pedidos = cargar_datos("Pedidos")
        renderizar_interfaz(df_pedidos, "Pedidos")
    except Exception as e:
        st.error(f"Asegúrate de que la pestaña se llama 'Pedidos'. Detalle: {e}")

with tab_inventario:
    try:
        df_inv = cargar_datos("Pedido Inventarios")
        renderizar_interfaz(df_inv, "Pedido Inventarios")
    except Exception as e:
        st.error(f"Asegúrate de que la pestaña se llama 'Pedido Inventarios'. Detalle: {e}")
