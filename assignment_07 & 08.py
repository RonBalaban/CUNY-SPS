# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 11:23:21 2024

@author: Ron
"""

"""
In this homework assignment, you will explore and analyze a public dataset of your choosing. Since this assignment is “open-ended” in nature,
you are free to expand upon the requirements below. However, you must meet the minimum requirments as indicated in each section.

You must use Pandas as the primary tool to process your data.
The preferred method for this analysis is in a .ipynb file. Feel free to use whichever platform of your choosing.

https://www.youtube.com/watch?v=inN8seMm7UI (Getting started with Colab).

Your data should need some "work", or be considered "dirty". You must show your skills in data cleaning/wrangling.

Some data examples:
• https://www.data.gov/
• https://opendata.cityofnewyork.us/
• https://datasetsearch.research.google.com/
• https://archive.ics.uci.edu/ml/index.php


Resources:
• https://pandas.pydata.org/pandas-docs/stable/getting_started/10min.html
• https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.html

Headings or comments
You are required to make use of comments, or headings for each section. You must explain what your code is doing,
and the results of running your code. Act as if you were giving this assignment to your manager - you must include clear and descriptive information for each section.

"""

#------------------------------------------------------------------------------
#Introduction
#In this section, please describe the dataset you are using. Include a link to the source of this data. You should also provide some explanation on why you choose this dataset.
"""
I'll be using the dataset- 'Estimation of Obesity Levels Based On Eating Habits and Physical Condition', which includes data for estimating obesity rates from individuals in Mexico,
Peru, and Colombia based on several factors such as their eating habits and diet, physical activity, age, height, family history with weight issues, smoking, and methods of transportation.
The data has 17 fields with 2,111 observations and was obtained in this study: (https://www.semanticscholar.org/paper/Dataset-for-estimation-of-obesity-levels-based-on-Palechor-Manotas/35b40bacd2ffa9370885b7a3004d88995fd1d011)

It was published by the UC Irvine Machine Learning Center, and can be accessed here: (https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition)
Data was collected using a web platform with a survey, where anonymous users answered each question


The data can also be accessed through the github repo: (https://github.com/uci-ml-repo/ucimlrepo)

I chose this dataset as I wanted to see which contributing factors lead to severe risk of obesity. I anticipate that there's different weights to each field to determine which had a larger impact on the individuals obesity,
and while it's obvious to say water intake, diet, movement, exercise, and medical history all have an impact, I'd like to know just how much each field does.

"""


# Import needed libraries for analysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.patches as mpatches
import seaborn as sns







# fetch dataset from github, and make it a dataframe- 'Estimation of Obesity Levels Based On Eating Habits and Physical Condition'
url = 'https://raw.githubusercontent.com/RonBalaban/CUNY-SPS-R/main/ObesityDataSet_raw_and_data_sinthetic.csv'
obesity_df = pd.read_csv(url)


#------------------------------------------------------------------------------
"""
Data Exploration
Import your dataset into your .ipynb, create dataframes, and explore your data.
Include:
• Summary statistics means, medians, quartiles,
• Missing value information
• Any other relevant information about the dataset.
"""

# Sample 5 rows of the data
obesity_df.head(5)


# summary of our dataframe, columns, datatypes, and nulls
obesity_df.info()


# Descriptive summary statistics of all columns- means, medians, quantiles, uniques, most common occurence for each field.
obesity_df.describe(include='all')


# Check for null/missing values, in this case we're missing none.
obesity_df.isnull().sum()
obesity_df.isna().sum()
# If we had missing values, we could drop them with droppedDf = df.dropna()
# We could check the count of missing values with df.isnull().sum().sort_values(ascending=FALSE)




#------------------------------------------------------------------------------
"""
Data Wrangling
Create a subset of your original data and perform the following. You are free (and should) to add on to these questions.
Please clearly indicate in your assignment your answers to these questions.
• Modify multiple column names.
• Look at the structure of your data – are any variables improperly coded? Such as strings or characters? Convert to correct structure if needed.
• Fix missing and invalid values in data.
• Create new columns based on existing columns or calculations.
• Drop column(s) from your dataset.
• Drop a row(s) from your dataset.
• Sort your data based on multiple variables.
• Filter your data based on some condition.
• Convert all the string values to upper or lower cases in one column.
• Check whether numeric values are present in a given column of your dataframe.
• Group your dataset by one column, and get the mean, min, and max values by group.
• Groupby()
• agg() or .apply()
• Group your dataset by two columns and then sort the aggregated results within the groups.
"""


# Check Column names
print(obesity_df.keys())


# Rename confusing column names
obesity_df = obesity_df.rename(columns={
    "Height": "Height_m",
    "Weight": "Weight_kg",
    "family_history_with_overweight" : "overweight_history",
    "FAVC"  : "eat_high_calories",
    "FCVC"  : "eat_vegetables",
    "NCP"   : "number_daily_meals",
    "CAEC"  : "eat_between_meals",
    "SMOKE" : "smoke",
    "CH2O"  : "water",
    "SCC"   : "monitor_calories",
    "FAF"   : "physical_activity",
    "TUE"   : "time_technology",
    "CALC"  : "frequency_alcohol",
    "MTRANS": "mode_transport",
    "NObeyesdad" : "obesity_level"
})





# Certain columns values don't make sense, and must be renamed.
# The study questions (https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition) has all the valid values for all fields.


# 1) Age should be an integer or float, stick to 1 value rather than both- let's use int.
# obesity_df_temp = obesity_df[obesity_df['Age'] % 1 != 0]
# The code above checks how many rows in the df have age as an integer, so 736 are integers and 1375 are floats.
obesity_df['Age'] = obesity_df['Age'].astype(int) # Converts them all to int



# 2) eat_vegetables should be 'never/sometimes/always', but its a float ranging from 1-3.
# Let's assume (since the study doesn't tell us), that 1= never, 2=sometimes, 3=always. Lets test the logic;
# obesity_df_temp =  obesity_df[(2 < obesity_df['eat_vegetables']) & (obesity_df['eat_vegetables'] < 3)]
# 652 with 3, 600 with 2, 33 with 1. I believe my mapping of the above is valid.
# Now let's check to see how many are 'in-between', meaning they're float values;
# 657 between 2 and 3, and 169 between 1 and 2. The sum is 2111 so this adds up.
# However, it doesn't make sense to have any values besides 1, 2, or 3. Let's change the floats to the nearest integer.
obesity_df['eat_vegetables'] =  obesity_df['eat_vegetables'].round(decimals=0)
# After running this block of code, we see that we no longer have anything besides 1/2/3. Let's check how many we have of each;
# obesity_df_temp =  obesity_df[(obesity_df['eat_vegetables'] == 3)]
# 102 with 1, 1013 with 2, 996 with 3. Inspecting the dataframe, I can see that all floats below X.5 became X, and all above X.5 became X+1
# Now we'll replace all 1's with 'never', all 2's with 'sometimes', and all 3's with 'always'
obesity_df['eat_vegetables'] = obesity_df['eat_vegetables'].replace(1, "Never")
obesity_df['eat_vegetables'] = obesity_df['eat_vegetables'].replace(2, "Sometimes")
obesity_df['eat_vegetables'] = obesity_df['eat_vegetables'].replace(3, "Always")
# We've succesfully replaced all ints with valid strings



# 3) On first thought, number_daily_meals should be 'between 1 and 2/between 2 and 3/ 3/ more than 3'
# Similar to the above, it doesn't make sense to say you had 1.66 of a meal (for example). We'll replace all values with ints, then strings
obesity_df['number_daily_meals'] =  obesity_df['number_daily_meals'].round(decimals=0)
# We've changed the floats to ints, now to make them valid strings
obesity_df['number_daily_meals'] = obesity_df['number_daily_meals'].replace(1, "1 to 2 meals")
obesity_df['number_daily_meals'] = obesity_df['number_daily_meals'].replace(2, "2 to 3 meals")
obesity_df['number_daily_meals'] = obesity_df['number_daily_meals'].replace(3, "3 meals")
obesity_df['number_daily_meals'] = obesity_df['number_daily_meals'].replace(4, "More than 3 meals")
# We've succesfully replaced all ints with valid strings



# 4) water should be 'less than liter / between 1 and 2L / more than 2L'
# At first glance, the floats seem valuable if we want to know how many liters of water someone drinks daily
# However, it's implausible for someone to know they drank 2.475 liters of water a day, they'd just say more than 2L so we'll do the same.
obesity_df['water'] =  obesity_df['water'].round(decimals=0)
# We've changed the floats to ints, now to make them valid strings
obesity_df['water'] = obesity_df['water'].replace(1, "1: Less than 1 liter")
obesity_df['water'] = obesity_df['water'].replace(2, "2: Between 1 and 2 Liters")
obesity_df['water'] = obesity_df['water'].replace(3, "3: More than 2 Liters")
# We've succesfully replaced all ints with valid strings




# 5) physical_activity should be 'I don't have / 1 or 2 days/ 3 or 4 days / More than 4 days'
obesity_df['physical_activity'] =  obesity_df['physical_activity'].round(decimals=0)
# We'll replace the 1/2/3/4 with the above strings
obesity_df['physical_activity'] = obesity_df['physical_activity'].replace(0, "0 days")
obesity_df['physical_activity'] = obesity_df['physical_activity'].replace(1, "1/2 days")
obesity_df['physical_activity'] = obesity_df['physical_activity'].replace(2, "3/4 days")
obesity_df['physical_activity'] = obesity_df['physical_activity'].replace(3, "> 4 days")
# We've succesfully replaced all ints with valid strings




# 6) time_technology should be '0-2 hours / 3-5 hours / more than 5 hours'
obesity_df['time_technology'] =  obesity_df['time_technology'].round(decimals=0)
# We'll replace the 0/1/2 with the above strings
obesity_df['time_technology'] = obesity_df['time_technology'].replace(0, "0-2 hours")
obesity_df['time_technology'] = obesity_df['time_technology'].replace(1, "3-5 hours")
obesity_df['time_technology'] = obesity_df['time_technology'].replace(2, "More than 5 hours")
# We've succesfully replaced all ints with valid strings



# 7) frequency_alcohol 'no' should be 'Never'
obesity_df['frequency_alcohol'] = obesity_df['frequency_alcohol'].replace("no", "Never")



# 8) Let's also make the weight_kg an int, for sake of future analysis
obesity_df['Weight_kg'] =  obesity_df['Weight_kg'].round(decimals=0)



# 9) For the sake of analysis, let's make a custom order to the obesity categories. Starting from insufficient weight -> Obesity 3. This will make it more easy to view and understand the analysis.
obesity_df['obesity_level'] = obesity_df['obesity_level'].replace("Insufficient_Weight", "1: Insufficient_Weight")
obesity_df['obesity_level'] = obesity_df['obesity_level'].replace("Normal_Weight", "2: Normal_Weight")
obesity_df['obesity_level'] = obesity_df['obesity_level'].replace("Overweight_Level_I", "3: Overweight_Level_I")
obesity_df['obesity_level'] = obesity_df['obesity_level'].replace("Overweight_Level_II", "4: Overweight_Level_II")
obesity_df['obesity_level'] = obesity_df['obesity_level'].replace("Obesity_Type_I", "5: Obesity_Type_I")
obesity_df['obesity_level'] = obesity_df['obesity_level'].replace("Obesity_Type_II", "6: Obesity_Type_II")
obesity_df['obesity_level'] = obesity_df['obesity_level'].replace("Obesity_Type_III", "7: Obesity_Type_III")







# frequency of the different obesity types
counts_obesity = obesity_df["obesity_level"].value_counts().reset_index()
display(counts_obesity)
# As we can see, only 287/ 2111 people are of a normal weight, 272 are underweight, and the rest are overweight/obese.




# Let's see if the number of meals has an effect on the obesity level. One flaw however, is that this doesn't account for what kind of meals
# I.e- a healthy person who's highly active person who drinks water and avoids high calorie meals, vs a slovenly person binging unhealthy food.
# cross tab of weight and meals
crosstab_obesity_meals = pd.crosstab(index=obesity_df['obesity_level'], columns=obesity_df['number_daily_meals'])
# if both eat 3 meals, then the data doesn't distinguish that. However, we have a field to account for that- 'eat_high_calories'




# Let's filter and make a new dataframe, just for those who eat high calorie meals
high_calories_df = obesity_df[obesity_df["eat_high_calories"] == 'yes']
# This new dataframe has 1866 rows, meaning the vast majority of the total 2111 consume high_calorie meals
# Now let's check this new crosstab to see how it compares to the prior.
crosstab_obesity_meals_high_calories = pd.crosstab(index=high_calories_df['obesity_level'], columns=high_calories_df['number_daily_meals'])


# We can see here that of those who eat high-calorie meals, the more high-calorie meal one eats, the higher their chance of obesity
# In fact, for those with 'Obesity_Type_III], they only ever eat 3 meals.  More interesting, is that when comparing the original crosstab to the high-calorie crosstab,
# we see that including only-high calorie meals has effects on lowering quantities across the different obesity levels. This is barely true for Obesity level I/II/III, as their counts barely change.
display(crosstab_obesity_meals)
display(crosstab_obesity_meals_high_calories)






# Weight by group (https://pandas.pydata.org/pandas-docs/version/1.2.2/getting_started/intro_tutorials/06_calculate_statistics.html)
# average
obesity_df[["obesity_level", "Weight_kg"]].groupby("obesity_level").mean().sort_values(by=["Weight_kg"], ascending=True)
# min
obesity_df[["obesity_level", "Weight_kg"]].groupby("obesity_level").min().sort_values(by=["Weight_kg"], ascending=True)
# max
obesity_df[["obesity_level", "Weight_kg"]].groupby("obesity_level").max().sort_values(by=["Weight_kg"], ascending=True)




# See the average ages, heights, weights by weight type
obesity_df.sort_values(['Weight_kg', 'obesity_level'])
obesity_df.groupby('obesity_level').agg(['mean']).sort_values(('Weight_kg', 'mean'))
# To sort multiple variables differently;
obesity_df.sort_values(['Weight_kg', 'obesity_level'], ascending= [True, False])



# Pivot the data- let's see the breakdown of obesity levels by exercise/water intake.
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.pivot_table.html
pivot_obesity_water_exercise = pd.pivot_table(obesity_df,
                              index =['obesity_level','water'],
                              columns = ['physical_activity'],
                              values= ["Age"],
                              aggfunc='count')
# This pivot table actually shows an obvious and logical metric; those who fall into the higher weight categories rarely exercise.
# However, it does offer an interesting insight; there is a small portion of those who are overweight who are trying to get in shape- exercising 3/4 days.




"""
# Identical to the above pivot, but add the subtotals for each row and column
temp_table = pd.pivot_table(obesity_df,
                       index=['obesity_level','water'],
                       values=['Age'],
                       columns=['physical_activity'],
                       aggfunc='count',
                       fill_value=0,
                       margins=True) #We need the row total which we can get with the margins function in our pivot table


temp_table['% total'] = (temp_table['Age']/temp_table['Age'].sum())*100


#!!!!!!! For future analysis; https://www.geeksforgeeks.org/how-to-include-percentage-in-pivot-table-in-pandas/
https://absentdata.com/pandas/calculate-percent-in-pandas-pivot-table/
Making percentages
"""






# Make a new column, based on 'overweight_history', 'eat_high_calories', , 'physical_activity' , 'obesity_level'
# Make a temporary dataframe of the original, to experiment new field on. Deep copy so as to not affect original dataframe
obesity_df_new = obesity_df.copy(deep=True)

"""
# Unfortunately, none of these methods work

# Create new column from function
def severe_risk(row):
    if "overweight_history" == "yes":
        answer = "Yes"
    else:
        answer = "No"
    return answer


# Method 1
obesity_df_new["Severe_obesity_risk"] = obesity_df_new.apply(severe_risk, axis=1)

# Method 2
obesity_df_new['Severe_obesity_risk'] = ["yes" if 'overweight_history' == 'yes' else "no"  for x in obesity_df_new['overweight_history']]

# Method 3
# Vectorize the function
func = np.vectorize(severe_risk)
# Create a new column based on the function
obesity_df_new["Severe_obesity_risk"] = func('overweight_history')

# Method 4; .isin()
specific_criteria = mydf['field'].isin(["Value1","Value2"])
mydf[specific_criteria]



# Subset for rows in South Atlantic or Mid-Atlantic regions
regions = ["South Atlantic", "Mid-Atlantic"]
condition = homelessness["region"].isin(regions)
south_mid_atlantic = homelessness[condition]

south_mid_atlantic = homelessness[homelessness["region"].isin(regions)]
south_mid_atlantic = homelessness[homelessness["region"].isin(["South Atlantic", "Mid-Atlantic"])]




"""

# Method 4- works!
# This creates a new column for those who are in severe risk, by eating unhealthy food, with a history of such issues in the family, and don't exercise.
obesity_df_new['Severe_obesity_risk'] = np.where(
                                          (obesity_df_new['overweight_history'] == 'yes') &
                                          (obesity_df_new['eat_high_calories'] == 'yes') &
                                          (obesity_df_new['physical_activity'] == '0 days') &
                                          (obesity_df_new['obesity_level'] != '2: Normal_Weight') &
                                          (obesity_df_new['obesity_level'] != '1: Insufficient_Weight')
                                          #(obesity_df_temp[(obesity_df_temp['obesity_level'].str.contains('obesity'))])
                                          #(obesity_df_temp[obesity_df_temp['obesity_level'].isin(["5: Obesity_Type_I", "6: Obesity_Type_II", "7: Obesity_Type_III"])])
                                          , 'Yes', 'No')




# Make the Severe_obesity_risk column values uppercase
#obesity_df_new['Severe_obesity_risk'] = obesity_df_new['Severe_obesity_risk'].str.upper()




# I don't believe we need to see how much technology a person uses to view its effects on their obesity. As long as their diet/exercise/water intake/etc. are alright
# obesity_df_new = obesity_df_new.drop(['time_technology'], axis=1)


# Dropping rows where weight is insufficient
#indexweight = obesity_df_new[(obesity_df_new['obesity_level'] == '1: Insufficient_Weight') ].index
#obesity_df_new.drop(indexweight, inplace=True)




# Multiple groupby and sort on Severe risk vs age
# https://stackoverflow.com/questions/17679089/pandas-dataframe-groupby-two-columns-and-get-counts
activity_vs_obesity = obesity_df_new.groupby(['physical_activity', 'obesity_level'])['Severe_obesity_risk'].count().sort_values( ascending=False)



# Add BMI column
obesity_df_new["BMI"] = obesity_df_new["Weight_kg"] /  obesity_df_new["Height_m"]**2




# Seperate dataframe of those with existing history of obesity;
# overweight_history_df = obesity_df[(obesity_df['overweight_history'] == "yes") & (obesity_df['Age'] <25)]



#------------------------------------------------------------------------------
"""
Conclusions
After exploring your dataset, provide a short summary of what you noticed from this dataset. What would you explore further with more time?
"""
# After analyzing, I found that the vast majority of people in this dataset, nearly 80% are unhealthy- either too little weight, or overweight.
# Of the 2111 people, 1139 are some category of obese. Most of these individuals are not exercising enough, and a concering amount are eating  high calorie meals.
# Of the 2111 people, 1866 eat high calorie food. The 244 who abstain from such food have lower rates of obesity.
# For future analysis, I'll explore how much exercise and water each bucket does- bucket meaning those who eat high calories vs those who don't.
# interestingly enough, I did see within my analysis a small subset of those who are obese, eat high calorie food, but do actually exercise 3/4+ days a week. Good for them!
# I'd also like to explore those with a family history of obesity, along with smoking/alcohol/exercise habits



"""
Visualizations
The main purpose of this assignment is to practice creating various visualizations using the matplotlib and seaborn library.

Part 1: Using matplotlib, create two or more plots that incorporate at least 5 of the following properties:

Note: these properties vary based on your data. The goal is to practice creating visualizations and modifying its properties.
X Use and change a legend position
X Change a legend font size
X Place a legend outside of the plot
• Create a single legend for all subplots
X Change the title and x/y labels
• Change the marker, line colors, and line width
• Add annotations
X Modify Axis Text Ticks/Labels
X Change size of axis Labels
X Your own choice not included above

Plots that you can create include:
You can add another plot not listed here if it works better for your data. This is not a complete list of plots to create.
• Scatter Plot
X Bar plot
• Line Chart
• Multi Plots (e.g. using .subplot()
X Histogram


Part 2: Recreate the visualizations above using the Seaborn library as best as possible.
You are required to explain what each of your plots is representing. Plots without comments will not be accepted. In addition, please explain the properties you are showcasing.

Part 3: In a comment or text box, explain the differences between creating a plot in matplotlib and seaborn, based on your above plots.
"""

######## Plots ######## 

##### Plot 1 ##### 
### Matplotlib
# Stacked Bar plot; obesity_level count vs Gender 
crosstab_obesity_gender = pd.crosstab(obesity_df_new['Gender'], obesity_df_new['obesity_level']) #Make crosstab for our data breakdown
# this method also works; obesity_df_new.groupby('Gender')['obesity_level'].value_counts().unstack()
crosstab_obesity_gender.plot(kind='barh', stacked=True)  #Stacked barplot
plt.title("Obesity by Gender", fontsize = 15) #Title
plt.xlabel('Gender') #Label
plt.ylabel('Obesity') #Label
plt.style.use("fivethirtyeight")  #Style
plt.xticks([0,100,200,300,400,500,600,700,800,900,1000])  #Change the x-axis ticks to be more detailed
plt.legend(title='Obesity Level', loc ="lower right", fontsize="10") #Move legend location
plt.show() #Show plot


### Seaborn
# Regular barplot
sns.set_style("whitegrid") #Style
sb1 = sns.countplot(x='Gender', data=obesity_df_new, hue = 'obesity_level') #Make plot. No y-label as we want count
sb1.set_title("Obesity by Gender", y=1.05) #Title
sb1.set(xlabel = 'Gender', ylabel='Count') # Label
plt.show() #Show plot






#####  Plot 1.5 ##### 
### Matplotlib
# See percentages of obesity type for the above plot
# https://stackoverflow.com/questions/50160788/annotate-stacked-barplot-matplotlib-and-pandas

# Define the plot
percentage_obese_gender = 100 * crosstab_obesity_gender.divide(crosstab_obesity_gender.sum(axis = 1), axis = 0)
percentage_obese_gender.plot.bar(stacked=True)

# Calculate the % for each obesity level by gender for above plot
ax = percentage_obese_gender.plot.bar(stacked=True)
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    ax.text(x+width/2, 
            y+height/2, 
            '{:.2f} %'.format(height), 
            horizontalalignment='center', 
            verticalalignment='center')
    
# Rotate the column labels
plt.xticks(rotation=0, size=20)
#Plot title
plt.title("Obesity by Gender", fontsize = 15)



### Seaborn
# Stacked barplot
# https://stackoverflow.com/questions/69846902/how-to-plot-stacked-100-bar-plot-with-seaborn-for-categorical-data
# calculate the distribution of `obesity_level` per `Gender`
distribution1 = pd.crosstab(obesity_df_new.Gender, obesity_df_new.obesity_level, normalize='index')
# plot the cumsum, with reverse hue order
sns.barplot(data=distribution1.cumsum(axis=1).stack().reset_index(name='Dist'),
            x='Gender', y='Dist', hue='obesity_level',
            hue_order = distribution1.columns[::-1],   # reverse hue order so that the taller bars got plotted first
            dodge=False)










#####  Plot 2 ##### 
### Matplotlib
# Stacked Bar plot; physical_activity vs obesity_level 
crosstab_physicalactivity_obesity = pd.crosstab(obesity_df_new['physical_activity'], obesity_df_new['obesity_level'])
crosstab_physicalactivity_obesity.plot(kind='barh', stacked=True)
plt.title("Obesity vs  Exercise", fontsize = 20)
#plt.xlabel('Gender')
plt.ylabel('Days of Physical Activity')
plt.style.use("fivethirtyeight") 
plt.xticks([0,100,200,300,400,500,600,700,800,900,1000])
#plt.legend(title='Obesity Level', loc ="lower right", fontsize="10")
plt.show()





#####  Plot 2.5 ##### 
### Matplotlib
# See percentages of exercise for the above plot
# Define the plot
percentage_obese_exercise = 100 * crosstab_physicalactivity_obesity.divide(crosstab_physicalactivity_obesity.sum(axis = 1), axis = 0)
percentage_obese_exercise.plot.bar(stacked=True)

# Calculate the % for each obesity level by exercise for above plot
ax = percentage_obese_exercise.plot.bar(stacked=True)
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    ax.text(x+width/2, 
            y+height/2, 
            '{:.2f} %'.format(height), 
            horizontalalignment='center', 
            verticalalignment='center')

plt.title("Obesity vs  Exercise", fontsize = 20)
plt.xlabel('Days of Physical Activity')
# Rotate the column labels
plt.xticks(rotation=0)
plt.title("Obesity by Exercise", fontsize = 15)
# Move legend 
plt.legend(loc ="lower right", fontsize="10", bbox_to_anchor=(3.6, 70), bbox_transform=plt.gca().transData)
plt.show()




### Seaborn
# https://stackoverflow.com/questions/69846902/how-to-plot-stacked-100-bar-plot-with-seaborn-for-categorical-data
# calculate the distribution of `obesity_level` per `physical_activity`
distribution2 = pd.crosstab(obesity_df_new.physical_activity, obesity_df_new.obesity_level, normalize='index')
# plot the cumsum, with reverse hue order
sns.barplot(data=distribution2.cumsum(axis=1).stack().reset_index(name='Dist'),
            x='physical_activity', y='Dist', hue='obesity_level',
            hue_order = distribution2.columns[::-1],   # reverse hue order so that the taller bars got plotted first
            dodge=False)







#####  Plot 3  ##### 
### Matplotlib
# Histogram of BMI
plt.hist(obesity_df_new['BMI'], bins = 200, color='blue')
plt.title("BMI Histogram", fontsize = 15)
plt.show()


### Seaborn
plt.figure(figsize=(10, 6))
sns.histplot(data=obesity_df_new, x='BMI', bins=200, kde=True, hue='Gender') #kde to show the kernel density curves, by gender
plt.title('BMI Histogram') #Title
plt.xlabel('BMI') #label
plt.ylabel('Frequency') #label
plt.grid(True)
plt.show()




# Heatmap of crosstab_obesity_meals_high_calories 
# Stacked Bar plot; physical activity, obesity_level, water
# Scatterplot ; age bucket vs BMI


"""
The differences between making plots in Matplotlib vs Seaborn, is that matplotlib almost seems more 'primitive'- all the changes and visualizations I wish to 
make are very manual, and I feel like I have more control over the customization. However, this is very tedious and seaborn is very good at being efficient
and removing the tedium of matplotlib. Less code is needed, and the code itself is more compact. There also some different functionalities that I've seen 
seaborn has to offer, that I wasn't able to figure out with matplotlib.
"""












