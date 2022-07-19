# Format the data for graphing
by_station_deep = pd.DataFrame(columns = ['STAT_ID', 'LATITUDE', 'LONGITUDE', 'TOP_LEFT', 'TOP_RIGHT', 'BOTTOM_RIGHT', 'BOTTOM_LEFT'])
by_station_shallow =  pd.DataFrame(columns = by_station_deep.columns)

variable = 'TCO2 in (mmol/kgSW)'

row = 0
by_station = s.groupby('STAT_ID')
for name, group in by_station:
    lat = group.iloc[0]['LATITUDE']
    lon = group.iloc[0]['LONGITUDE']

    by_station_deep.loc[row, 'LATITUDE'] = lat
    by_station_deep.loc[row, 'LONGITUDE'] = lon

    by_station_shallow.loc[row, 'LATITUDE'] = lat
    by_station_shallow.loc[row, 'LONGITUDE'] = lon

    by_station_deep.loc[row, 'STAT_ID'] = name
    by_station_shallow.loc[row, 'STAT_ID'] = name

    shallow = group[group['DEPTH (m)'] < 3]
    deep = group[group['DEPTH (m)'] > 19]

      #print(shallow)
    if len(shallow) == 0:
      if len(deep > 0):
        print('HELLO')

      if len(deep) == 0:
        continue

      elif len(deep) == 1:
        deep_row = deep.iloc[0]
        by_station_deep.loc[row, 'TOP_LEFT'] = deep_row[variable]
        by_station_deep.loc[row, 'TOP_RIGHT'] = deep_row[variable]
        by_station_deep.loc[row, 'BOTTOM_RIGHT'] =  deep_row[variable]
        by_station_deep.loc[row, 'BOTTOM_LEFT'] =   deep_row[variable]
      
      elif len(deep) == 2:
        deep_row = deep.iloc[0]
        deep_dupe = deep.iloc[1]
        by_station_deep.loc[row, 'TOP_LEFT'] = deep_dupe[variable]
        by_station_deep.loc[row, 'BOTTOM_LEFT'] = deep_dupe[variable]
        by_station_deep.loc[row, 'TOP_RIGHT'] = deep_dupe[variable]
        by_station_deep.loc[row, 'BOTTOM_RIGHT'] = deep_dupe[variable]

      else:
        print('Error: more than 2 deep values')
        break
    elif len(shallow) == 1:
      shallow_row = shallow.iloc[0]
      if len(deep) == 0:
        by_station_shallow.loc[row, 'TOP_LEFT'] = shallow_row[variable]
        by_station_shallow.loc[row, 'TOP_RIGHT'] = shallow_row[variable]
        by_station_shallow.loc[row, 'BOTTOM_RIGHT'] = shallow_row[variable]
        by_station_shallow.loc[row, 'BOTTOM_LEFT'] = shallow_row[variable]

      elif len(deep) == 1:
        deep_row = deep.iloc[0]
        by_station_shallow.loc[row, 'TOP_LEFT'] = shallow_row[variable]
        by_station_shallow.loc[row, 'TOP_RIGHT'] = shallow_row[variable]
        by_station_deep.loc[row, 'BOTTOM_RIGHT'] = deep_row[variable]
        by_station_deep.loc[row, 'BOTTOM_LEFT'] = deep_row[variable]

      elif len(deep) == 2:
        deep_row = deep.iloc[0]
        deep_dupe = deep.iloc[1]
        by_station_shallow.loc[row, 'TOP_LEFT'] = shallow_row[variable]
        by_station_shallow.loc[row, 'TOP_RIGHT'] = shallow_row[variable]
        by_station_deep.loc[row, 'BOTTOM_LEFT'] = deep_row[variable]
        by_station_deep.loc[row, 'BOTTOM_RIGHT'] = deep_dupe[variable]
    elif len(shallow) == 2:
      shallow_row = shallow.iloc[0]
      shallow_dupe = shallow.iloc[1]
      if len(deep) == 0:
        by_station_shallow.loc[row, 'TOP_LEFT'] = shallow_row[variable]
        by_station_shallow.loc[row, 'TOP_RIGHT'] = shallow_dupe[variable]
        by_station_shallow.loc[row, 'BOTTOM_RIGHT'] = shallow_dupe[variable]
        by_station_shallow.loc[row, 'BOTTOM_LEFT'] = shallow_row[variable]
      elif len(deep) == 1:
        deep_row = deep.iloc[0]
        by_station_shallow.loc[row, 'TOP_LEFT'] = shallow_row[variable]
        by_station_shallow.loc[row, 'TOP_RIGHT'] = shallow_dupe[variable]
        by_station_deep.loc[row, 'BOTTOM_LEFT'] = deep_row[variable]
        by_station_deep.loc[row, 'BOTTOM_RIGHT'] = deep_row[variable]
      elif len(deep) == 2:
        deep_row = deep.iloc[0]
        deep_dupe = deep.iloc[1]
        by_station_shallow.loc[row, 'TOP_LEFT'] = shallow_row[variable]
        by_station_shallow.loc[row, 'TOP_RIGHT'] = shallow_dupe[variable]
        by_station_deep.loc[row, 'BOTTOM_LEFT'] = deep_row[variable]
        by_station_deep.loc[row, 'BOTTOM_RIGHT'] = deep_dupe[variable]
    row += 1


    # Drop the nans
top_left_shallow = by_station_shallow.dropna(subset=['TOP_LEFT'])
top_right_shallow = by_station_shallow.dropna(subset=['TOP_RIGHT'])
bottom_left_shallow = by_station_shallow.dropna(subset=['BOTTOM_LEFT'])
bottom_right_shallow = by_station_shallow.dropna(subset=['BOTTOM_RIGHT'])

top_left_deep = by_station_deep.dropna(subset=['TOP_LEFT'])
top_right_deep = by_station_deep.dropna(subset=['TOP_RIGHT'])
bottom_left_deep = by_station_deep.dropna(subset=['BOTTOM_LEFT'])
bottom_right_deep = by_station_deep.dropna(subset=['BOTTOM_RIGHT'])

# Fill the whole circle if a shallow/deep is not available, use different color scale for each
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
fig.suptitle('SBNMS Sites with TA data')

# Get the max and min DIC values
min_ta = s['TA in (mmol/kgSW)'].min()
max_ta =  s['TA in (mmol/kgSW)'].max()

# Plot the shallow segments
s1 = ax.scatter(
  top_left_shallow['LONGITUDE'],
   top_left_shallow['LATITUDE'],
    c=top_left_shallow['TOP_LEFT'],
     vmin=min_ta,
      vmax = max_ta,
       cmap = 'Blues_r',
        marker=top_left,
         s = 400)
s2 = ax.scatter(
  top_right_shallow['LONGITUDE'],
   top_right_shallow['LATITUDE'],
    c=top_right_shallow['TOP_RIGHT'],
     vmin=min_ta,
      vmax = max_ta,
       cmap = 'Blues_r',
        marker=top_right,
         s = 400)
s3 = ax.scatter(
  bottom_left_shallow['LONGITUDE'],
    bottom_left_shallow['LATITUDE'],
      c=bottom_left_shallow['BOTTOM_LEFT'],
        vmin=min_ta,
          vmax = max_ta,
            cmap = 'Blues_r',
              marker=bottom_left,
                s = 400)
s4 = ax.scatter(
  bottom_right_shallow['LONGITUDE'],
    bottom_right_shallow['LATITUDE'],
      c=bottom_right_shallow['BOTTOM_RIGHT'],
        vmin=min_ta,
          vmax = max_ta,
            cmap = 'Blues_r',
              marker=bottom_right,
                s = 400)

# Set the colorbar
cbar1 = plt.colorbar(s1, ax=ax)
cbar1.set_label('TA in (mmol/kgSW) Shallow')

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')


# Plot the deep segments
d1 = ax.scatter(
  top_left_deep['LONGITUDE'],
    top_left_deep['LATITUDE'],
      c=top_left_deep['TOP_LEFT'],
        vmin=min_ta,
          vmax = max_ta,
            cmap = 'Reds_r',
              marker=top_left,
                s = 400)
d2 = ax.scatter(top_right_deep['LONGITUDE'],
    top_right_deep['LATITUDE'],
      c=top_right_deep['TOP_RIGHT'],
        vmin=min_ta,
          vmax = max_ta,
            cmap = 'Reds_r',
              marker=top_right,
                s = 400)
d3 = ax.scatter(
  bottom_left_deep['LONGITUDE'],
    bottom_left_deep['LATITUDE'],
      c=bottom_left_deep['BOTTOM_LEFT'],
        vmin=min_ta,
          vmax = max_ta,
            cmap = 'Reds_r',
              marker=bottom_left,
                s = 400)
d4 = ax.scatter(
  bottom_right_deep['LONGITUDE'],
    bottom_right_deep['LATITUDE'],
      c=bottom_right_deep['BOTTOM_RIGHT'],
        vmin=min_ta,
          vmax = max_ta,
            cmap = 'Reds_r',
              marker=bottom_right,
                s = 400)

# Add the colorbar
cbar2 = plt.colorbar(d1, ax=ax)
cbar2.set_label('TA (mmol/kgSW) Deep')

ax.set_title('SBNMS Sites with TA data')

plt.show()
