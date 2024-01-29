import os
import pandas as pd

import scripts.dataCollect as dc
from scripts.dataCollect import load_hateRep
from scripts.agreement import get_scores_and_delta
from scripts.utils import export_table_plot
from scripts.agreement import keep_by_annotation_count

PROJ_DIR = os.getcwd()
U_PATH = os.path.join(PROJ_DIR, 'annotators')
D_PATH = os.path.join(PROJ_DIR, 'data')


################################################
# Import data
################################################

data, samples, users = load_hateRep(u_path=U_PATH, d_path=D_PATH)

print('Imported data with samples, annotations, and user tables')


################################################
# Agreement: Krippendorff's Alpha
################################################

example = data[['Question ID', 'User', 'gender_1']].sample(10)
print(example)
print('... unique texts', len(data['Question ID'].unique()))

# TABLE 1: including all annotations, Krippendorff's Alpha scores and delta between phases
tables_1, table_1_cols = {}, ['Ph1', 'Ph2', 'Δ']
# from gender and sexuality binary categories
for g in dc.TARGET_GROUPS:
    values = {}
    for sg in dc.TARGET_LABELS[g]:
        values[sg] = get_scores_and_delta(data, 'krippendorf', sg)
    tables_1[g] = pd.DataFrame.from_dict(values, orient='index', columns=table_1_cols)
# from the other data annotations
values = {}
for label in dc.TARGET_GROUPS + dc.HATE_QS:
    values[label] = get_scores_and_delta(data, 'krippendorf', label)
tables_1['other'] = pd.DataFrame.from_dict(values, orient='index', columns=table_1_cols)
# sort values by delta
[tables_1[t].sort_values(by='Δ', inplace=True) for t in tables_1.keys()]

# TABLE 2: Krippendorff's Alpha delta scores disaggregated by annotator demographics
if not os.path.exists('figures'):
    os.mkdir('figures')
tables_2 = {}
for g in dc.TARGET_GROUPS:
    values_alpha, values_delta = {}, {}
    # of annotator demographics
    for c in dc.CATEG.values():
        print(data[c].value_counts())
        for sc in data[c].unique():
            # for every value in the category
            subset, alphas_2, deltas = data.loc[data[c] == sc], [], []
            for sg in dc.TARGET_LABELS[g]:
                _, alpha_2, delta = get_scores_and_delta(subset, 'krippendorf', sg)
                alphas_2.append(alpha_2)
                deltas.append(delta)
            values_alpha[sc], values_delta[sc] = alphas_2, deltas
    tables_2[f'{g}_alpha'], tables_2[f'{g}_delta'] = pd.DataFrame.from_dict(values_alpha), pd.DataFrame.from_dict(values_delta)
    # TODO: of personal experiences (bootstrapping?)
    # index labels and same order as tables 1
    for t in ['alpha', 'delta']: 
        tables_2[f'{g}_{t}'].index = dc.TARGET_LABELS[g]
        tables_2[f'{g}_{t}'] = tables_2[f'{g}_{t}'].reindex(tables_1[g].index.to_list())

    # Table plots
    # TODO: also do table with personal experience (of yes/no, and by 4 subcategories)
    cols = ['nonLGBT', 'LGBT', 'M', 'W', 'S', 'G']
    # plot_1, plot_2 = ['nonLGBT', 'M', 'W',], ['LGBT', 'S', 'G']
    export_table_plot(cell_values_df=tables_2[f'{g}_alpha'][cols], color_values_df=tables_2[f'{g}_delta'][cols], pdf_filename=f'figures/krippendorff_{g}_{'_'.join(cols)}.pdf')
    # export_table_plot(cell_values_df=tables_2[f'{g}_alpha'][plot_1], color_values_df=tables_2[f'{g}_delta'][plot_1], pdf_filename=f'figures/krippendorff_{g}_{'_'.join(plot_1)}.pdf')
    # export_table_plot(cell_values_df=tables_2[f'{g}_alpha'][plot_2], color_values_df=tables_2[f'{g}_delta'][plot_2], pdf_filename=f'figures/krippendorff_{g}_{'_'.join(plot_2)}.pdf')
    
################################################
# Agreement: Fleiss Kappa
################################################ 
# Case a: keep only those with 6 annotations
d_filter = keep_by_annotation_count(df=data, by='Question ID', n_counts=6, method='filter') 
print('... unique texts', len(d_filter['Question ID'].unique()))
# Case b: undersample to 5 annotations  
d_downsample = ... 

tables_1_kappa = {}
# from gender and sexuality binary categories
for g in dc.TARGET_GROUPS:
    val_filter = {}
    for sg in dc.TARGET_LABELS[g]:
        val_filter[sg] = get_scores_and_delta(d_filter, 'fleiss', sg)
    tables_1_kappa[f'{g}_filter'] = pd.DataFrame.from_dict(val_filter, orient='index', columns=table_1_cols)
# from the other data annotations
val_filter = {}
for label in dc.TARGET_GROUPS + dc.HATE_QS:
    val_filter[label] = get_scores_and_delta(d_filter, 'fleiss', label)
tables_1_kappa['other_filter'] = pd.DataFrame.from_dict(val_filter, orient='index', columns=table_1_cols)
# sort values by delta
[tables_1_kappa[t].sort_values(by='Δ', inplace=True) for t in tables_1_kappa.keys()]
          

print('')

################################################
# Confidence
################################################



################################################
# Coverage
################################################





################################################
# Quality
################################################
