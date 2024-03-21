# HateRep: A Hate Speech Dataset with Repetitions

**Resolving Unintended Disagreement due to Lack of Context**



## Repo structure

The data files are organised within two folders: 

* *Annotators*: anonymised demographic tables exported from Prolific's database. Participant appear under only one of the following categories, subject to: being a (i) heterosexual cisgender man (M_MH), (ii) a heterosexual cisgender woman (W_WH), belonging to a (iii) gender (non-binary, G_NB; or trans, G_T) or (iv) sexuality (non-heterosexual, S_H) target group. 


[comment]: # (Note: target group categories are non-exclusive, i.e., participants in (iii) -- (iv) may have also in (iii) to (iv).)

* *Data*: hate speech annotations and responses to additional background questions from the annotators. Hate speech annotations are shown in the [Figure](#hate-speech-annotations).


All code to evaluate the two-stage study in *scripts*. Specifically, in the Python files:

* *dataCollect.py*: generates a table of non-aggregated user annotations without (_1) and with (_2) context (data), hate speech sample with context (samples), and all user information (users). A full description of each table column can be found in the datasheet.

* *agreement.py*: functions to compute inter-annotator agreement (Krippendorff's Alpha, Fleiss' Kappa).

* *helper.py*: helper functions to analyse impact on categorisation (by agreement and participants' decision rules) and alignment (Pearson's correlation).

* *utils.py*: plotting functions for table (agreement, correlation), horizontal bar (frequency), diagram (Sankey shifts) and heatmap (matrix shifts and overlap) plots.

## Hate speech annotations

<p align="center">
 <img src="data/survey_items.png" alt="drawing" width="600" class="center"/>
</p>

## Run files

This code run in a conda environment using Python version 3.12

```commandline
    scripts <user-login>$ python main.py
```
