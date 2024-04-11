[![Python](https://upload.wikimedia.org/wikipedia/commons/5/50/Blue_Python_3.12%2B_Shield_Badge.svg)](https://www.python.org/downloads/release/python-3120/)

# hateRep: A Hate Speech Dataset with Repetitions

This repository contains [semantic]('data/database.csv') and crowdsourced (data/annotations*.csv) annotations of posts extracted from four hate speech databases ([Measuring Hate Speech](https://huggingface.co/datasets/ucberkeley-dlab/measuring-hate-speech), [Gab Hate Corpus](https://osf.io/edua3/), [HateXplain](), and [XtremeSpeech](https://github.com/antmarakis/xtremespeech)).

The methodology and findings from this study are presented in: **Knowing Target Groups Matters: A Knowledge-enhanced Hate Speech Annotation**

## Abstract

Hate speech detection requires dealing with different perceptions of what constitutes hate speech. Previous work has found that not belonging to frequent target groups leads to perceiving less hate speech. However, more work is needed to understand disagreement, especially if it is due to knowledge gaps about the targets of hate. Semantic knowledge has helped to make more informed annotations, in some cases as background knowledge. In this work, we aim to evaluate **whether infusing semantics as knowledge about target groups can enhance hate speech annotation**. Specifically, by highlighting and defining concepts related to groups of social identities targeted by hate speech (e.g., gender and race). Our knowledge-enhanced annotation consists of a two-stage study that isolates the effect of semantics, and includes a diverse sample of participants from a crowdsourcing platform. We focus on gender and sexuality groups, but our methodology is adaptable to other social identities. Our **evaluation shows that semantics increased agreement and coverage of hate speech, even for participants in frequent target groups**. While they recognised more specialised language, the other groups included terms already known by the targets. Background knowledge increased inter-annotator agreement by up to 19\%, bringing annotations closer to those from target groups. 

## Repo structure

The data files are organised within two folders: 

* *Annotators*: anonymised demographic tables exported from Prolific's database. Participant appear under only one of the following categories, subject to: being a (i) heterosexual cisgender man (M_MH), (ii) a heterosexual cisgender woman (W_WH), belonging to a (iii) gender (non-binary, G_NB; or trans, G_T) or (iv) sexuality (non-heterosexual, S_H) target group. 


* *Data*: semantic and crowdsourced annotations. The specific annotated categories are shown in [figure](#hate-speech-annotations) below. Source code for semantic annotation is provided in Jupyter [Notebooks](semantic_annotation).


All code to evaluate the two-stage study is in *scripts*. Specifically, in the Python files:

* *dataCollect.py*: generates a table of non-aggregated user annotations without (_1) and with (_2) semantics (data), semantically enriched hate speech sample (samples), and all user information (users). 

* *agreement.py*: functions to compute inter-annotator agreement (Krippendorff's Alpha, Fleiss' Kappa on 87% of the posts, i.e., with 6 annotations).

* *helper.py*: helper functions to analyse alignment (Pearson's correlation) and semantics impact with a rule-based categorisation (by agreement and participants' decision).

* *utils.py*: plotting functions for table (agreement, correlation), horizontal bar (frequency), Sankey diagram (shifts) and heatmap (overlap).

## Hate Speech Annotation Example

<p align="center">
 <img src="data/survey_items.png" alt="drawing" width="700" class="center"/>
</p>

## Run files

The code runs in a conda environment using Python version 3.12

```commandline
    hateRep <user-login>$ python main.py
```

