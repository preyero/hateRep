import os
import pandas as pd
from typing import List, Dict

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
def compute_table_1(df: pd.DataFrame, score: str, order_by: Dict[str, pd.DataFrame] = None):
    """ Compute a dictionary with tables of scores of subgroup categories and generic questions """
    table_1, table_1_cols = {}, ['Ph1', 'Ph2', 'Δ']
    # from gender and sexuality binary categories
    for g in dc.TARGET_GROUPS:
        values = {}
        for sg in dc.TARGET_LABELS[g]:
            values[sg] = get_scores_and_delta(df, score, sg)
        table_1[g] = pd.DataFrame.from_dict(values, orient='index', columns=table_1_cols)
    # from the other data annotations
    values = {}
    for label in dc.TARGET_GROUPS + dc.HATE_QS:
        values[label] = get_scores_and_delta(df, score, label)
    table_1['other'] = pd.DataFrame.from_dict(values, orient='index', columns=table_1_cols)
    # sort values by custom list or by delta
    for t in table_1.keys():
        if order_by and t in order_by.keys():
            table_1[t] = table_1[t].reindex(order_by[t].index.to_list())
        else:
            table_1[t].sort_values(by='Δ', inplace=True) 
    return table_1

table_1_alpha = compute_table_1(data, 'krippendorf')

# include also Fleiss Kappa scores
# case a: keep only those with 6 annotations
d_filter = keep_by_annotation_count(df=data, by='Question ID', n_counts=6, method='filter') 
print('... unique texts', len(d_filter['Question ID'].unique()))
# case b: undersample to 5 annotations  
d_downsample = ... 

table_1_kappa = compute_table_1(d_filter, 'fleiss', table_1_alpha)


# TABLE 2: Krippendorff's Alpha delta scores disaggregated by annotator demographics
def compute_table_2(df: pd.DataFrame, score: str, categories: List[int], binary: bool = False, order_by: pd.DataFrame = None):
    """ Compute table of scores in data categories """
    values_alpha, values_delta = {}, {}
    for c in categories:
        print(df[c].value_counts())
        for sc in df[c].unique():
            # for every value in the category
            subset, alphas_2, deltas = df.loc[df[c] == sc], [], []
            for sg in dc.TARGET_LABELS[g]:
                _, alpha_2, delta = get_scores_and_delta(subset, score, sg)
                alphas_2.append(alpha_2)
                deltas.append(delta)
            tag = [f'{c}-{sc}\n{subset.shape[0]}' if binary else sc]
            values_alpha[tag[0]], values_delta[tag[0]] = alphas_2, deltas
    # index names and sort by
    res_df =  [pd.DataFrame.from_dict(values_alpha), pd.DataFrame.from_dict(values_delta)]
    for i in range(0, len(res_df)):
        res_df[i].index = dc.TARGET_LABELS[g]
        if isinstance(order_by, pd.DataFrame):
            res_df[i] = res_df[i].reindex(order_by.index.to_list())
    return res_df


if not os.path.exists('figures'):
    os.mkdir('figures')
table_2 = {}
for g in dc.TARGET_GROUPS:
    # of annotator demographics
    table_2[f'{g}_alpha'], table_2[f'{g}_delta'] = compute_table_2(data, 'krippendorf', dc.CATEG.values(), order_by=table_1_alpha[g])
    # of personal experiences
    table_2[f'{g}_PE_alpha'], table_2[f'{g}_PE_delta'] = compute_table_2(data, 'krippendorf', [dc.COFACT[f'f6.{n}'] for n in range(1, 5)], binary=True, order_by=table_1_alpha[g])
    # index labels and same order as tables 1

    # Table plots
    cols = ['nonLGBT', 'LGBT', 'M', 'W', 'S', 'G']
    # plot_1, plot_2 = ['nonLGBT', 'M', 'W',], ['LGBT', 'S', 'G']
    export_table_plot(cell_values_df=table_2[f'{g}_alpha'][cols], color_values_df=table_2[f'{g}_delta'][cols], pdf_filename=f'figures/krippendorff_{g}_{'_'.join(cols)}.pdf')
    # export_table_plot(cell_values_df=table_2[f'{g}_alpha'][plot_1], color_values_df=table_2[f'{g}_delta'][plot_1], pdf_filename=f'figures/krippendorff_{g}_{'_'.join(plot_1)}.pdf')
    # export_table_plot(cell_values_df=table_2[f'{g}_alpha'][plot_2], color_values_df=table_2[f'{g}_delta'][plot_2], pdf_filename=f'figures/krippendorff_{g}_{'_'.join(plot_2)}.pdf')
    export_table_plot(cell_values_df=table_2[f'{g}_PE_alpha'], color_values_df=table_2[f'{g}_PE_delta'], pdf_filename=f'figures/krippendorff_{g}_personal-experience.pdf')
# TODO: why not possible to show tables in viewer after running this code (comment for now)   

################################################
# Confidence
################################################



################################################
# Coverage
################################################





################################################
# Quality
################################################
