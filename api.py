import pandas as pd
import numpy as np
import re

def cleansing_text(text):
    abusive = pd.read_csv("static/abusive.csv", encoding='utf-8', error_bad_lines=False)
    abusive_arr = abusive.to_numpy()
    # abusive_dict = dict(zip(abusive))

    kamusalay = pd.read_csv('static/new_kamusalay.csv', encoding='latin-1', names=['old','new'])
    kamusalay_arr = kamusalay.to_numpy()
    # kamusalay_dict = dict(zip(kamusalay['old'], kamusalay['new']))
    
    text = re.split(' ', text.lower())
    #Abusive cleansing
    for i in text:
        for j in abusive_arr:
            if i == j:
                index = text.index(i)
                text[index] = '**sensor**'
                
    #Kamus alay cleansing      
    for x in text:
        for y in kamusalay_arr:
            if x == y[0]:
                index = text.index(x)
                text[index] = y[1]
                
    text = ' '.join(text)
    return text