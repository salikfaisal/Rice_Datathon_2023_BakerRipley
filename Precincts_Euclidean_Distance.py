import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import math

# imports shapefile of Harris County Precincts
harris_county = gpd.read_file("HOUSTON_LIMITS_BOUNDARIES_PACKAGE.shp", encoding="utf-8")

# import summary level precinct data
precincts_data = pd.read_csv("Precinct_Level_Data_Summary.csv")

# Converts Precinct data in shapefile to float
harris_county['Precinct'] = harris_county['Precinct'].astype(float)

# List of Precincts targeted by BakerRipley
precincts_targeted = [9, 10, 11, 44, 46, 285, 347, 379, 411, 430, 431, 664, 752, 792, 793]

targeted_precincts_summary = precincts_data[precincts_data["Precinct"].isin(precincts_targeted)]
non_targeted_summary = precincts_data[~precincts_data["Precinct"].isin(precincts_targeted)]

targeted_anglo_perc = targeted_precincts_summary['anglovap'].sum() / targeted_precincts_summary['vap'].sum()
targeted_hisp_perc = targeted_precincts_summary['hispvap'].sum() / targeted_precincts_summary['vap'].sum()
targeted_black_perc = targeted_precincts_summary['blackvap'].sum() / targeted_precincts_summary['vap'].sum()
targeted_asian_perc = targeted_precincts_summary['asianvap'].sum() / targeted_precincts_summary['vap'].sum()

print(targeted_anglo_perc)
print(targeted_hisp_perc)
print(targeted_black_perc)
print(targeted_asian_perc)

euclidean_distances = []
for precinct_ord, precinct in non_targeted_summary.iterrows():
    anglo_euclid = math.pow(targeted_anglo_perc - precinct['AngloVAPPerc'], 2)
    hisp_euclid = math.pow(targeted_hisp_perc - precinct['HispVAPPerc'], 2)
    black_euclid = math.pow(targeted_black_perc - precinct['BlackVAPPerc'], 2)
    asian_euclid = math.pow(targeted_asian_perc - precinct['AsianVAPPerc'], 2)
    euclid_dist = math.sqrt(anglo_euclid + hisp_euclid + black_euclid + asian_euclid)
    euclidean_distances.append(euclid_dist)
non_targeted_summary['Euclidean_Distance'] = euclidean_distances
non_targeted_summary = non_targeted_summary.sort_values(by=['Euclidean_Distance'])
print(non_targeted_summary['Precinct'].tolist()[0:15])

harris_county = harris_county.merge(non_targeted_summary, how='left')

all_harris_county = harris_county.merge(precincts_data, how='left')

# Geo DataFrame containing the precincts targeted by BakerRipley
precincts_targeted_gpd = harris_county[harris_county['Precinct'].isin(precincts_targeted)]

# Geo DataFrame containing the precincts not targeted
precincts_not_targeted_gpd = harris_county[harris_county['Precinct'].isin(non_targeted_summary['Precinct'])]

ax = harris_county.plot(figsize=(10, 10), color='white', edgecolor='black', linewidth=0.5)
precincts_targeted_gpd.plot(color='maroon', ax=ax, edgecolor='black', linewidth=0.5)
precincts_not_targeted_gpd.plot(ax=ax, column='Euclidean_Distance', legend_kwds={'shrink': 0.3},
            alpha=.5, cmap='hot', legend = 'True')
ax.set_title('Similarity of Harris County Precincts to BakerRipley Targets')

ax2 = all_harris_county.plot(figsize=(10, 10), color='white', edgecolor='black', linewidth=0.5)
all_harris_county.plot(ax=ax2, column='Voter_Turnout_Rate', legend_kwds={'shrink': 0.3},
            alpha=.5, cmap='Greens', legend='True')
ax2.set_title('Voter Turnout in Harris County Precincts')


plt.show()