# Insight Data Engineering - Coding Challenge 2008

This project aims at solving the 2018 Insight Data Engineering - [Coding Challenge](https://github.com/InsightDataScience/donation-analytics). We remand to the README file of the previous link for a detailed discussion of the challenge; here we summarize only the most relevant details. We need to analyze the electoral campaign contributions published by the Federal Election Commission regularly publishes. The goal is to identify recurrent donors, crunch a few values and write the results into an output file, "repeat_donors.txt"

The name of the main code to solve the challenge is _donation-analytics.py_, written in Python. Syntax: _python ./src/donation-analytics.py ./input/itcont.txt ./input/percentile.txt ./output/repeat_donors.txt_

The code requires the libraries _numpy_ and _pandas_. Here we report the version of the libraries used:
* Python 2.7.14
* numpy 1.12.1
* pandas 0.20.3
 
 The code is located into a _src_ directory according to the guideline in the [README](https://github.com/InsightDataScience/donation-analytics) file of the challenge.  The code is taking into input a percentile value from the file _percentile.txt_ and store it into the variable _q_ which will define the running percentile value of the contributions received from repeat donors to a recipient. The code then reads the file _itcont.txt_ splitting it into "pieces" of _chunksize_ rows and via a iterator, to avoid memory issues. Only the columns _CMTE_ID,NAME,ZIP_CODE,TRANSACTION_DT,TRANSACTION_AMT,OTHER_ID_ are read.
 
 Relevant functions for read operations are:
 * _f_zip_code_ which parse the zip code by taking only the first 5 digits of the provided field and perform a quality check of it, that is whether the field is made up of digits only. A _NAN_ value is thrown if the field is malformed.
 * _dateparse_: it is a _lambda_ function which parses the data field in the form _mmddyyyy_, and throw a _NAN_ if a malformed field is present. The date is converted into a _datetime_ object.
 
 We then fetch a sub-dataframe obtained from iterating over sequence; dropping _NAN_ values; keeping rows with empty OTHER_ID since we are interested in donations from individuals; and finally storing the relevant fields in a list.
 
 Once we finish with the iterator we concatenate all the sub-dataframes. 
 
 First, we create a unique IDs based on NAME and ZIP_CODE for the purpose to identify uniquely a person. We then removed single-entry lines which cannot clearly contains repeat donors.
 
 Next, we find repeating donors by grouping by ID and applying the function _repeat_donor_, which returns a Boolean value identifying whether a donor had previously contributed to any recipient listed in the _itcont.txt_ 
 
 We then select only rows corresponding to repeat donors and throw away the remaining ones.
 
 For each recipient, zip code and year we calculate:
 * the running percentile of contributions received from repeat donors to a recipient streamed in so far for this zip code and calendar year. We used the _expanding_ function of _pandas_ to perform the calculation in a window out to the current line; and the _numpy_ routine _percentile_ to infer the actual percentile of parameter _q_ in the previous windows. We used the nearest-rank method for this purpose, and we call the retrieved field _percentile_contribution_
 * total amount of contributions received by recipient from the contributor's zip code streamed in so far in this calendar year from repeat donors. We called the retrieved field of transactions received by recipient from _total_number_contributions_
* cumulative sum of the contributor's zip code streamed in so far this calendar year from repeat donors. We call the inferred field _total_dollar_amount_

Finally, we select the columns _CMTE_ID, ZIP_CODE, year, percentile_contribution,total_dollar_amount, total_number_contributions_, and write them on the output on the pipe delimited file _repeat_donors.txt_.

 
 

