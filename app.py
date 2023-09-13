#!/usr/bin/env python
# coding: utf-8

# In[4]:


#!pip install streamlit


# In[3]:


import streamlit as st
import pickle
import numpy as np

# Cargar el modelo entrenado
with open('modelo_entrenado_XGB.pkl', 'rb') as model_file:
    modelo = pickle.load(model_file)

st.title('Aplicación de Predicción')

# Interfaz de usuario
sepal_length = st.slider('Longitud del Sépalo', 0.0, 10.0, 5.0)
sepal_width = st.slider('Ancho del Sépalo', 0.0, 10.0, 3.0)
petal_length = st.slider('Longitud del Pétalo', 0.0, 10.0, 2.0)
petal_width = st.slider('Ancho del Pétalo', 0.0, 10.0, 1.0)

features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])

if st.button('Realizar Predicción'):
    predicciones = modelo.predict(features)
    st.write(f'Clase predicha: {predicciones[0]}')

