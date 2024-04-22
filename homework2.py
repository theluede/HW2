# PPHA 30537
# Spring 2024
# Homework 2

# Kathryn Luedke
# thelued

# Due date: Sunday April 21st before midnight
# Write your answers in the space between the questions, and commit/push only
# this file to your repo. Note that there can be a difference between giving a
# "minimally" right answer, and a really good answer, so it can pay to put
# thought into your work.  Using functions for organization will be rewarded.

##################

# To answer these questions, you will use the csv document included in
# your repo.  In nst-est2022-alldata.csv: SUMLEV is the level of aggregation,
# where 10 is the whole US, and other values represent smaller geographies. 
# REGION is the fips code for the US region. STATE is the fips code for the 
# US state.  The other values are as per the data dictionary at:
# https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2020-2022/NST-EST2022-ALLDATA.pdf
# Note that each question will build on the modified dataframe from the
# question before.  Make sure the SettingWithCopyWarning is not raised.

# PART 1: Macro Data Exploration

# Question 1.1: Load the population estimates file into a dataframe. Specify
# an absolute path using the Python os library to join filenames, so that
# anyone who clones your homework repo only needs to update one for all
# loading to work.
import pandas as pd
import os
base_path = r'C:\Users\klued\OneDrive - The University of Chicago\Quarter 3'
path = os.path.join(base_path, "NST-EST2022-ALLDATA (2).csv")
raw_census = pd.read_csv(path)
raw_census.head
pd.set_option('display.max_columns', None)
# Question 1.2: Your data only includes fips codes for states (STATE).  Use 
# the us library to crosswalk fips codes to state abbreviations.  Drop the
# fips codes.
# pip Install us
import us

FIP_abbr = us.states.mapping("fips", "abbr")
FIP_abbr
FIP_abbr = {int(k):v for k,v in FIP_abbr.items()}

raw_census["state_abbr"] = raw_census["STATE"].map(FIP_abbr)
raw_census.drop(columns=["STATE"])

print(raw_census.head())

raw_census["state_abbr"].unique()

## I used https://stackoverflow.com/questions/53480403/how-to-merge-pandas-
## dataframe-with-dict-of-lists and https://stackoverflow.com/questions/36397273
## /convert-key-from-dictionary-to-int-in-python

# Question 1.3: Then show code doing some basic exploration of the
# dataframe; imagine you are an intern and are handed a dataset that your
# boss isn't familiar with, and asks you to summarize for them.  Do not 
# create plots or use groupby; we will do that in future homeworks.  
# Show the relevant exploration output with print() statements.

print(raw_census.describe())
print(raw_census.info())
print(raw_census.isna().sum())

## I used https://www.analyticsvidhya.com/blog/2021/06/top-15-pandas-data-exploration-functions/
## for inspiration and https://saturncloud.io/blog/how-to-count-nan-values-in-
## a-pandas-dataframe-column/#:~:text=To%20count%20the%20number%20of,is%20NaN%
## 20and%20False%20otherwise. to count NaNs

# Question 1.4: Subset the data so that only observations for individual
# US states remain, and only state abbreviations and data for the population
# estimates in 2020-2022 remain.  The dataframe should now have 4 columns.

cut_census = raw_census[["state_abbr", "POPESTIMATE2020", "POPESTIMATE2021", "POPESTIMATE2022"]]
cut_census = cut_census.dropna()

## dropna method: https://pandas.pydata.org/docs/reference/api/pandas.DataFram
## e.dropna.html
# Question 1.5: Show only the 10 largest states by 2021 population estimates,
# in decending order.

cut_census.sort_values("POPESTIMATE2021", ascending=False).head(10)

## I used this website: https://python.plainenglish.io/how-to-print-the-first-10-
## rows-of-a-pandas-dataframe-8018e1b9c04b for inspiration

# Question 1.6: Create a new column, POPCHANGE, that is equal to the change in
# population from 2020 to 2022.  How many states gained and how many lost
# population between these estimates?

cut_census["POPCHANGE"] = cut_census.apply(lambda x: (x["POPESTIMATE2020"] - x["POPESTIMATE2021"]), axis=1)

len(cut_census["POPCHANGE"]) ## this is to audit the counts provided below

cut_census[(cut_census["POPCHANGE"] > 0)].count()
cut_census[cut_census["POPCHANGE"] < 0].count()
## I promtped chat GPT with the error "TypeError: <lambda>() missing 1 required
## positional argument: 'b'" to figure out this code.  I referenced https://www.
## geeksforgeeks.org/applying-lambda-functions-to-pandas-dataframe/# to help 
## structure the lambda function and https://saturncloud.io/blog/5-easy-ways-
## to-get-pandas-dataframe-row-count/#:~:text=The%20count()%20function%20of,
## pandas%20as%20pd%20df%20%3D%20pd. to use the count method

# Question 1.7: Show all the states that had an estimated change in either
# direction of smaller than 1000 people. 
## -1000 < popchange < 1000
print(cut_census[(cut_census["POPCHANGE"] > -1000) & (cut_census["POPCHANGE"] < 1000)])

# Question 1.8: Show the states that had a population growth or loss of 
# greater than one standard deviation.  Do not create a new column in your
# dataframe.  Sort the result by decending order of the magnitude of 
# POPCHANGE.
stdev = cut_census["POPCHANGE"].std()
cut_census.sort_values("POPCHANGE", key=lambda x: x["POPCHANGE"]/stdev)

## used this, couldn't get it to work: https://www.freecodecamp.org/news/lambda
## -sort-list-in-python/#:~:text=You%20can%20%E2%80%9Clambda%20sort%E2%80%9D%2
## 0a,and%20the%20sorted()%20function. Run out of time.
#PART 2: Data manipulation

# Question 2.1: Reshape the data from wide to long, using the wide_to_long function,
# making sure you reset the index to the default values if any of your data is located 
# in the index.  What happened to the POPCHANGE column, and why should it be dropped?
# Explain in a brief (1-2 line) comment.
cut_census_long = pd.wide_to_long(cut_census, stubnames="POPESTIMATE", i = "state_abbr", j = "year")
cut_census_long = cut_census_long.reset_index()
print(cut_census_long)
print(cut_census_long.isna().sum())

## https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html
## Pop change just reiterated over the values and repeated them twice over.

# Question 2.2: Repeat the reshaping using the melt method.  Clean up the result so
# that it is the same as the result from 2.1 (without the POPCHANGE column).
rename = {"POPESTIMATE2020":"2020", "POPESTIMATE2021":"2021", "POPESTIMATE2022":"2022"}
cut_census.columns
cut_census_renamed = cut_census.drop(["POPCHANGE"], axis=1)
cut_census_renamed = cut_census_renamed.rename(rename, axis=1)

cut_census_renamed.melt(id_vars="state_abbr", value_vars=None, var_name="year", value_name="POPESTIMATE")

## I used https://www.freecodecamp.org/news/dataframe-drop-column-in-pandas-
## how-to-remove-columns-from-dataframes/#:~:text=Method%20in%20Pandas-,The%20.
## ,the%20inplace%20parameter%20to%20True%20. to understand the .drop method

# Question 2.3: Open the state-visits.xlsx file in Excel, and fill in the VISITED
# column with a dummy variable for whether you've visited a state or not.  If you
# haven't been to many states, then filling in a random selection of them
# is fine too.  Save your changes.  Then load the xlsx file as a dataframe in
# Python, and merge the VISITED column into your original wide-form population 
# dataframe, only keeping values that appear in both dataframes.  Are any 
# observations dropped from this?  Show code where you investigate your merge, 
# and display any observations that weren't in both dataframes.
path2 = os.path.join(base_path, "state-visits.csv")
state_visit = pd.read_csv(path2)
state_visit.head

state_visit_census = cut_census.merge(state_visit, left_on=["state_abbr"], right_on=["STATE"], how="right")
print(state_visit_census)
# Question 2.4: The file policy_uncertainty.xlsx contains monthly measures of 
# economic policy uncertainty for each state, beginning in different years for
# each state but ending in 2022 for all states.  The EPU_National column esimates
# uncertainty from national sources, EPU_State from state, and EPU_Composite 
# from both (EPU-N, EPU-S, EPU-C).  Load it as a dataframe, then calculate 
# the mean EPU-C value for each state/year, leaving only columns for state, 
# year, and EPU_Composite, with each row being a unique state-year combination.
path3 = os.path.join(base_path, "policy_uncertainty.csv")
policy_uncertainty = pd.read_csv(path3)
policy_uncertainty.head

cut_policy_uncertainty = policy_uncertainty.drop(["month", "EPU_National", "EPU_State"], axis=1)

cut_policy_uncertainty = cut_policy_uncertainty.groupby(["state", "year"], as_index=False).mean(numeric_only=True)
cut_policy_uncertainty
## This website helped me with the mean function: https://github.com/pandas-dev
## /pandas/issues/57031 and https://www.freecodecamp.org/news/dataframe-drop-
## column-in-pandas-how-to-remove-columns-from-dataframes/#:~:text=Method%20in%20Pandas-,The%20.,the%20inplace%20parameter%20to%20True%20.

# Question 2.5) Reshape the EPU data into wide format so that each row is unique 
# by state, and the columns represent the EPU-C values for the years 2022, 
# 2021, and 2020. 
cut_policy_uncertainty_20_22=cut_policy_uncertainty.loc[cut_policy_uncertainty["year"] > 2019]

new_df = cut_policy_uncertainty_20_22.pivot(index="state", columns="year", values="EPU_Composite")
print(new_df)

# Question 2.6) Finally, merge this data into your merged data from question 2.3, 
# making sure the merge does what you expect.
state_name = us.states.mapping("abbr", "name")
state_name

state_visit_census["STATE"] = cut_census["state_abbr"].map(state_name)
print(state_visit_census)

states_and_uncertainty = state_visit_census.merge(new_df, left_on="STATE", right_on="state", how="left")
print(states_and_uncertainty.info())

## I referenced this article for support onthis: https://stackoverflow.com/ques
## tions/25888207/pandas-join-dataframes-on-field-with-different-names

# Question 2.7: Using groupby on the VISITED column in the dataframe resulting 
# from the previous question, answer the following questions and show how you  
# calculated them: a) what is the single smallest state by 2022 population  
# that you have visited, and not visited?  b) what are the three largest states  
# by 2022 population you have visited, and the three largest states by 2022 
# population you have not visited? c) do states you have visited or states you  
# have not visited have a higher average EPU-C value in 2022?
states_and_uncertainty.sort_values("POPESTIMATE2022").groupby(["STATE", "VISITED"]).head()
## Wyoming, Vermont
states_and_uncertainty.sort_values("POPESTIMATE2022", ascending=False).groupby(["STATE", "VISITED"]).head()
## Texas, New York, Illinois. Pennsylvania, New Jersey, Virginia
states_and_uncertainty.groupby("VISITED")["EPU-C"].mean()
# Question 2.8: Transforming data to have mean zero and unit standard deviation
# is often called "standardization", or a "zscore".  The basic formula to 
# apply to any given value is: (value - mean) / std
# Return to the long-form EPU data you created in step 2.4 and then, using groupby
# and a function you write, transform the data so that the values for EPU-C
# have mean zero and unit standard deviation for each state.  Add these values
# to a new column named EPU_C_zscore.



