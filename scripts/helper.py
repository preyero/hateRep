from typing import List, Dict
import pandas as pd
from scipy import stats

#########################
# Intra-annotator consistency (IAC)
#########################

# 1. Test-retest: correlation at two distinct occassions, agreement in repeated measures
# https://www.sciencedirect.com/topics/nursing-and-health-professions/test-retest-reliability


# 2. Intraclass Correaltion Coefficients (ICC): consistency in repeated measures


#########################
# Alignment
#########################
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