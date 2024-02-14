from typing import List, Dict
import pandas as pd
from scipy import stats

#########################
# Alignment
#########################
# 1. Test-retest: correlation at two distinct occassions, agreement in repeated measures
# https://www.sciencedirect.com/topics/nursing-and-health-professions/test-retest-reliability
# 2. Intraclass Correaltion Coefficients (ICC): consistency in repeated measures

EXPERT = {'group': ['LGBT'], 'subgroupA': ['S', 'G'], 'subgroupB': ['NB', 'T', 'H']}
def define_expert(values: Dict[str, List[float]], position: int, categ_level: str) -> str:
    """ Given a dict of alpha values for each subcategory in categ_level, return the one with highest value of label at position """
    candidates = EXPERT[categ_level]
    if len(candidates) > 1:
        candidates_values = [values[sc][position] for sc in candidates]
        expert_i = max(range(len(candidates_values)), key=candidates_values.__getitem__)
    else:
        expert_i = 0
    return candidates[expert_i]


def pearson_correlation(src_df: pd.DataFrame, target_df: pd.DataFrame, label: str, id_col: str):

    # other studies using correlation and kappa to uncover non-random examiner error: https://pubmed.ncbi.nlm.nih.gov/3455967/

    # Majority vote:
    src_agg = src_df[[id_col, label]].groupby(id_col).agg('mean')
    target_agg = target_df[[id_col, label]].groupby(id_col).agg('mean')

    to_compare = pd.merge(target_agg, src_agg, on=[id_col], how='inner', suffixes=['_target', '_src'])

    # if to_compare.shape[0]!= 240:
    #     print(f' less samples seen in {label}: {to_compare.shape[0]}')

    # pearson coeffs and p values
    pearson = stats.pearsonr(to_compare[f'{label}_src'], to_compare[f'{label}_target'])
    corr_coeff, pval = pearson.statistic, pearson.pvalue
    # Bonferroni correction: https://www.ibm.com/support/pages/calculation-bonferroni-adjusted-p-values
    pval_corrected = pval * to_compare.shape[0]
    return round(corr_coeff, 2), pval_corrected

#########################
# Categorisation: CASE 6 ANNOTATORS
#########################
TYPES_ANNOT = [f'{a}_{d}' for a in ['all', 'majority'] for d in ['not-targeting', 'unclear', 'targeting']] + \
    [f'opinions_{a}' for a in ['one', 'two', 'three']] + \
    ['none']
TYPES_ANNOT_COLOR = ['green'] * 3 + ['greenyellow'] * 3 + ['orange'] * 3 + ['red'] 


def group_by_value(input_data: List[List[str]]):
    # Create a dictionary to store sublists grouped by their unique values
    group_dict = {}
    for sublist in input_data:
        key = tuple(sorted(set(sublist)))
        group_dict.setdefault(key, []).append(sublist)

    # Sort the dictionary items by the size of the sublists in decreasing order
    sorted_groups = sorted(group_dict.items(), key=lambda x: len(x[1]), reverse=True)

    # Extract the sublists from the sorted groups
    group = [sublists for _, sublists in sorted_groups]
    # Extract the group counts
    counts = [len(sublists) for _, sublists in sorted_groups]
    print(f'{counts} counts of groups: {group}')
    return group, counts


def define_category(subset_annot: pd.DataFrame, col: str, labels_type: str) -> str:
    annotations = subset_annot[col].to_list()
    print(len(annotations), annotations)
    subgroup_annot, subgroup_counts = group_by_value(annotations)
    first_group = subgroup_annot[0]
    # Case 1: all are the same
    if subgroup_counts[0] == len(annotations):
        category = 'all'
        if first_group[0] == [f'{labels_type}_not-referring']:
            category += '_not-targeting'
        elif first_group[0] == [f'{labels_type}_unclear']:
            category += '_unclear'
        else:
            category += '_targeting'
    # Case 2: there is a majority vote
    elif subgroup_counts[0] >= 4:
        category = 'majority'
        if first_group[0] == [f'{labels_type}_not-referring']:
            category += '_not-targeting'
        elif first_group[0] == [f'{labels_type}_unclear']:
            category += '_unclear'
        else:
            category += '_targeting'
    # Case 3: there are different opinions
    elif subgroup_counts[0] >= 2:
        category = 'opinions'
        if len(subgroup_counts) > 2 and subgroup_counts[2] >= 2:
            category += '_three'
        elif subgroup_counts[1] >= 2:
            category += '_two'
        else:
            category += '_one'
    # Case 4: no agreement
    else:
        category='none'
    print(category)
    return category