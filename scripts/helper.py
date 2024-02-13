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

# https://towardsdatascience.com/17-types-of-similarity-and-dissimilarity-measures-used-in-data-science-3eb914d2681
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
# Categorisation
#########################
TYPES_ANNOT = [f'all_{d}' for d in ['not-targeting', 'unclear', 'targeting']] + \
    [f'common_{d}' for d in ['not-targeting', 'unclear', 'targeting-single', 'targeting-multiple']] + \
    [f'divisive_{d}' for d in [f'two-{subd}' for subd in ['both-targeting', 'one-targeting', 'one-unclear']] + [f'three-{subd}' for subd in ['all-targeting', 'two-targeting', 'one-targeting']]] + \
    ['none']
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

def check_targeting(input_data: List[List[str]], drop_values: List[str]):
    for drop_value in drop_values:
        if drop_value in input_data:
            input_data.remove(drop_value)
    return input_data

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
    # Case 2: at least two opinions (divisive opinion)
    elif subgroup_counts[1] >= 2:
        category, second_group = 'divisive', subgroup_annot[1]
        group_opinions = [first_group[0], second_group[0]]
        if len(subgroup_counts) > 2 and subgroup_counts[2] >= 2:
            category += '_three'
            group_opinions.append(subgroup_annot[2][0])
            if_two = 'two'
        else:
            category += '_two'
            if_two = 'both'
        targeting = check_targeting(group_opinions, [[f'{labels_type}_not-referring'], [f'{labels_type}_unclear']])
        if len(targeting) == 3:
            category += '-all-targeting'
        elif len(targeting) == 2:
            category += f'-{if_two}-targeting'
        elif len(targeting) == 1:
            category += '-one-targeting'
        else: # No other options, but one were unclear: 
            category += '-one-unclear'
    # Case 3: one common opinion 
    #  Consider differentiation to one emergent group > this is >= 3, and next is same but == 2
    elif subgroup_counts[0] >= 2:
        category = 'common'
        if first_group[0] == [f'{labels_type}_not-referring']:
            category += '_not-targeting'
        elif first_group[0] == [f'{labels_type}_unclear']:
            category += '_unclear'
        elif len(first_group[0]) == 1:
            category += '_targeting-single'
        else:
            category += '_targeting-multiple'
    # Case 4: no agreement
    else:
        category='none'
    print(category)
    return category