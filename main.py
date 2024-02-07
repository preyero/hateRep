import os
import pandas as pd
from typing import List, Dict
from collections import defaultdict

import scripts.dataCollect as dc
from scripts.dataCollect import load_hateRep
from scripts.agreement import get_scores_and_delta, keep_by_annotation_count
from scripts.helper import define_expert, pearson_correlation
from scripts.utils import export_table_plot


PROJ_DIR = os.getcwd()
U_PATH = os.path.join(PROJ_DIR, 'annotators')
D_PATH = os.path.join(PROJ_DIR, 'data')


################################################
# Import data
################################################

data, samples, users = load_hateRep(u_path=U_PATH, d_path=D_PATH)
print('Imported data with samples, annotations, and user tables')


################################################
# Analysis on all annotations
################################################

example = data[['Question ID', 'User', 'gender_1']].sample(10)
print(example)

# TABLE 1.1: Inter-annotator agreement scores and delta between phases
def analyse_IAA(df: pd.DataFrame, score: str, order_by: Dict[str, pd.DataFrame] = None):
    """ Compute a dictionary with tables of scores of binary categories and generic questions """
    table_1, values, table_1_cols = {}, defaultdict(dict), ['Ph1', 'Ph2', 'Δ']
    # from gender and sexuality binary categories
    for g in dc.TARGET_GROUPS:
        for sg in dc.TARGET_LABELS[g]:
            values[g][sg] = get_scores_and_delta(df, score, sg)
        table_1[g] = pd.DataFrame.from_dict(values[g], orient='index', columns=table_1_cols)
    # from the other data annotations
    for label in dc.TARGET_GROUPS + dc.HATE_QS:
        values['other'][label] = get_scores_and_delta(df, score, label)
    table_1['other'] = pd.DataFrame.from_dict(values['other'], orient='index', columns=table_1_cols)
    # sort values by custom list or by delta
    for t in table_1.keys():
        if order_by and t in order_by.keys():
            table_1[t] = table_1[t].reindex(order_by[t].index.to_list())
        else:
            table_1[t].sort_values(by='Δ', inplace=True) 
    return table_1

# Krippendorff's Alpha 
print('... unique texts (Krippendorff)', len(data['Question ID'].unique()))
table_1_alpha = analyse_IAA(data, 'krippendorf')

# Fleiss Kappa scores keeping only those with 6 annotations
d_filter = keep_by_annotation_count(df=data, by='Question ID', n_counts=6, method='filter') 
print('... unique texts (Fleiss)', len(d_filter['Question ID'].unique()))

# table_1_kappa = analyse_IAA(d_filter, 'fleiss', table_1_alpha)

# TODO: TABLE 1.2: Consistency distribution and table counts for understanding IAA
if not os.path.exists('results'):
    os.mkdir('results')
def analyse_consistency(labels: List[str]):
    # for each binary categories
    # ... ( get scores )
    # plot and export distribution with subfigures (consistency_{labels})
    # ... is the distribution similar for the ones in each subset?
    # once seen, export json file with label: counts, ids, n_sample_ids
    # ... especially in the extremes, what are the reasons for (yes/no) changing? considering texts and list of labels
    return

# Reasons for low agreement
low_agreement = ['heterosexual', 'sexuality_unclear', 'gender_unclear']
analyse_consistency(labels=low_agreement)

# Reasons for lower agreement with semantics
lower_with_semantics = ['asexual', 'non-binary', 'gender_other']
analyse_consistency(labels=lower_with_semantics)

analyse_consistency(labels=[sg for sg in dc.TARGET_LABELS['gender'] if sg not in low_agreement+lower_with_semantics])
analyse_consistency(labels=[sg for sg in dc.TARGET_LABELS['sexuality'] if sg not in low_agreement+lower_with_semantics])

################################################
# Analysis by subgroups
################################################

# TABLE 2: Disaggregated IAA scores and correlation with target groups
def subgroup_analysis(df: pd.DataFrame, score: str, categories: List[int], order_by: pd.DataFrame = None):
    """ Compute a list of resulting dataframes: with IAA and correlation (R and p-val) on each phase """
    values = defaultdict(dict)
    for c in categories:
        print(df[c].value_counts())
        for sc in df[c].unique():
            # for every value in the category
            subset, alphas_1, alphas_2 = df.loc[df[c] == sc], [], []
            for sg in dc.TARGET_LABELS[g]:
                alpha_1, alpha_2, _ = get_scores_and_delta(subset, score, sg)
                alphas_1.append(alpha_1)
                alphas_2.append(alpha_2)
            values['alpha_1'][sc], values['alpha_2'][sc] = alphas_1, alphas_2
        # alignment with highest target group in category c
        for p in dc.PHASES:
            for i, sg in enumerate(dc.TARGET_LABELS[g]):
                # target group with highest agreement on sg label
                target = define_expert(values[f'alpha_{p}'], i, c) 
                target_subset = df.loc[df[c] == target]
                for src in df[c].unique():
                    src_subset = df.loc[df[c] == src] 
                    pearson = pearson_correlation(src_subset, target_subset, f'{sg}_{p}', 'Question ID') # how much they align with it
                    try:
                        values[f'r_{p}'][src].append(pearson.statistic)
                        values[f'p_{p}'][src].append(pearson.pvalue)
                    except KeyError:
                        values[f'r_{p}'][src], values[f'p_{p}'][src] = [pearson.statistic], [pearson.pvalue]

    # index names and sort by of (6 tables: alpha, R, p_val for each phase)
    res_df =  [pd.DataFrame.from_dict(values[k]) for k in values.keys()]
    for i in range(0, len(res_df)):
        res_df[i].index = dc.TARGET_LABELS[g]
        if isinstance(order_by, pd.DataFrame):
            res_df[i] = res_df[i].reindex(order_by.index.to_list())
    return res_df

# Krippendorff's Alpha and Pearson Correlation
table_2 = {}
hide_rows = {'gender':['gender_other', 'non-binary', 'gender_unclear'], 
             'sexuality': ['asexual', 'sexuality_unclear']}
for g in dc.TARGET_GROUPS:
    # of annotator demographics
    results = subgroup_analysis(data, 'krippendorf', dc.CATEG.values(), order_by=table_1_alpha[g])
    table_2[f'{g}_alpha_1'], table_2[f'{g}_alpha_2'], table_2[f'{g}_r_1'], table_2[f'{g}_p_1'], table_2[f'{g}_r_2'], table_2[f'{g}_p_2'] = results

    # Table plots
    cols = ['nonLGBT', 'LGBT', 'M', 'W', 'S', 'G']
    for p in dc.PHASES:
        export_table_plot(cell_values_df=table_2[f'{g}_alpha_{p}'][cols], 
                          color_values_df=table_2[f'{g}_r_{p}'][cols], 
                          pdf_filename=f'results/krippendorff_with_pearson_pval_{g}_{p}_{'_'.join(cols)}.pdf', 
                          boldface_ranges=[0, 2, 6], 
                          p_values_df=table_2[f'{g}_p_{p}'][cols])

        # hide rows
        n_rows = 7 - len(hide_rows[g])
        export_table_plot(cell_values_df=table_2[f'{g}_alpha_{p}'][cols], 
                          color_values_df=table_2[f'{g}_r_{p}'][cols], 
                          pdf_filename=f'results/krippendorff_with_pearson_pval_increase_{g}_{p}_{'_'.join(cols)}.pdf', 
                          boldface_ranges=[0, 2, 6], 
                          p_values_df=table_2[f'{g}_p_{p}'][cols], 
                          hide_rows=hide_rows[g], 
                          figsize=(10, 7 - len(hide_rows[g])))    
    
    # hide columns
    # plot_1, plot_2 = ['nonLGBT', 'M', 'W',], ['LGBT', 'S', 'G'] 
    # export_table_plot(cell_values_df=table_2[f'{g}_alpha'][plot_1], color_values_df=table_2[f'{g}_delta'][plot_1], pdf_filename=f'results/krippendorff_{g}_{'_'.join(plot_1)}.pdf')
    # export_table_plot(cell_values_df=table_2[f'{g}_alpha'][plot_2], color_values_df=table_2[f'{g}_delta'][plot_2], pdf_filename=f'results/krippendorff_{g}_{'_'.join(plot_2)}.pdf')


