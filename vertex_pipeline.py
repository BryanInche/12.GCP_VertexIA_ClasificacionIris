import kfp.dsl as dsl   # Esta biblioteca es parte de la versión anterior de Kubeflow Pipelines
from kfp.v2 import dsl as v2_dsl  # Ayuda a definir componentes de pipeline, flujos de trabajo y tareas de manera programática 
from google.cloud import aiplatform  # Se utiliza para interactuar con los servicios y recursos de Vertex AI, como entrenar modelos, desplegar modelos, administrar flujos de trabajo

# Definimos la función de entrenamiento personalizada
def custom_training_function(project_id: str, input_bucket: str, bq_dataset: str, bq_table: str):
    #input_bucket:ubicación en Google Cloud Storage (GCS) donde se encuentran los datos de entrada
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from google.cloud import bigquery

    # Carga los datos desde GCS (Bucket creado en Google Cloud Storage)
    data = pd.read_csv(f"{input_bucket}/iris.csv")  # Cargamos previo en el bucket la base de iris

    # Realizamos la transformación y preparación de datos
    mapeo_clasificacion = {
        "setosa": 0,
        "versicolor": 1,
        "virginica": 2
    }

    data["Species_encoded"] = data["Species"].map(mapeo_clasificacion)
    X = data[['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width']]
    y = data['Species_encoded']

    # Se divide los datos en conjuntos de entrenamiento y prueba
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=99)

    # Se entrena un modelo de Regresión Logística
    logisticRegr = LogisticRegression(penalty='l2', max_iter=1000)
    logisticRegr.fit(x_train, y_train)

    # Se realiza predicciones en el conjunto de prueba
    y_pred = logisticRegr.predict(x_test)

    # Se almacena las predicciones en una tabla de BigQuery
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(bq_dataset)
    table_ref = dataset_ref.table(bq_table)

    predictions_df = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
    #Se carga el contenido del DataFrame predictions_df en la tabla de BigQuery especificada por table_ref
    predictions_df.to_gbq(destination_table=table_ref, if_exists='replace') 

#Se define un flujo de trabajo de Kubeflow Pipelines utilizando la biblioteca kfp.v2.dsl

#Anotación de decorador que se utiliza para definir un flujo de trabajo de Kubeflow Pipelines
@v2_dsl.pipeline(
    name="custom-ml-pipeline",  # Nombre del flujo de trabajo
    description="A custom machine learning pipeline.",
)

#Función que define el flujo de trabajo: Se personaliza y configura la ejecución del flujo de trabajo
def custom_ml_pipeline(
    project_id: str = "your-project-id",  #Indicamos el nombre del proyecto en Bigquery
    input_bucket: str = "gs://your-input-bucket",  # Indicamos el bucket de donde se traera el dataset
    bq_dataset: str = "your-dataset",   #Nombre del dataset en Bigquery
    bq_table: str = "your-table",     #Nombre de la tabla en Bigquery donde se almacenaran las predicciones
):
    # Definimos el componente personalizado de un trabajo de entrenamiento personalizado para un modelo de ML
    custom_training_component = aiplatform.CustomPythonPackageTrainingJob(
        display_name="custom-training-job", #Nombre útil para identificar el trabajo en el entorno de Vertex AI y Kubeflow Pipelines.
        #Especifica la ubicación en Google Cloud Storage (GCS) del archivo comprimido (por ejemplo, un archivo .tar.gz) que contiene
        #el código fuente y los recursos necesarios para el trabajo de entrenamiento 
        python_package_gcs_uri="gs://your-code-bucket/your-code-container.tar.gz",
        python_module_name="your_custom_module",  # python_module_name debe apuntar al código de entrenamiento del modelo sin .py 

        #Especifica la ubicación del contenedor Docker que se utilizará para ejecutar el código de entrenamiento personalizado:
        # 1.Etiquetar tu contenedor: docker tag <NOMBRE_DEL_CONTENEDOR>:<VERSION> gcr.io/<TU_PROJECT_ID>/<NOMBRE_DEL_CONTENEDOR>:<VERSION>
        # <TU_PROJECT_ID>: El ID de tu proyecto de Google Cloud.
        # Subir el contenedor a Container Registry: docker push gcr.io/<TU_PROJECT_ID>/<NOMBRE_DEL_CONTENEDOR>:<VERSION>
        #Obtener la URL del contenedor: gcr.io/<TU_PROJECT_ID>/<NOMBRE_DEL_CONTENEDOR>:<VERSION>
        container_uri="gcr.io/cloud-aiplatform/training-containers/tf-cpu.2-2:latest",  
        requirements=["numpy", "pandas", "scipy", "scikit-learn", "google-cloud-bigquery"],  # Lista de requerimientos de Python
        args=[
            "--project-id", project_id,
            "--input-bucket", input_bucket,
            "--bq-dataset", bq_dataset,
            "--bq-table", bq_table,
        ],
    )

    # Ejecutamos el componente personalizado
    custom_training_task = custom_training_component()

#El código se encarga de compilar el flujo de trabajo de Kubeflow Pipelines definido en el script en un 
# archivo YAML que puede ser utilizado para ejecutar el flujo de trabajo en el entorno de Kubeflow Pipelines
if __name__ == "__main__":
    from kfp.v2 import compiler
    compiler.Compiler().compile(custom_ml_pipeline, "custom_ml_pipeline.yaml")