import streamlit as st  # Importa Streamlit para crear interfaces web interactivas
import numpy as np  # Importa NumPy para manejo de vectores y operaciones numéricas
import plotly.graph_objects as go  # Importa plotly para generar gráficos 3D
from itertools import combinations  # Importa combinaciones para iterar pares de cargas


# r_vec: dirección y distancia entre cargas

# r_mag: solo la distancia

# r_hat: solo la dirección

# f_mag: solo la magnitud de la fuerza

# f_vec: vector de la fuerza (dirección y magnitud)



k = 8.99e9  # Constante de Coulomb

st.title("Calculadora de Fuerza Eléctrica Vectorial") 

st.markdown("### Selecciona cargas a ingresar") 

# el usuario selecciona cuántas cargas va a ingresar (entre 2 y 20)
n_cargas = st.number_input("Número de cargas", min_value=2, max_value=20, value=2, step=1)

st.markdown("### Ingresa los valores y posiciones de las cargas") 

cargas = []  # Lista para guardar los datos de cada carga (valor)

# Ciclo para capturar el valor y la posición de cada carga
for i in range(n_cargas):
    st.markdown(f"#### Carga {i+1}") 
    # Entrada del valor de la carga en Coulombs
    q = st.number_input(f"q{i+1} (C)", value=1e-6 if i == 0 else (-1e-6 if i == 1 else 1e-6), format="%.2e", key=f"q{i}")
    # Entradas de posición en X, Y y Z
    #x1, valor data, key identifica
    x = st.number_input(f"x{i+1}", value=0.0, key=f"x{i}")
    y = st.number_input(f"y{i+1}", value=0.0, key=f"y{i}")
    z = st.number_input(f"z{i+1}", value=0.0, key=f"z{i}")
    # Guarda la carga y posición en un array
    #carga, posicion: coordenadas en 3d
    cargas.append({'q': q, 'pos': np.array([x, y, z])})

# iniciar los cálculos y mostrar resultados
if st.button("Calcular y Mostrar Gráfico"):
    n = len(cargas)  # Número de cargas

    # Lista para almacenar la fuerza neta sobre cada carga
    #[0.0, 0.0, 0.0]
    fuerzas = [np.zeros(3) for _ in range(n)] 

    # Matriz para guardar las distancias entre pares de cargas
    distancias = np.zeros((n, n))

    # Cálculo de las fuerzas entre todas las combinaciones de cargas
    for i in range(n):
        for j in range(n):
            if i != j:
                #vector de posición que va de la carga i a la carga j.
                r_vec = cargas[j]['pos'] - cargas[i]['pos']  

                # r_magnitud: distancia entre ambas cargas.
                r_mag = np.linalg.norm(r_vec)
                distancias[i][j] = r_mag  # Almacena la distancia

                if r_mag == 0:
                    # Error si dos cargas están en el mismo punto
                    st.error(f"Las cargas {i+1} y {j+1} están en el mismo punto. No se puede calcular la fuerza.")
                    st.stop()
                
                r_hat = r_vec / r_mag  # Vector unitario en la dirección de la fuerza
                f_mag = k * cargas[i]['q'] * cargas[j]['q'] / r_mag**2  # Magnitud de la fuerza de Coulomb
                f_vec = f_mag * r_hat  # Vector de la fuerza
                fuerzas[i] += f_vec  # Suma la fuerza total que actúa sobre la carga i

    # Muestra los resultados de las fuerzas netas sobre cada carga
    st.markdown("### Resultados de Fuerzas")

    #recorre la lista de fuerzas que cada elimento es un vector de 3
    for i, f in enumerate(fuerzas):
        #f[0], f[1], f[2]: componentes x, y, z de la fuerza neta
        #:.2e: formato en notación científica con 2 cifras decimales
        st.success(f"Fuerza neta sobre carga {i+1} (N): ({f[0]:.2e}, {f[1]:.2e}, {f[2]:.2e})")
    
    # Muestra una tabla con las distancias entre cada par de cargas
    st.markdown("### Distancias entre cargas (metros)")
    dist_text = "| Cargas | Distancia (m) |\n|-------|--------------|\n"
    for i, j in combinations(range(n), 2):
        dist_text += f"| q{i+1}-q{j+1} | {distancias[i][j]:.2e} |\n"
    st.markdown(dist_text) # se muestra la tabla completa

    # Crea una figura 3D vacía para graficar las cargas y vectores de fuerza
    fig = go.Figure() #go creaa gráficos personalizados.

    colores = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'cyan', 'magenta']  # Colores para distinguir las cargas
    #recorre las cargas
    for i, carga in enumerate(cargas):
        c = colores[i % len(colores)]  # Asigna un color a cada carga

        #pos[0] = x, pos[1] = y, pos[2] = z.
        pos = carga['pos']
        # Añade un punto 3D para representar la carga
        fig.add_trace(go.Scatter3d(
            x=[pos[0]], y=[pos[1]], z=[pos[2]],

            #Se dibuja un punto y un texto encima.
            mode='markers+text',
            #Tamaño y color del punto que representa la carga.
            marker=dict(size=8, color=c),
            #Texto que aparece junto al punto, como q1
            text=[f"q{i+1}"],
            #Posición del texto 
            textposition="top center",
            #Nombre para la leyenda
            name=f'Carga {i+1}'
        ))

    # Añade vectores de fuerza como conos 3D desde cada carga

    #recorre la lista fuerzas, que contiene los vectores de fuerza neta calculados
    for i, f in enumerate(fuerzas):
        pos = cargas[i]['pos']
        fig.add_trace(go.Cone(
            x=[pos[0]], y=[pos[1]], z=[pos[2]],

            #Determinan hacia dónde apunta el cono
           # Componentes del vector fuerza en cada eje (dirección y magnitud)
            u=[f[0]],  # Componente en X de la fuerza
            v=[f[1]],  # Componente en Y de la fuerza
            w=[f[2]],  # Componente en Z de la fuerza

            sizemode="absolute", sizeref=0.2,
            # El cono se dibuja con la "cola" en la posición (x,y,z), la punta indica dirección
            anchor="tail",
            showscale=False,
            colorscale='Viridis',
            name=f'Fuerza sobre q{i+1}'
        ))
    
    # Añade líneas entre cada par de cargas para visualizar sus conexiones 
    # y mostrar distancias
    for i, j in combinations(range(n), 2):

        #obtenemos la posicion de las cargas en el grafico 3d
        pos_i = cargas[i]['pos']
        pos_j = cargas[j]['pos']
        
        # Línea entre las cargas i y j
        fig.add_trace(go.Scatter3d(
            x=[pos_i[0], pos_j[0]],
            y=[pos_i[1], pos_j[1]],
            z=[pos_i[2], pos_j[2]],
            mode='lines',
            # línea discontinua
            line=dict(color='yellow', width=2, dash='dash'),
            showlegend=False
        ))
        
        # Muestra la distancia entre las cargas 
        mid_point = (pos_i + pos_j) / 2 # sumando las coordenadas y dividiendo por 2.
        fig.add_trace(go.Scatter3d(
            x=[mid_point[0]],
            y=[mid_point[1]],
            z=[mid_point[2]],
            mode='text',
            text=[f"{distancias[i][j]:.2f}m"],
            textposition="middle center",
            textfont=dict(color='black', size=10),
            showlegend=False,
            hoverinfo='text',
            hovertext=f"Distancia q{i+1}-q{j+1}: {distancias[i][j]:.2e}m"
        ))

    # Configura la apariencia del gráfico 3D
    fig.update_layout(
        scene=dict(
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            zaxis_title='Z (m)',
            aspectmode='data'
        ),
        title="Interacción de Cargas Eléctricas con Distancias",
        showlegend=True,
        margin=dict(l=0, r=0, b=0, t=40) #márgenes alrededor del gráfico
    )

    # Muestra el gráfico en la interfaz de Streamlit
    st.plotly_chart(fig, use_container_width=True)
