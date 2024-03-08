import os, sys
import pandas as pd
from typing import List, Dict
from collections import defaultdict

import scripts.dataCollect as dc
from scripts.dataCollect import load_hateRep
from scripts.agreement import get_scores_and_delta, keep_by_annotation_count
from scripts.helper import define_expert, pearson_correlation
from scripts.helper import define_category, process_rationale
import scripts.utils as u


PROJ_DIR = os.getcwd()
U_PATH = os.path.join(PROJ_DIR, 'annotators')
D_PATH = os.path.join(PROJ_DIR, 'data')


################################################
# Import data
################################################

data, samples, users = load_hateRep(u_path=U_PATH, d_path=D_PATH)
print('Imported data with samples, annotations, and user tables')


################################################
# Inter-annotator agreement scores and delta between phases
################################################

example = data[['Question ID', 'User', 'gender_1']].sample(10)
print(example)

# ANALYSIS 1.1: Inter-annotator agreement scores and delta between phases
def analyse_IAA(df: pd.DataFrame, score: str, order_by: Dict[str, pd.DataFrame] = None):
    """ Compute a dictionary with tables of scores of binary categories and generic questions """
    table_1, values, table_1_cols = {}, defaultdict(dict), ['Ph1', 'Ph2', '$\Delta$']
    # from gender and sexuality binary categories
    for g in dc.TARGET_GROUPS:
        for sg in dc.TARGET_LABELS[g]:
            values[g][sg] = get_scores_and_delta(df, score, sg)
        table_1[g] = pd.DataFrame.from_dict(values[g], orient='index', columns=table_1_cols)
    # from the other data annotations
    for label in [f"{l}_bin" for l in dc.TARGET_GROUPS + dc.HATE_QS]:
        values['other'][label] = get_scores_and_delta(df, score, label)
    table_1['other'] = pd.DataFrame.from_dict(values['other'], orient='index', columns=table_1_cols)
    # sort values by custom list or by delta
    for t in table_1.keys():
        if order_by and t in order_by.keys():
            table_1[t] = table_1[t].reindex(order_by[t].index.to_list())
        else:
            table_1[t].sort_values(by='$\Delta$', inplace=True) 
    return table_1

# Krippendorff's Alpha 
print('... unique texts (Krippendorff)', len(data['Question ID'].unique()))
table_1_alpha = analyse_IAA(data, 'krippendorf')

if not os.path.exists('results'):
    os.mkdir('results')
for key, table in table_1_alpha.items():
    with open(f'results/krippendorff_{key}.tex', 'w') as f:
        f.write(table.to_latex(#index=False,
                  formatters={"name": str.upper},
                  float_format="{:.3f}".format))


# Fleiss Kappa scores keeping only those with 6 annotations
d_filter = keep_by_annotation_count(df=data, by='Question ID', n_counts=6, method='filter') 
print('... unique texts (Fleiss)', len(d_filter['Question ID'].unique()))

# table_1_kappa = analyse_IAA(d_filter, 'fleiss', table_1_alpha)

################################################
# Types of hate speech annotation for understanding changes
################################################
# TODO: preprocesar los labels del Y-axis para quitar underscores y quizas en bold los targeting.

# ANALYSIS 1.2: Types of hate speech annotation for understanding changes
# data.to_csv('results/data.csv', index=False)
    
def analyse_types(df: pd.DataFrame, group: str, types_hs: List[str], samples: pd.DataFrame=samples):
    with open(f'results/annotation-type_examples_{group}', 'w') as output_file:
        sys.stdout = output_file
        for id in samples['Question ID']:
            print('\n\nQUESTION ID: ', id)
            for g in dc.TARGET_GROUPS:
                for p in dc.PHASES:
                    category = define_category(df.loc[df['Question ID']==id,], f"{g}_cat_{p}", g)
                    samples.loc[samples['Question ID']==id, f"{g}_types_{group}_{p}"] = category
    # reset sys.stdout to the original value after the specific subpart
    sys.stdout = sys.__stdout__

    for g in dc.TARGET_GROUPS:
        # Plot distribution
        u.export_frequency_plot(df=samples, 
                            col1=f"{g}_types_{group}_1", 
                            col2=f"{g}_types_{group}_2", 
                            order=types_hs, 
                            labels_type=g, 
                            pdf_filename=f'results/types_freq-plot_{g}_{group}.pdf')

        # Plot shifts
        u.export_sankey_diagram(df=samples, 
                            col1=f"{g}_types_{group}_1", 
                            col2=f"{g}_types_{group}_2", 
                            order=types_hs[::-1], 
                            labels_type=g, 
                            pdf_filename=f'results/types_shifts-sankey_{g}_{group}.pdf', 
                            case=group)
        u.export_matrix_viz(df=samples, 
                            col1=f"{g}_types_{group}_1", 
                            col2=f"{g}_types_{group}_2", 
                            order=types_hs[::-1], 
                            labels_type=g, 
                            pdf_filename=f'results/types_shifts-matrix_{g}_{group}.pdf')
        
# Categorisation based on level of disagreement and decision made
types_hs = [f'{a}_{d}' for a in ['all', 'majority', 'opinions'] for d in u.DECISIONS] + \
    ['no-agreement']

analyse_types(df=data, group='all', types_hs=types_hs)

# Categorisation by groups
for group in data[dc.CATEG['c1']].unique():
    print(group)
    subset = data.loc[data[dc.CATEG['c1']]==group].copy()
    print(group, ': ', subset.shape)

    analyse_types(df=subset, group=group, types_hs=types_hs)

samples.to_csv('results/samples.csv', index=False)
for g in dc.TARGET_GROUPS:
    # Categories overlap between c1 groups
    for p in dc.PHASES:
        u.export_overlap_count(samples, col1=f"{g}_types_LGBT_{p}", col2=f"{g}_types_nonLGBT_{p}", order=types_hs[::-1], labels_type=g, pdf_filename=f'results/types_overlap_{g}_Phase{p}.pdf')
    # Entitites learnt
    with open(f'results/types_learned_{g}', 'w') as output_file:
        sys.stdout = output_file
        process_rationale(samples, data, labels_type=g)
        sys.stdout = sys.__stdout__

    
################################################
# Disaggregated IAA scores and correlation with target groups
################################################

# ANALYSIS 2: Disaggregated IAA scores and correlation with target groups
def subgroup_analysis(df: pd.DataFrame, iaa_score: str, annotator_categories: List[int], labels: List[str], labels_type: str, order_by: pd.DataFrame = None, manual_expert: bool = True):
    """ Compute a list of resulting dataframes: with IAA and correlation (R and p-val) on each phase """
    if manual_expert:
        MANUAL_EXPERT = {'group': {'gender': 'LGBT', 'sexuality': 'LGBT'}, 'subgroupA': {'gender': 'G', 'sexuality': 'S'}}
    else:
        MANUAL_EXPERT = {}
    values = defaultdict(dict)
    for c in annotator_categories:
        print(df[c].value_counts())
        # agreement on each subgroup
        for sc in df[c].unique():
            # for every value in the category
            subset, alphas_1, alphas_2 = df.loc[df[c] == sc], [], []
            for sg in labels:
                alpha_1, alpha_2, _ = get_scores_and_delta(subset, iaa_score, sg)
                alphas_1.append(alpha_1)
                alphas_2.append(alpha_2)
            values['alpha_1'][sc], values['alpha_2'][sc] = alphas_1, alphas_2
        # alignment with highest target group in category c
        for p in dc.PHASES:
            for i, sg in enumerate(labels):
                # target group with highest agreement on sg label
                target = [MANUAL_EXPERT[c][labels_type] if c in MANUAL_EXPERT and labels_type in MANUAL_EXPERT[c] 
                          else define_expert(values=values[f'alpha_{p}'], position=i, categ_level=c)][0]
                target_subset = df.loc[df[c] == target]
                for src in df[c].unique():
                    src_subset = df.loc[df[c] == src] 
                    corr_coeff, pvalue = pearson_correlation(src_subset, target_subset, f'{sg}_{p}', 'Question ID') # how much they align with it
                    try:
                        values[f'r_{p}'][src].append(corr_coeff)
                        values[f'p_{p}'][src].append(pvalue)
                    except KeyError:
                        values[f'r_{p}'][src], values[f'p_{p}'][src] = [corr_coeff], [pvalue]

    # index names and sort by (6 tables: alpha, R, p_val for each phase)
    res_df =  [pd.DataFrame.from_dict(values[k]) for k in values.keys()]
    for i in range(0, len(res_df)):
        res_df[i].index = labels
        if isinstance(order_by, pd.DataFrame):
            res_df[i] = res_df[i].reindex(order_by.index.to_list())
    return res_df

# Krippendorff's Alpha and Pearson Correlation
table_2 = {}
hide_rows = {'gender':['gender_other', 'non-binary', 'gender_unclear'], 
             'sexuality': ['asexual', 'sexuality_unclear']}
for g in dc.TARGET_GROUPS:
    # of annotator demographics
    results = subgroup_analysis(data, 'krippendorf', dc.CATEG.values(), labels = dc.TARGET_LABELS[g], labels_type=g, order_by=table_1_alpha[g])
    table_2[f'{g}_alpha_1'], table_2[f'{g}_alpha_2'], table_2[f'{g}_r_1'], table_2[f'{g}_p_1'], table_2[f'{g}_r_2'], table_2[f'{g}_p_2'] = results

    # Table plots
    cols = ['nonLGBT', 'LGBT', 'M', 'W', 'S', 'G']
    for p in dc.PHASES:
        
        # hide rows
        n_rows = 7 - len(hide_rows[g])
        u.export_table_plot(cell_values_df=table_2[f'{g}_alpha_{p}'][cols], 
                          color_values_df=table_2[f'{g}_alpha_{p}'][cols], 
                          pdf_filename=f'results/krippendorff_increased_{g}_{p}_{'_'.join(cols)}.pdf', 
                          boldface_ranges=[0, 2, 6], 
                          hide_rows=hide_rows[g], 
                          figsize=(10, 7 - len(hide_rows[g])), 
                          colorbar_label='Krippendorff Alpha', phase = p)  

        # show correlation values instead of agreement scores
        u.export_table_plot(cell_values_df=table_2[f'{g}_r_{p}'][cols], 
                          color_values_df=table_2[f'{g}_r_{p}'][cols], 
                          pdf_filename=f'results/pearson_increased_{g}_{p}_{'_'.join(cols)}.pdf', 
                          boldface_ranges=[0, 2, 6], 
                          p_values_df=table_2[f'{g}_p_{p}'][cols], 
                          hide_rows=hide_rows[g], 
                          figsize=(10, 7 - len(hide_rows[g])), 
                          colorbar_label='Correlation Coefficient', phase = p)

        # # mixed
        # export_table_plot(cell_values_df=table_2[f'{g}_alpha_{p}'][cols], 
        #                   color_values_df=table_2[f'{g}_r_{p}'][cols], 
        #                   pdf_filename=f'results/krippendorff_with_pearsonPval_{g}_{p}_{'_'.join(cols)}.pdf', 
        #                   boldface_ranges=[0, 2, 6], 
        #                   p_values_df=table_2[f'{g}_p_{p}'][cols])    
    
    # hide columns
    # plot_1, plot_2 = ['nonLGBT', 'M', 'W',], ['LGBT', 'S', 'G'] 
    # export_table_plot(cell_values_df=table_2[f'{g}_alpha'][plot_1], color_values_df=table_2[f'{g}_delta'][plot_1], pdf_filename=f'results/krippendorff_{g}_{'_'.join(plot_1)}.pdf')
    # export_table_plot(cell_values_df=table_2[f'{g}_alpha'][plot_2], color_values_df=table_2[f'{g}_delta'][plot_2], pdf_filename=f'results/krippendorff_{g}_{'_'.join(plot_2)}.pdf')

# other annotations 
g, g_labels = 'other', [f"{l}_bin" for l in dc.TARGET_GROUPS + dc.HATE_QS]
print(g_labels)
results = subgroup_analysis(data, 'krippendorf', dc.CATEG.values(), labels = g_labels, labels_type=g, order_by=table_1_alpha[g])
table_2[f'{g}_alpha_1'], table_2[f'{g}_alpha_2'], table_2[f'{g}_r_1'], table_2[f'{g}_p_1'], table_2[f'{g}_r_2'], table_2[f'{g}_p_2'] = results
for p in dc.PHASES:
    u.export_table_plot(cell_values_df=table_2[f'{g}_alpha_{p}'][cols], 
                  color_values_df=table_2[f'{g}_alpha_{p}'][cols], 
                  pdf_filename=f'results/krippendorff_{g}_{p}_{'_'.join(cols)}.pdf', 
                  boldface_ranges=[0, 2, 6], figsize=(10, 4),
                  colorbar_label='Krippendorff Alpha', phase = p)
    
    u.export_table_plot(cell_values_df=table_2[f'{g}_r_{p}'][cols], 
                  color_values_df=table_2[f'{g}_r_{p}'][cols], 
                  pdf_filename=f'results/pearson_{g}_{p}_{'_'.join(cols)}.pdf', 
                  boldface_ranges=[0, 2, 6], figsize=(10, 4),
                  p_values_df=table_2[f'{g}_p_{p}'][cols], 
                  colorbar_label='Correlation Coefficient', phase = p)
