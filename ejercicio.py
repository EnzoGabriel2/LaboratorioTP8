import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter

# Función para mostrar información del alumno
def mostrar_informacion_alumno():
    st.markdown('**Legajo:** 58873')
    st.markdown('**Nombre:** Salazar Enzo Gabriel')
    st.markdown('**Comisión:** C5')

# Configuración de la página
st.set_page_config(layout="wide")
st.title("Análisis de Ventas por Producto")

# Panel lateral
st.sidebar.header("Cargar archivo de datos")
uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV", type="csv")
sucursal = st.sidebar.selectbox("Seleccionar Sucursal", ["Todas"])

if uploaded_file is not None:
    # Cargar datos
    df = pd.read_csv(uploaded_file)

    # Validar y limpiar las fechas
    df['Año'] = pd.to_numeric(df['Año'], errors='coerce')  # Convertir Año a numérico
    df['Mes'] = pd.to_numeric(df['Mes'], errors='coerce')  # Convertir Mes a numérico
    df = df.dropna(subset=['Año', 'Mes'])  # Eliminar filas con datos nulos
    df = df[(df['Año'] >= 2000) & (df['Año'] <= 2024)]  # Filtrar años en rango lógico
    df['Mes'] = df['Mes'].apply(lambda x: x if 1 <= x <= 12 else None)  # Validar meses
    df = df.dropna(subset=['Mes'])  # Eliminar filas con meses fuera de rango

    # Crear columna de fecha
    df['Fecha'] = pd.to_datetime(
        df['Año'].astype(int).astype(str) + '-' +
        df['Mes'].astype(int).astype(str).apply(lambda x: x.zfill(2))  # Aplicar zfill con apply
    )

    # Filtrar datos por sucursal
    if sucursal != "Todas":
        df = df[df['Sucursal'] == sucursal]

    # Calcular métricas
    df['Precio_promedio'] = df['Ingreso_total'] / df['Unidades_vendidas']
    df['Margen_promedio'] = (df['Ingreso_total'] - df['Costo_total']) / df['Ingreso_total']

    grouped = df.groupby('Producto').agg(
        Unidades_vendidas=('Unidades_vendidas', 'sum'),
        Precio_promedio=('Precio_promedio', 'mean'),
        Margen_promedio=('Margen_promedio', 'mean')
    ).reset_index()

    # Visualización
    st.header("Datos de Todas las Sucursales")
    for i, row in grouped.iterrows():
        col1, col2 = st.columns([1, 3])

        # Métricas en el lado izquierdo
        with col1:
            st.subheader(row['Producto'])

            # Ejemplo de delta dinámico (ajusta con tu lógica)
            delta_precio = row['Precio_promedio'] * 0.1  # Ajusta el delta según tus datos
            delta_margen = row['Margen_promedio'] * 0.05  # Ajusta el delta según tus datos
            delta_unidades = row['Unidades_vendidas'] * 0.1  # Ajusta el delta según tus datos

            st.metric("Precio Promedio", f"${row['Precio_promedio']:.2f}",
                      delta=f"{delta_precio:.2f}", delta_color="normal")
            st.metric("Margen Promedio", f"{row['Margen_promedio']*100:.2f}%",
                      delta=f"{delta_margen:.2f}%", delta_color="inverse")
            st.metric("Unidades Vendidas", f"{row['Unidades_vendidas']:,}",
                      delta=f"{int(delta_unidades):,}", delta_color="normal")

        # Gráfica en el lado derecho
        with col2:
            product_data = df[df['Producto'] == row['Producto']]

            # Agrupar ventas por fecha
            monthly_sales = product_data.groupby('Fecha').agg(
                Unidades_vendidas=('Unidades_vendidas', 'sum')
            ).reset_index()

            # Crear gráfica
            plt.figure(figsize=(10, 6))
            plt.plot(
                monthly_sales['Fecha'], monthly_sales['Unidades_vendidas'],
                marker='o', linestyle='-', color='blue', label=row['Producto']
            )

            # Añadir línea de tendencia
            sns.regplot(
                x=monthly_sales.index,
                y=monthly_sales['Unidades_vendidas'],
                scatter=False,
                color='red',
                label='Tendencia',
                line_kws={"linewidth": 2}
            )

            # Formato del eje X
            ax = plt.gca()
            ax.xaxis.set_major_formatter(DateFormatter("%Y-%m"))
            ax.set_xlim([monthly_sales['Fecha'].min(), monthly_sales['Fecha'].max()])  # Ajustar límites del eje X

            plt.title(f"Evolución de Ventas Mensual - {row['Producto']}", fontsize=14)
            plt.xlabel("Fecha (Año-Mes)", fontsize=12)
            plt.ylabel("Unidades Vendidas", fontsize=12)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.legend()
            plt.tight_layout()

            st.pyplot(plt)

# Mostrar información del alumno
mostrar_informacion_alumno()
