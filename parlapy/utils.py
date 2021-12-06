import pandas as pd
from .models import *
from typing import *

def filter_method(obj, param: str):

    def method(query):

        obj.params.update({obj.param_map[param]: query})

        return obj

    return method

def to_dataframe(motions: List[Motion], by='document'):

    df = pd.DataFrame.from_records([motion.to_dict() for motion in motions])

    # Create a dataframe
    if by == 'document':
        
        return df

    # Explode row of authors to long format
    elif by == 'author':

        pf = pd.concat(
            df['authors'].apply(pd.DataFrame).tolist(), 
            keys=df.index)\
                .droplevel(1)\
                .rename({'name': 'author'})
        
        # Join on index and then reindex
        # Use doc_id to group
        df = df.drop(['authors'], axis=1).join(pf).reset_index(drop=True)

        return df

    else:
        raise ValueError

