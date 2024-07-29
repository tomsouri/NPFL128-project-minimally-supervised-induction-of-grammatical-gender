# NPFL128-project-minimally-supervised-induction-of-grammatical-gender

This project aims to partially replicate the work of Cucerzan & Yarowsky 2003 (Minimally supervised induction of grammatical gender https://aclanthology.org/N03-1006). They describe a process how to use unannotated corpus and small number of seeds to learn a reliable predictor of gender.

We perform our experiments on Czech. As training, development and testing data we use the Czech-PDT UD treebank by Daniel Zeman and Jan Hajič. Training data are used as an unannotated corpus, while development and testing data are used for evaluation of the performance.

We start by automatically translating the proposed English seeds to Czech and automatically removing collisions (natural seeds). For translating the seeds, we used Charles Translator by Popel, M., Tomkova, M., Tomek, J. et al. Transforming machine translation: a deep learning system reaches news translation quality comparable to human professionals. Nat Commun 11, 4381 (2020). https://doi.org/10.1038/s41467-020-18073-9 .

Then we try to extend the number of nouns with known gender by context bootstrapping, as proposed. We employ all six proposed context models (left/right/bilateral x whole word/suffix). However, in the paper they do not mention the length of suffix used. We therefore try lengths 1, 2, 3 and choose arbitrarily (it does not seem to make much difference).

However, we face several difficulties, mostly caused by vague description of the process in the paper. They say:
"The bootstrapping process starts by collecting statistics over the contexts in the corpus with which the seeds co-occur. These are filtered using a frequency threshold sensitive to both the size of the corpus and the seed list. Additional filtering is done by discarding contexts with high relative co-occurrence with words outside the noun list, based on the estimated coverage of this available noun list."
"Once reliable contexts in terms of grammatical gender are determined, the distributions for all the words in the noun list are modified according to the number of reliable contexts with which they co-occur. Based on association statistics with these derived contexts, additional non-seed nouns with gender assignments above a threshold are added to the seed list and the bootstrapping algorithm iterates until no more such nouns or contexts are found."

They mention several times some tresholds, but is not clear, what exact threshold value should be used, and we were not able to adjust the treshold such that the bootstrapping process would work. We tried to setup the way how to filter the contexts/nouns to get only relevant ones, but we did not succeed: with some methods, we obtained 98% precision, but recall 0.04%. With other methods, we obtained recall 100%, but precision less than 40% (which is really bad, considering that by predicting always masculine gender you can get 44%).
The process either stops too early (when the relevance condition is too strict) or ends up with almost all nouns being marked as feminine (and, in some cases, almost all nouns marked as masculine), when the condition is not strict at all.


What we tried - Consider the noun/context to be feminine, if its counts are: 
    1. fem > masc + quest/2, and vice versa. (too strict: precision=0.3522012, recall=0.0041395)
    2. fem > 0 (or > 1 or >2 etc.) and masc = 0 (or fem > n and masc = 0) (too strict, precision=0.384917, recall=0.69700)
    3. fem > masc (too permissive, allows a lot of errors: precision=0.380766, recall=0.69981, res5)
    4. the same as 1., but if no new nouns are discovered, iteratively decrease the weight 1/2 until you obtain some match. (too permissive)
    
    
    
FUTURE WORK:
- make the bootstrapping work by setting up a better condition
- add the morphological analysis additional tool to increase the recall
- compare the obtained results with the results from paper
