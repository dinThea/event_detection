import requests
import pandas as pd
import re
import os
import json
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from src.gstorage import download

def fetch_events(user, pwd, day):

    auth = {'user':user, 'pwd':pwd}
    with requests.post('https://cliente.visio.ai/api/auth/login', json=auth) as res:
        if res.status_code == requests.codes.ok:
            print("Login succed", flush=True)
            auth = res.json()
            token = auth['token']
            request_header = {"Authorization": "Bearer {}".format(token)}
            results = requests.get(f'https://cliente.visio.ai/api/review/subway-iguatemi-saocarlos/balcao/{day.replace("-","")}', headers=request_header)
            
            return results

def clear_events(events, filtered=False, for_review=False):
    
    purchases = [event for event in events['eventos_aceitos'] if 'a' not in event['_id'] and 'b' not in event['_id']] 
    regular_events = [event for event in events['eventos_rejeitados'] if 'a' not in event['_id'] and 'b' not in event['_id']]
    if filtered:
        regular_events += [event for event in events['eventos_rejeitados_filtro'] if 'a' not in event['_id'] and 'b' not in event['_id']]
    if for_review:
        regular_events += [event for event in events['eventos_nao_revisados'] if 'a' not in event['_id'] and 'b' not in event['_id']] 
    
    return purchases, regular_events

def load_csv_and_create_dataframe(events, y, origin=None):

    big_df = pd.DataFrame(columns=['id','day','pos','purchase']) if not isinstance(origin, pd.DataFrame) else origin
    available_files = os.listdir('data')
    i = big_df.shape[0]
    
    for event in events:

        pattern = re.compile(r'https:\/\/storage\.googleapis\.com/(.*)\/(.*)\/(.*)')
        found = list(re.findall(pattern, event['link_bucket'][0]))[0]
        
        if 'X0' in event['link_bucket'][0]:
            continue
        if f"{event['_id']}.csv" not in available_files: 
            try:
                download(found[0], f'{found[1]}/{found[2].replace(".mp4", ".csv")}', f'data/{found[2].replace(".mp4", ".csv")}')
            except:
                continue
        try:
            df_event = pd.read_csv(f'data/{found[2].replace(".mp4", ".csv")}')
            df_event['bbox'].apply(lambda x: list(tuple (x)))
        except:
            continue
        big_df.loc[i] = [event['_id'], found[1], df_event['bbox'].to_list(), y]
        i+=1
    
    return big_df    

def load_credentials():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials_gcp.json'

if __name__ == '__main__':


    load_credentials()

    credentials = {}
    with open('credentials_visio.json') as creds:
        credentials = json.load(creds)
    purchases, regular_events = clear_events(fetch_events(credentials['user'], credentials['pwd'], '20200119').json()[0])
    data = load_csv_and_create_dataframe(purchases, 1)
    data = load_csv_and_create_dataframe(regular_events, 0, data)

    data.to_csv('teste.csv')
