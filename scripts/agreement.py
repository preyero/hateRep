import numpy as np 
import pandas as pd
from statsmodels.stats.inter_rater import fleiss_kappa, aggregate_raters
import krippendorff


#########################
# Inter-annotator agreement (IAA)/Interrater reliability
#########################

# 1. Cohen's Kappa: agreement between two raters
# https://www.surgehq.ai/blog/inter-rater-reliability-metrics-understanding-cohens-kappa
from sklearn.metrics import cohen_kappa_score
# y1: label assigned by first rater (i think is nominal, a variable with n_classes) 
# y2: label by rater 2
# only in the intersect between two raters!
#from statsmodels.stats.inter_rater import cohens_kappa
# For more than two raters, it can create a contigency of n_raters-dimensions (instead of 2-dimen)
# https://www.statsmodels.org/stable/generated/statsmodels.stats.inter_rater.to_table.html
# sample x annotations. BUT no NaN (have to delete them?? i think it does use the information of which labeler for p_e.
# look kappa with missing data (at random): listwise deletion https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6506991/ 
# Maybe one against the others? gives one value per annotator and calculate mean + std deviation.

# 2. Fleiss' Kappa: agreement between more than 3 raters (nominal: x in {A, B, C}) > 
# Kendall for ordinal (A<B<C), intra-class correlation for a metric.
# https://datatab.net/tutorial/fleiss-kappa
# from counts of category assigned: Fleiss Kappa can be specially used when participants are rated by different sets of raters. This means that the raters responsible for rating one subject are not assumed to be the same as those responsible for rating another (Fleiss et al., 2003).
def keep_by_annotation_count(df: pd.DataFrame, by: str, n_counts: int, method: str):
    # Get counts
    c = df.groupby(by)[by].transform('count')

    if method == 'filter':
        return df[ c == n_counts ]
    elif method == 'downsample':
        return


def fleiss(df: pd.DataFrame, subject_col: str, rating_col: str, verbose: bool = False):
    # Table of category assignments, e.g. (3 raters),
    # category_assignment = [[0, 0, 1], # Text/Subject 1
    #                 [1, 0, 0], # Text/Suject 2
    #                 [1, 0, 0]] # Text/Subject 3
    category_assignment = []
    subject_ids = df[subject_col].unique()
    for subject_id in subject_ids:
        ratings = df.loc[df[subject_col]==subject_id, rating_col].values.tolist()
        category_assignment.append(ratings)
    
    # Format for fleiss_kappa, e.g., 
    # table = [[1, 2], # Text/Subject 1
    #                 [2, 1], # Text/Suject 2
    #                 [2, 1]] # Text/Subject 3
    table, categories = aggregate_raters(data=category_assignment)
    if verbose:
        print(f'Computing Fleiss kappa on {rating_col} with categories: {categories}')

    # Compute fleiss kappa score
    return fleiss_kappa(table)

# 3. Krippendorf's Alpha: incomplete data (not every annotator each sample) and arbitrary number of raters (not always 2 or 3)
# https://www.surgehq.ai/blog/inter-rater-reliability-metrics-an-introduction-to-krippendorffs-alpha
# https://www.lighttag.io/blog/krippendorffs-alpha/
def krippendorf(df: pd.DataFrame, rater_col: str, subject_col: str, rating_col: str, verbose: bool = False):
    if verbose:
        print(f'computing Krippendorf on {rating_col}')

    # Select values as nominal or ordinal
    if '_bin' in rating_col:
        level = "ordinal"
    else:
        level = "nominal"
    # Transform to data format, e.g.,
    # rating_table = [[np.nan, np.nan, np.nan, np.nan, np.nan, 3, 4, 1, 2, 1, 1, 3, 3, np.nan, 3], # User/Rater 1
    #                 [1, np.nan, 2, 1, 3, 3, 4, 3, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan], # User/Rater 2
    #                 [np.nan, np.nan, 2, 1, 3, 4, 4, np.nan, 2, 1, 1, 3, 3, np.nan, 4]] # User/Rater 3
    df = df.pivot_table(index=rater_col, columns=subject_col, values=rating_col, aggfunc="first", fill_value=np.nan)
    rating_table = df.values.tolist()

    # Compute Krippendorf's Alpha
    return krippendorff.alpha(reliability_data=rating_table, level_of_measurement=level)


def get_scores_and_delta(data_subset: pd.DataFrame, score: str, rating_col: str, rater_col: str = 'User', subject_col: str = 'Question ID', verbose: bool = False):
    """ IAA in both phases and delta between them """

    # get alpha values
    if score == 'krippendorf':
        val_1 = krippendorf(df=data_subset, rater_col=rater_col, subject_col=subject_col, rating_col=f'{rating_col}_1', verbose=verbose)
        val_2 = krippendorf(df=data_subset, rater_col=rater_col, subject_col=subject_col, rating_col=f'{rating_col}_2', verbose=verbose)
    # get kappa values
    elif score == 'fleiss':
        val_1 = fleiss(df=data_subset, subject_col=subject_col, rating_col=f'{rating_col}_1', verbose=verbose)
        val_2 = fleiss(df=data_subset, subject_col=subject_col, rating_col=f'{rating_col}_2', verbose=verbose)
    return [round(val_1, 3), round(val_2, 3), round(val_2-val_1, 3)]