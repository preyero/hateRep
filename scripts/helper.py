from typing import List, Dict
import pandas as pd
from scipy import stats

#########################
# Alignment
#########################
EXPERT = {'group': ['LGBT'], 'subgroupA': ['S', 'G'], 'subgroupB': ['NB', 'T', 'H']}
MANUAL_EXPERT = {'group': {'gender': 'LGBT', 'sexuality': 'LGBT'}, 'subgroupA': {'gender': 'G', 'sexuality': 'S'}}

def define_expert(values: Dict[str, List[float]], position: int, categ_level: str, manual_expert=True, labels_type:str=None) -> str:
    """ Given a dict of float values of a string subcategory (in categ_level), returns the one with highest value of label at position """
    if manual_expert and categ_level in MANUAL_EXPERT.keys() and labels_type in MANUAL_EXPERT[categ_level].keys():
        return MANUAL_EXPERT[categ_level][labels_type]
    else:
        candidates = EXPERT[categ_level]
        if len(candidates) > 1:
            candidates_values = [values[sc][position] for sc in candidates]
            expert_i = max(range(len(candidates_values)), key=candidates_values.__getitem__)
        else:
            expert_i = 0
        return candidates[expert_i]


def pearson_correlation(src_df: pd.DataFrame, target_df: pd.DataFrame, label: str, id_col: str):
    """ Compute correlation coefficients between a source (src_df) and target (target_df) label column, aggregating values (by id_col) """

    # other studies using correlation and kappa to uncover non-random examiner error: https://pubmed.ncbi.nlm.nih.gov/3455967/

    # Majority vote:
    src_agg = src_df[[id_col, label]].groupby(id_col).agg('mean')
    target_agg = target_df[[id_col, label]].groupby(id_col).agg('mean')

    to_compare = pd.merge(target_agg, src_agg, on=[id_col], how='inner', suffixes=['_target', '_src'])

    # pearson coeffs 
    pearson = stats.pearsonr(to_compare[f'{label}_src'], to_compare[f'{label}_target'])

    return round(pearson.statistic, 2)

#########################
# Categorisation
#########################
def group_by_value(input_data: List[List[str]]):
    """ Create annotation vectors: dictionaries of count and sublists of unique values """
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


def is_majority(same: int, total: int):
    """ Returns True if integer value of counts (same) is a majority given a total integer number (total) """
    if same > total/2:
        return True
    else:
        return False


def define_category(subset_annot: pd.DataFrame, col: str, labels_type: str) -> str:
    """ Rule-based categorisation by agreement and decision on target groups """
    annotations = subset_annot[col].to_list()
    print(len(annotations), annotations)
    subgroup_annots, subgroup_counts = group_by_value(annotations)
    first_group = subgroup_annots[0]
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
    elif len(annotations) > 2 and is_majority(subgroup_counts[0], len(annotations)):
        category = 'majority'
        if first_group[0] == [f'{labels_type}_not-referring']:
            category += '_not-targeting'
        elif first_group[0] == [f'{labels_type}_unclear']:
            category += '_unclear'
        else:
            category += '_targeting'
    # Case 3: there are different opinions
    elif subgroup_counts[0] >= 2:
        subcat, i = '_not-targeting', 0
        while i < len(subgroup_annots) and subgroup_counts[i] >= 2:
            subgroup_annot = subgroup_annots[i]
            if subgroup_annot[0][0] not in [f'{labels_type}_not-referring', f'{labels_type}_unclear']:
                subcat = '_targeting'
                break
            if subgroup_annot[0] == [f'{labels_type}_unclear']:
                subcat = '_unclear'
            i += 1
        category = 'opinions' + subcat
    # Case 4: no agreement
    else:
        category='no-agreement'
    print(category)
    return category


def process_rationale(d: pd.DataFrame, annot: pd.DataFrame, labels_type: str):
    """ Print counts and unique entities learnt with semantics in participant groups """
    N, agreed = d.shape[0],  ['all', 'majority', 'opinions']
    yes = [f'{a}_targeting' for a in agreed]
    no = [f'{a}_not-targeting' for a in agreed] # + [f'{a}_unclear' for a in agreed] + ['no-agreement']
    replace = {k:'no' for k in no} | {k:'yes' for k in yes}
    replace_c = [f'{labels_type}_types_{sg}_{p}' for sg in ['LGBT', 'nonLGBT'] for p in ['1', '2']]
    d[replace_c] = d[replace_c].replace(to_replace=replace)
    for sg in ['LGBT', 'nonLGBT']:
        print(f'\n\n\n PROCESSING {labels_type} for {sg}')
        # Get IDs of new posts targeting 
        ids = d.loc[(d[f'{labels_type}_types_{sg}_1']=='no') & (d[f'{labels_type}_types_{sg}_2']=='yes'), 'Question ID'].to_list()
        # Filter rationales in texts(new in justify_change_{labels_type}), full in justify)
        subset = annot.loc[annot['Question ID'].isin(ids)]
        print(f'{sg}: {round(len(ids)/N*100, 2)}% ({len(ids)})')
        for id in ids:
            print('\n\nQUESTION ID: ', id)
            subset_id = subset.loc[subset['Question ID']==id]
            print(subset_id['Question'].to_list()[0])
            print(f'\n {sg}:')
            print(subset_id.loc[subset_id['group']==sg, [f'{labels_type}_cat_2', f'justify_change_{labels_type}', f'Justify {labels_type.capitalize()}_2']])

            other_sg = ['LGBT' if sg == 'nonLGBT' else 'nonLGBT'][0]
            print(f'\n by {other_sg}')
            print(subset_id.loc[subset_id['group']==other_sg, [f'{labels_type}_cat_2', f'justify_change_{labels_type}', f'Justify {labels_type.capitalize()}_2']])            