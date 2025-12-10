
import pandas as pd
import io
import os
import uuid

"""
    Cleans the given DataFrame by performing the following operations:
    - Removes duplicate rows.
    - Cleans column names by stripping whitespace, converting to lowercase, and replacing spaces with underscores
    - Handles missing values by filling numeric columns with 0 and non-numeric columns with N/D
    - Strips whitespace from string columns
"""

UPLOAD_FOLDER = 'datasets'

def save_dataset(df: pd.DataFrame, filename) -> str:

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    clean_filename = filename.replace(" ", "_") 
    file_id = f"{uuid.uuid4()}-{clean_filename}"

    file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.csv")
    
    df.to_csv(file_path, index=False)
    
    return file_id

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:

    df.columns = (df.columns
                  .str.strip()
                  .str.lower()
                  .str.replace(' ', '_')
                  .str.replace(r'[^\w]', '', regex=True))
    return df

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    
    # 1. Standardize column names
    df = standardize_column_names(df)

    # 2. remove duplicate rows
    df = df.drop_duplicates()

    # 3. remove rows that are completely empty
    df = df.dropna(how='all')

    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    return df

def csv_to_dataframe(file) -> dict | None:

    try:

        file_content = file.read()
        
        # build DataFrame from CSV content
        df = pd.read_csv(io.BytesIO(file_content))

        # clean the DataFrame
        df_cleaned = clean_dataframe(df)

        # Build response data
        preview_df = df_cleaned.head(5)
        preview_safe = preview_df.where(pd.notnull(preview_df), None)

        # Build response data
        response_data = {
            "messaggio": "File elaborato con successo (Backend Flask)",
            "righe_originali": len(df),
            "righe_finali": len(df_cleaned),
            "colonne": list(df_cleaned.columns),
            "anteprima_dati": preview_safe.to_dict(orient="records")
        }
        return response_data, df_cleaned

    except Exception as e:
        print(f"Errore: {e}")
        return None, None
    

# Business-logic API2:  Analisi del dataset per proposta modello da usare 

def suggest_models(df, target=None):
    models = []

    if target is None:
        # Nessun target → clustering
        if df.shape[1] > 2: #columns > 2
            models.append("KMeans")
            models.append("DBSCAN")
        else:
            models.append("AgglomerativeClustering")
    else:
        target_dtype = df[target].dtype #taking the column type: if numeric--> regr; if categ--> class.
        if target_dtype in ['int64', 'float64']:
            # Regressione
            models.append("LinearRegression")
            if df.shape[0] > 1000:
                models.append("RandomForestRegressor")
                models.append("XGBoostRegressor")
        elif target_dtype == 'object' or df[target].nunique() < 20: #pd.nuniqie() conta categorie in una colonna
            # Classificazione
            if df[target].nunique() == 2:
                models.append("LogisticRegression")
                models.append("RandomForestClassifier")
            else:
                models.append("MultinomialLogisticRegression")
                models.append("GradientBoostingClassifier")

    return models