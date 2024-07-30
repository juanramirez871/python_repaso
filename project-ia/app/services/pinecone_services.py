from pinecone import ServerlessSpec
import time
import pandas as pd
import os

def create_index(index_name, pinecone):
    try:
        pinecone.describe_index(index_name)
    except:
        pinecone.create_index(
            index_name,
            dimension=768,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws', 
                region='us-east-1'
            ) 
        )
        
def insert_vector(index, vector, metadata):
    upsert_response = index.upsert(
        vectors=[
            {
                'id': str(time.time() * 1000),
                'values': vector.tolist(),
                'metadata': metadata
            }
        ],
        namespace=metadata['from']
    )
    
    return upsert_response

def get_all_vectors_by_number(index, number_phone):
    
        my_number = my_number = os.getenv("MY_NUMBER")
        ids_from = [id_vector for id_vector in index.list(namespace=number_phone)][0]
        ids_to = [id_vector for id_vector in index.list(namespace=my_number)][0]
        all_ids = list(set(ids_from + ids_to))
        
        vectors = index.fetch(ids=all_ids, namespace=number_phone)['vectors']
        conversations = []
        for id_vector in all_ids:
            metadata = vectors[id_vector]['metadata']
            conversations.append({
                "from": metadata['from'],
                "to": metadata['to'],
                "created_at": metadata['created_at'],
                "message": metadata['message']
            })
        
        df = pd.DataFrame(conversations)
        df['created_at'] = pd.to_datetime(df['created_at'], format='%d/%m/%Y %H:%M:%S')
        df_sorted = df.sort_values(by='created_at')
        messages = df_sorted.to_dict(orient='records')
        return messages