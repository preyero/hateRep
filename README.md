[![Python](https://upload.wikimedia.org/wikipedia/commons/5/50/Blue_Python_3.12%2B_Shield_Badge.svg)](https://www.python.org/downloads/release/python-3120/)

# hateRep: A Hate Speech Dataset with Repetitions

This repository contains posts with [semantic]('data/database.csv') and crowdsourced (i.e., in `data/annotations_*.csv`) annotation, which have been extracted from 4 hate speech databases ([Measuring Hate Speech](https://huggingface.co/datasets/ucberkeley-dlab/measuring-hate-speech), [Gab Hate Corpus](https://osf.io/edua3/), [HateXplain](), and [XtremeSpeech](https://github.com/antmarakis/xtremespeech)).

The methodology and findings from this study are presented in: **Semantics of Target Groups Matters: A Knowledge-enhanced Hate Speech Annotation**

## Abstract

Detecting online hate requires dealing with different perceptions of what constitutes hate speech. Previous work has found that not belonging to groups frequently targeted may lead to perceiving less hate speech. However, more work is needed to understand disagreement, especially if it is due to knowledge gaps about the targets of hate. Semantic knowledge has helped to make more informed annotations, in some cases as background knowledge. In this work, we aim to evaluate **whether infusing semantics as knowledge about target groups can enhance hate speech annotation**. Specifically, by highlighting and defining concepts related to groups targeted due to their social identity (e.g., gender and race). Our knowledge-enhanced annotation involves a two-stage study to isolate infusing semantics, and includes a diverse participant sample. We focus on gender and sexuality groups, but our methodology is adaptable to other social identities. Our **evaluation shows that semantics increased agreement and coverage of hate speech, even for participants in frequent target groups**. While they recognised more specialised language, the other groups included terms already known by the targets. Background knowledge increased inter-annotator agreement by up to 19\%, bringing annotation closer to the target groups. 

## Repo structure

Data is organised in three folders: 

* *Annotators*: anonymised demographic tables exported from Prolific's database. Participants appear under only one of the following categories, subject to: being a (i) heterosexual cis men (M_MH), (ii) a heterosexual cis women (W_WH), or belonging to (iii) gender (trans, G_T, or non-binary, G_NB) or (iv) sexuality (non-heterosexual, S_H) groups frequently targeted. 


* *Data*: contains semantic and crowdsourced annotations. The specific categories are shown in [figure](#hate-speech-annotations) below. Semantic annotations were provided with Jupyter [Notebooks](semantic_annotation) (*semantic_annotation*).

* *Documentation*: contains the approved ethics application form and participant information sheet.

Source code is in *scripts*, specifically in the Python files:

* *dataCollect.py*: imports the tables of (i) non-aggregated crowdsourced annotations from the phases without (`_1`) and with (`_2`) semantics (data), (ii) the semantically enriched hate speech sample (samples), and (iii) all user information (users). 

* *agreement.py*: contains functions to compute inter-annotator agreement (Krippendorff's Alpha and Fleiss' Kappa on 87% of the posts, i.e., with 6 annotations).

* *helper.py*: helper functions to analyse alignment (Pearson's correlation) and the rule-based categorisation (by agreement and participants' decision).

* *utils.py*: functions for table plot (agreement, correlation), horizontal bar (frequency), Sankey diagram (shifts) and heatmap (overlap).

## Hate Speech Annotation Example

<p align="center">
 <img src="data/survey_items.png" alt="drawing" width="700" class="center"/>
</p>

## Run files

The code runs in a conda environment using Python version 3.12

```commandline
    hateRep <user-login>$ python main.py
```

