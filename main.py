import os
import pandas as pd

import scripts.dataCollect as dc
from scripts.dataCollect import load_hateRep
from scripts.agreement import get_alpha_and_deltas

PROJ_DIR = os.getcwd()
U_PATH = os.path.join(PROJ_DIR, 'annotators')
D_PATH = os.path.join(PROJ_DIR, 'data')


################################################
# Import data
################################################

data, samples, users = load_hateRep(u_path=U_PATH, d_path=D_PATH)

print('Imported data with samples, annotations, and user tables')


################################################
# Agreement
################################################

example = data[['Question ID', 'User', 'gender_1']].sample(10)
print(example)

# TABLE 1: including all annotations, Krippendorff's Alpha scores and delta between phases
tables_1, table_1_cols = {}, ['Ph1', 'Ph2', 'Δ']
# from gender and sexuality binary categories
for g in dc.TARGET_GROUPS:
    values = {}
    for sg in dc.TARGET_LABELS[g]:
        values[sg] = get_alpha_and_deltas(data, sg)
    tables_1[g] = pd.DataFrame.from_dict(values, orient='index', columns=table_1_cols)

# from the other data annotations
values = {}
for label in dc.TARGET_GROUPS + dc.HATE_QS:
    values[label] = get_alpha_and_deltas(data, label)
tables_1['Other'] = pd.DataFrame.from_dict(values, orient='index', columns=table_1_cols)

[tables_1[t].sort_values(by='Δ', inplace=True) for t in tables_1.keys()]

# TABLE 2: Krippendorff's Alpha delta scores disaggregated by annotator demographics
tables_2 = {}
for g in dc.TARGET_GROUPS:
    values = {}
    for c in dc.CATEG.values():
        print(data[c].value_counts())
        for sc in data[c].unique():
            # for every value in the category
            subset, deltas = data.loc[data[c] == sc], []
            for sg in dc.TARGET_LABELS[g]:
                deltas.append(round(get_alpha_and_deltas(subset, sg)[-1], 3))
            values[sc] = deltas
    tables_2[g] = pd.DataFrame.from_dict(values)
    tables_2[g].index = dc.TARGET_LABELS[g]
    # same order as tables 1
    tables_2[g] = tables_2[g].reindex(tables_1[g].index.to_list())
            

################################################
# Confidence
################################################



################################################
# Coverage
################################################





################################################
# Quality
################################################
