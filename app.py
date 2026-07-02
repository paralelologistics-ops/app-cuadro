import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración estética de la página (Diseño limpio y centrado)
st.set_page_config(layout="wide", page_title="Control de Pedidos e Inventario", page_icon="📊")

# Estilos visuales personalizados para los botones de filtro y diseño
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #1E293B; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 Panel de Control Visual</div>', unsafe_allow_html=True)

# Conexión con tu Google Sheet central
conn = st.connection("gsheets", type=GSheetsConnection)
sheet_url = "https://docs.google.com/spreadsheets/d/1iITzBsZYVoFyvUb-Pvzn-nCCiF_Za7JaugetEZVuBZA/edit"

# Función para cargar datos de una pestaña específica de forma limpia
@st.cache_data(ttl=10) # Se refresca cada 10 segundos automáticamente para captar nuevos formularios
def cargar_datos(pestaña):
    return conn.read(spreadsheet=sheet_url, worksheet=pestaña)

# --- CREACIÓN DE LAS DOS PESTAÑAS EN LA APP ---
tab_pedidos, tab_inventario = st.tabs(["📋 Hojas de Pedidos", "📦 Pedido de Inventario"])

# =========================================================================
# PESTAÑA 1: PEDIDOS
# =========================================================================
with tab_pedidos:
    st.write("Visualiza, filtra y gestiona los estados de los pedidos entrantes.")
    
    try:
        df_pedidos = cargar_datos("Pedidos")
        
        # Asegurar que existan las columnas de control si no están creadas
        if "Estado" not in df_pedidos.columns: df_pedidos["Estado"] = "Pendiente"
        if "Observaciones" not in df_pedidos.columns: df_pedidos["Observaciones"] = ""
        
        # --- BOTONES DE FILTRO RÁPIDO ---
        st.write("**Filtrar rápidamente por Estado:**")
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        
        # Usamos el estado de la sesión de Streamlit para recordar qué botón se presionó
        if "filtro_pedidos" not in st.session_state:
            st.session_state.filtro_pedidos = "Todos"
            
        with col_b1:
            if st.button("📋 Ver Todos", key="btn_p_todos"): st.session_state.filtro_pedidos = "Todos"
        with col_b2:
            if st.button("⏳ Solo Pendientes", key="btn_p_pend"): st.session_state.filtro_pedidos = "Pendiente"
        with col_b3:
            if st.button("⚙️ En Preparación", key="btn_p_prep"): st.session_state.filtro_pedidos = "En Preparación"
        with col_b4:
            if st.button("✅ Despachados", key="btn_p_desp"): st.session_state.filtro_pedidos = "Despachado"
            
        # Aplicar el filtro seleccionado por los botones al cuadro de datos
        if st.session_state.filtro_pedidos != "Todos":
            df_filtrado = df_pedidos[df_pedidos["Estado"] == st.session_state.filtro_pedidos]
        else:
            df_filtrado = df_pedidos

        st.info(f"Mostrando: **{st.session_state.filtro_pedidos}** ({len(df_filtrado)} registros)")

        # --- TABLA INTERACTIVA ESTÉTICA ---
        # Definimos qué columnas NO se pueden tocar (las que vienen del formulario)
        columnas_bloqueadas = [col for col in df_pedidos.columns if col not in ["Estado", "Observaciones"]]
        
        # El data_editor permite modificar celdas como un Excel pero de forma controlada
        cambios_pedidos = st.data_editor(
            df_filtrado,
            disabled=columnas_bloqueadas, # Bloquea los datos del formulario para protegerlos
            column_config={
                "Estado": st.column_config.SelectboxColumn(
                    "Estado Actual",
                    options=["Pendiente", "En Preparación", "Despachado", "Cancelado"],
                    required=True
                ),
                "Observaciones": st.column_config.TextColumn("Observaciones / Notas Internas", width="large")
            },
            hide_index=True,
            use_container_width=True,
            key="editor_pedidos"
        )
        
        # --- BOTÓN PARA GUARDAR MODIFICACIONES ---
        if st.button("💾 Guardar Cambios en Pedidos", type="primary"):
            # Reincorporar las filas editadas al dataframe original respetando sus posiciones reales
            df_pedidos.update(cambios_pedidos)
            conn.update(spreadsheet=sheet_url, worksheet="Pedidos", data=df_pedidos)
            st.success("¡Cuadro de Pedidos actualizado con éxito en Sheets!")
            st.cache_data.clear() # Limpia caché para forzar la lectura fresca de datos
            st.rerun()

    except Exception as e:
        st.error(f"Asegúrate de que la pestaña se llama exactamente 'Pedidos'. Error: {e}")


# =========================================================================
# PESTAÑA 2: PEDIDO DE INVENTARIO
# =========================================================================
with tab_inventario:
    st.write("Visualiza y gestiona las solicitudes y movimientos de inventario.")
    
    try:
        df_inv = cargar_datos("Pedido de Inventario")
        
        if "Estado" not in df_inv.columns: df_inv["Estado"] = "Pendiente"
        if "Observaciones" not in df_inv.columns: df_inv["Observaciones"] = ""
        
        # --- BOTONES DE FILTRO RÁPIDO PARA INVENTARIO ---
        st.write("**Filtrar rápidamente por Estado:**")
        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        
        if "filtro_inv" not in st.session_state:
            st.session_state.filtro_inv = "Todos"
            
        with col_i1:
            if st.button("📦 Ver Todo el Inventario", key="btn_i_todos"): st.session_state.filtro_inv = "Todos"
        with col_i2:
            if st.button("🛑 Por Surtir / Pendiente", key="btn_i_pend"): st.session_state.filtro_inv = "Pendiente"
        with col_i3:
            if st.button("🚚 En Camino", key="btn_i_cam"): st.session_state.filtro_inv = "En Camino"
        with col_i4:
            if st.button("🟢 Finalizado / Recibido", key="btn_i_fin"): st.session_state.filtro_inv = "Finalizado"
            
        if st.session_state.filtro_inv != "Todos":
            df_inv_filtrado = df_inv[df_inv["Estado"] == st.session_state.filtro_inv]
        else:
            df_inv_filtrado = df_inv

        st.info(f"Mostrando: **{st.session_state.filtro_inv}** ({len(df_inv_filtrado)} registros)")

        # --- TABLA INTERACTIVA ---
        columnas_bloqueadas_inv = [col for col in df_inv.columns if col not in ["Estado", "Observaciones"]]
        
        cambios_inv = st.data_editor(
            df_inv_filtrado,
            disabled=columnas_bloqueadas_inv,
            column_config={
                "Estado": st.column_config.SelectboxColumn(
                    "Estado Inventario",
                    options=["Pendiente", "En Camino", "Finalizado"],
                    required=True
                ),
                "Observaciones": st.column_config.TextColumn("Notas de Inventario", width="large")
            },
            hide_index=True,
            use_container_width=True,
            key="editor_inventario"
        )
        
        if st.button("💾 Guardar Cambios en Inventario", type="primary"):
            df_inv.update(cambios_inv)
            conn.update(spreadsheet=sheet_url, worksheet="Pedido de Inventario", data=df_inv)
            st.success("¡Cuadro de Inventario actualizado con éxito en Sheets!")
            st.cache_data.clear()
            st.rerun()

    except Exception as e:
        st.error(f"Asegúrate de que la pestaña se llama exactamente 'Pedido de Inventario'. Error: {e}")
