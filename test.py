import sys, os
import numpy as np
import pandas as pd

SAVE_PATH = os.path.expanduser('Documents/Boenderne')


PLAYERS = pd.DataFrame({
    'id': pd.Series(dtype='str'),
    'name': pd.Series(dtype='str'),
    'rating': pd.Series(dtype='int'),
    'oversidder': pd.Series(dtype='boolean')
})
MATCHES = pd.DataFrame({
    'p1Id': pd.Series(dtype='str'),
    'p2Id': pd.Series(dtype='str'),
    'winnerId': pd.Series(dtype='str'),
    'p1Rating': pd.Series(dtype='int'),
    'p2Rating': pd.Series(dtype='int')
})

def load_db():
    if os.path.exists(os.path.join(SAVE_PATH, 'PLAYERS.csv')):
        PLAYERS = pd.read_csv(os.path.join(SAVE_PATH, 'PLAYERS.csv'))
    if os.path.exists(os.path.join(SAVE_PATH, 'MATCHES.csv')):
        MATCHES = pd.read_csv(os.path.join(SAVE_PATH, 'MATCHES.csv'))

def save_db():
    if not os.path.isdir(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    PLAYERS.to_csv(path_or_buf=os.path.join(SAVE_PATH, 'PLAYERS.csv'))
    MATCHES.to_csv(path_or_buf=os.path.join(SAVE_PATH, 'MATCHES.csv'))

print(os.path.join(SAVE_PATH, 'PLAYERS.csv'))
#load_db()
#save_db()