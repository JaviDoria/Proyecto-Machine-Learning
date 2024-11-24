import streamlit as st
import pickle
import pandas as pd

# Cargar el modelo y el escalador desde archivos
with open('LogisticRegression.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Título de la aplicación
st.title('Predicción de Suscripción a Depósito a Plazo')

# Entrada de datos demográficos del usuario
st.header('Información Personal')

age = st.number_input('Edad:', min_value=16, max_value=125)

job = st.selectbox('Trabajo:', 
                   ('management', 'blue-collar', 'technician', 'admin.', 
                    'services', 'housemaid', 'self-employed', 'entrepreneur',
                    'unemployed', 'retired', 'student', 'unknown'))

marital = st.radio('Estado Civil:', ['casado','soltero'])

education = st.radio('Nivel Educativo:', ['primaria', 'secundaria', 'terciaria'])

# Entrada de datos financieros del usuario
st.header('Datos Financieros')

balance = st.number_input('Saldo:')

default = st.radio('Incumplimiento de Crédito:', ['no', 'sí'])

housing = st.radio('Préstamo Hipotecario:', ['no', 'sí'])

loan = st.radio('Préstamo Personal:', ['no', 'sí'])

pdays = st.number_input('Días desde el último contacto:')


# Crear un DataFrame con las entradas
user_data = pd.DataFrame({
    'age': [age],
    'education': [education],
    'default': [default],
    'balance': [balance],
    'housing': [housing],
    'loan': [loan],
    'pdays': [pdays],
    'job': [job],
    'marital': [marital],
})

# Codificación de las características 'default', 'housing', 'loan' y 'education'
user_data['default'] = user_data['default'].map({'no': 0, 'sí': 1}).astype(int)
user_data['housing'] = user_data['housing'].map({'no': 0, 'sí': 1}).astype(int)
user_data['loan'] = user_data['loan'].map({'no': 0, 'sí': 1}).astype(int)
user_data['education'] = user_data['education'].map({'primaria': 1, 'secundaria': 2, 'terciaria': 3}).astype(int)

# Mapeo del 'job' (One-Hot Encoding)
grouped_jobs = {'management': 'office',
                'admin.': 'office',
                'blue-collar': 'blue-collar',
                'technician': 'blue-collar',
                'services': 'service',
                'housemaid': 'service',
                'self-employed': 'self-employed',
                'entrepreneur': 'self-employed',
                'unemployed': 'unemployed',
                'student': 'student',
                'unknown': 'other'}

user_data['job'] = user_data['job'].map(grouped_jobs)

# Codificación One-Hot de las características 'job' y 'marital'
user_encoded_data = pd.get_dummies(user_data, columns=['job', 'marital'])
user_encoded_data = user_encoded_data.astype(int)  # Para transformar el resultado de dummies False/True a binario 0/1

# Verificar las columnas que el modelo y el escalador esperan
# model_columns = model.feature_names_in_  # Las columnas que el modelo espera
# scaler_columns = scaler.feature_names_in_  # Las columnas que el escalador espera

st.write("Columnas del modelo:", model_columns)
st.write("Columnas del escalador:", scaler_columns)

# Asegurar que las columnas necesarias estén presentes
required_columns = set(model_columns)  # O usar scaler_columns si prefieres las columnas del escalador

# Agregar columnas faltantes con valor 0
for col in required_columns:
    if col not in user_encoded_data.columns:
        user_encoded_data[col] = 0

# Asegurarse de que las columnas estén en el orden correcto
user_encoded_data = user_encoded_data[model_columns]

# Verificar que las columnas 'age' y 'balance' estén presentes en el DataFrame antes de la estandarización
if 'age' not in user_encoded_data.columns or 'balance' not in user_encoded_data.columns:
    st.error("Las columnas 'age' y 'balance' deben estar presentes para la estandarización.")
else:
    # Estandarizar las entradas de edad y saldo usando el escalador cargado
    scale_variable = ['age', 'balance']
    user_encoded_data[scale_variable] = scaler.transform(user_encoded_data[scale_variable])

# Realizar la predicción
prediction = model.predict(user_encoded_data)

# Mostrar la predicción
st.header('Resultado de la Predicción')
if prediction == 1:
    st.success('El cliente probablemente SE SUSCRIBIRÁ a un depósito a plazo.')
else:
    st.error('El cliente probablemente NO SE SUSCRIBIRÁ a un depósito a plazo.')
