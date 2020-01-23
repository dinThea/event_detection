#!/usr/bin/env python
# coding: utf-8

# In[2]:


from fetch_data import fetch_events, clear_events, load_csv_and_create_dataframe, load_credentials
import numpy as np
import json
from matplotlib import pyplot as plt
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, LSTM, GlobalMaxPooling1D, SpatialDropout1D
plt.style.use('dark_background')


# In[3]:


load_credentials()
credentials = {}
with open('credentials_visio.json') as creds:
    credentials = json.load(creds)
purchases, regular_events = clear_events(fetch_events(credentials['user'], credentials['pwd'], '20200119').json()[0])
data = load_csv_and_create_dataframe(purchases, 1)
data = load_csv_and_create_dataframe(regular_events, 0, data)


# In[4]:


new_data = data.copy()
new_data['pos'] = new_data['pos'].apply(lambda x: np.array([list(map(float, value.replace('(','[').replace(')',']').replace('[','').replace(']','').split(', '))) for value in x]))
new_data['len'] = new_data['pos'].apply(len) 

max_phrase_len = new_data['len'].max()
feature_dimention = 4


# In[5]:


plt.figure(figsize = (10, 8))
plt.hist(new_data['len'], alpha = 0.2, density = True)
plt.xlabel('phrase len')
plt.ylabel('probability')
plt.grid(alpha = 0.25)


# In[6]:


y_train = new_data['purchase']
X_train = pad_sequences(new_data['pos'], maxlen = max_phrase_len)
y_train = to_categorical(y_train)


# In[7]:


batch_size = 512
epochs = 8


# In[8]:


model_lstm = Sequential()
# model_lstm.add(Embedding(input_dim = 4, output_dim = 256, input_length = max_phrase_len))
# model_lstm.add(SpatialDropout1D(0.3))
model_lstm.add(LSTM(256, input_shape=(max_phrase_len, 4)))

model_lstm.add(Dense(256, activation = 'relu'))
model_lstm.add(Dropout(0.5))
model_lstm.add(Dense(10, activation='softmax'))

model_lstm.compile(
    loss='sparse_categorical_crossentropy',
    optimizer='Adam',
    metrics=['accuracy']
)


# In[1]:


history = model_lstm.fit(
    X_train,
    y_train,
    validation_split = 0.1,
    epochs = epochs,
    batch_size = batch_size,
    verbose=1
)


# In[ ]:




