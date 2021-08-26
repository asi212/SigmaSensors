import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog

print('Requirements: '
      ' 1. Starting the lowest temperature and containing the upcycle and downcycle'
      '2. csv file with 5s intervals'
      ' 3. Reference sensor contains "ref" in the name')

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()

# open CSV
df = pd.read_csv(file_path, index_col=0)
n_sensors = len(df.columns)
col_names = df.columns.to_list()

ref_pos = [i for i, name in enumerate(col_names) if 'ref' in name]  # index of the reference sensor
ref_pos_int = int(ref_pos[0])
'''
Determine the steady state temperatures and the times
at which they *ended (time = when temp increases or deceases
'''
up_times = []
down_times = []
up_temps = []
down_temps = []
interval = 600  #standard lookback of 300 10s intervals = 3000s. Need to do more if each temperature steady state is held for 1 hr
t = 0
while t < len(df):
    if t > 2:
        if len(up_temps) > 0:
            if (df.iloc[t][-2] - df.iloc[t-3][-2] >= 1.10 and df.iloc[t-3][-2] - df.iloc[t-6][-2] <= 1.00 and up_times[-1]
                <= t - 50) or (df.iloc[t][-2] -
                               df.iloc[t-3][-2] <= -1 and df.iloc[t-3][-2] - df.iloc[t-6][-2] >= -1 and
                               max(df.iloc[t-interval:t-100, -2]) < df.iloc[t-3][-2] + 2):  # uptrending
                # this max statement below says that the max temperature from -3000s to -1000s must be less than
                # the current temperature (plus 2, to be sure), otherwise it must be downtrending
                up_times.append(t-3)
                up_temps.append(df.iloc[t-3][ref_pos][0])
                if len(up_times) > 1:
                    interval = up_times[1] - up_times[0]  #update interval length once we have enough data
                t = t + 2 # skip 20 seconds ahead
        if len(up_temps) == 0:
            if (df.iloc[t][-2] - df.iloc[t-3][-2] >= 1.10 and df.iloc[t-3][-2] - df.iloc[t-6][-2] <= 1.00) or (df.iloc[t][-2] -
                                                                                                                df.iloc[t-3][-2] <= -1 and df.iloc[t-3][-2] - df.iloc[t-6][-2] >= -1 and
                                                                                                                max(df.iloc[t-interval:t-100, -2]) < df.iloc[t-3][-2] + 2):  # uptrending
                # this max statement below says that the max temperature from -3000s to -1000s must be less than
                # the current temperature (plus 2, to be sure), otherwise it must be downtrending
                up_times.append(t-3)
                up_temps.append(df.iloc[t-3][ref_pos][0])
                if len(up_times) > 1:
                    interval = up_times[1] - up_times[0]  #update interval length once we have enough data
                t = t + 2 # skip 20 seconds ahead
        if len(down_temps) == 0:
            if (df.iloc[t][-2] - df.iloc[t-3][-2] <= -1.00 and df.iloc[t-3][-2] - df.iloc[t-6][-2] >= -1.00
                and max(df.iloc[t-interval:t-100, -2]) > df.iloc[t-3][-2] + 2) or (t == len(df)-1 and     #or at the end and
                                                                                   max(df.iloc[t-120:t, -2]) < min(df.iloc[t-120:t, -2]) + 2 and # if the max over the past 20 min is not much greater than min, then steady state
                                                                                   max(df.iloc[t-interval:t-100, -2]) > df.iloc[t-3][-2] + 2):  # downtrending
                if t != len(df) - 1:
                    down_times.append(t-3)
                    down_temps.append(df.iloc[t-3][ref_pos][0])
                if t == len(df) - 1:
                    down_times.append(t)
                    down_temps.append(df.iloc[t][ref_pos][0])
                t = t + 2  # skip 20 seconds ahead
        if len(down_temps) > 0:
            if (df.iloc[t][-2] - df.iloc[t-3][-2] <= -1.00 and df.iloc[t-3][-2] - df.iloc[t-6][-2] >= -1.00
                and max(df.iloc[t-interval:t-100, -2]) > df.iloc[t-3][-2] + 2 and down_times[-1]
                <= t - 50) or (t == len(df)-1 and     #or at the end and
                               max(df.iloc[t-120:t, -2]) < min(df.iloc[t-120:t, -2]) + 2 and # if the max over the past 20 min is not much greater than min, then steady state
                               max(df.iloc[t-interval:t-100, -2]) > df.iloc[t-3][-2] + 2):  # downtrending
                if t != len(df) - 1:
                    down_times.append(t-10)
                    down_temps.append(df.iloc[t-10][ref_pos][0])
                if t == len(df) - 1:
                    down_times.append(t)
                    down_temps.append(df.iloc[t][ref_pos][0])
                t = t + 2  # skip 20 seconds ahead
    t = t + 1  # 10 seconds ahead

# reverse down_temps and down_times
down_temps.reverse()
down_times.reverse()

# remove the first time and temperature if it was a "false positive" and wasn't actually a steady state.
# this will happen because of the.. if abs(..) expression
try:
    if up_times[0] < 50:  # if the program determines the first steady state to occur in the first 500s, its a false positive
        up_times = up_times[1:]
        up_temps = up_temps[1:]
except:
    None

try:
    if down_times[0] < 50:
        down_times = down_times[1:]
        down_temps = down_temps[1:]
except:
    None



## Remove NaNs
try:
    up_temps.remove('nan')
except:
    None

try:
    up_times.remove('nan')
except:
    None

try:
    down_temps.remove('nan')
except:
    None

try:
    down_times.remove('nan')
except:
    None


# round temperatures to nearest 5 degrees
i = 0
while i < len(up_temps):
    up_temps[i] = round(up_temps[i]/5)*5
    i += 1
i = 0
while i < len(down_temps):
    down_temps[i] = round(down_temps[i]/5)*5
    i += 1



#make df that contains up_stats
up_stats = pd.DataFrame(columns=col_names, index=['temp', 'reference mean', 'sensor mean', 'offset',
                                                  'std dev', 'std uncertainty',
                                                  'all sensor average',
                                                  'combined wafer uncertainty', ' ']*len(up_temps))
# calculate up_stats
for i in range(len(up_temps)):
    up_stats.iloc[0+i*9][0] = 'temp = ' + str(up_temps[i])    # temp
    for c in col_names:
        up_stats.iloc[1+i*9][c] = np.mean(df[col_names[ref_pos_int]][up_times[i]-100:up_times[i]-50])   # reference mean
        up_stats.iloc[2+i*9][c] = np.mean(df[c][up_times[i]-100:up_times[i]-50])            # mean value
        up_stats.iloc[3+i*9][c] = np.mean(df[col_names[ref_pos_int]][up_times[i]-100:up_times[i]-50]) - \
                                  np.mean(df[c][up_times[i]-100:up_times[i]-50])            # offset
        up_stats.iloc[4+i*9][c] = np.std(df[c][up_times[i]-100:up_times[i]-50])              # std dev
        up_stats.iloc[5+i*9][c] = np.std(df[c][up_times[i]-100:up_times[i]-50])/np.sqrt(50)  #std uncertainty

    up_stats.iloc[6+i*9][0] = np.mean(up_stats.iloc[1+i*9][:-3])
    up_stats.iloc[7+i*9][0] = np.sqrt(sum((up_stats.iloc[3+i*9][:-3]**2)))
    i += 1


#make df that contains down_stats
down_stats = pd.DataFrame(columns=col_names, index=['temp', 'reference mean', 'sensor mean', 'offset', 'std dev',
                                                    'std uncertainty',
                                                    'all sensor average',
                                                    'combined wafer uncertainty', ' ']*len(down_temps))
# calculate down_stats
for i in range(len(down_temps)):
    down_stats.iloc[0+i*9][0] = 'temp = ' + str(down_temps[i])
    for c in col_names:
        down_stats.iloc[1+i*9][c] = np.mean(df[col_names[ref_pos_int]][down_times[i]-100:down_times[i]-50])   # reference mean
        down_stats.iloc[2+i*9][c] = np.mean(df[c][down_times[i]-100:down_times[i]-50])            # mean value
        down_stats.iloc[3+i*9][c] = np.mean(df[col_names[ref_pos_int]][down_times[i]-100:down_times[i]-50]) - \
                                    np.mean(df[c][down_times[i]-100:down_times[i]-50])            # offset
        down_stats.iloc[4+i*9][c] = np.std(df[c][down_times[i]-100:down_times[i]-50])              # std dev
        down_stats.iloc[5+i*9][c] = np.std(df[c][down_times[i]-100:down_times[i]-50])/np.sqrt(50)  #std uncertainty

    down_stats.iloc[6+i*9][0] = np.mean(down_stats.iloc[1+i*9][:-3])
    down_stats.iloc[7+i*9][0] = np.sqrt(sum((down_stats.iloc[3+i*9][:-3]**2)))
    i += 1


''' to do: when a sensor is missing, the combined uncertainty is returned as Nan... need to build warning that sensor
value is missing'''



# create hysteresis stats table by averaging
''' check to make sure we have correct number of up and down temps'''
hys_error = False
if up_temps[:-1] != down_temps or len(down_stats) + 9 != len(up_stats):
    hys_error = True
    print('there has been an error while attempting to read picolog csv data. Steady state temperatures were' +
          'not correctly determined. Please make sure the file contains both up and down-trending data.')

def av_dev(x, y):
    result = []
    for z in range(len(y)):
        temp = ((x[z]**2 + y[z]**2)/2)**0.5
        result.append(temp)
    result.append(x[-1])
    return result


if hys_error == False:
    hys_stats = up_stats.copy()
    for i in range(len(down_temps)):
        for y in range(len(col_names)):
            temp = ([sum(z)/2 for z in
                     zip(up_stats.loc['reference mean', col_names[y]],
                         down_stats.loc['reference mean', col_names[y]])
                     ])
            temp.append(up_stats.loc['reference mean', col_names[y]][-1])
            hys_stats.loc['reference mean', col_names[y]] = temp

            temp = [sum(z)/2 for z in
                    zip(up_stats.loc['sensor mean', col_names[y]],
                        down_stats.loc['sensor mean', col_names[y]])
                    ]
            temp.append(up_stats.loc['sensor mean', col_names[y]][-1])
            hys_stats.loc['sensor mean', col_names[y]] = temp

            temp = [sum(z)/2 for z in
                    zip(up_stats.loc['offset', col_names[y]],
                        down_stats.loc['offset', col_names[y]])
                    ]
            temp.append(up_stats.loc['offset', col_names[y]][-1])
            hys_stats.loc['offset', col_names[y]] = temp

            hys_stats.loc['std dev', col_names[y]] = av_dev(up_stats.loc['std dev', col_names[y]],
                                                            down_stats.loc['std dev', col_names[y]])

            hys_stats.loc['std uncertainty', col_names[y]] = av_dev(up_stats.loc['std uncertainty', col_names[y]],
                                                                    down_stats.loc['std uncertainty', col_names[y]])

    temp = [sum(z)/2 for z in
            zip(up_stats.loc['all sensor average', col_names[0]],
                down_stats.loc['all sensor average', col_names[0]])]
    temp.append(up_stats.loc['all sensor average', col_names[0]][-1])
    hys_stats.loc['all sensor average', col_names[0]] = temp



# Create rows to visually split and identify the data when viewed in a spreadsheet
up_row_holder = pd.DataFrame(columns=col_names, index=['', 'trend'])
up_row_holder.iloc[0] = '***************'
up_row_holder.iloc[1][0] = 'Uptrending'
down_row_holder = pd.DataFrame(columns=col_names, index=['', 'trend'])
down_row_holder.iloc[0] = '***************'
down_row_holder.iloc[1][0] = 'Downtrending'
hys_row_holder = pd.DataFrame(columns=col_names, index=['', 'trend'])
hys_row_holder.iloc[0] = '***************'
hys_row_holder.iloc[1][0] = 'Average of Up + Down'

#append dfs together into one df "stats"
stats = hys_row_holder.append(hys_stats)
stats = stats.append(up_row_holder)
stats = stats.append(up_stats)
stats = stats.append(down_row_holder)
stats = stats.append(down_stats)
stats = stats.replace(np.nan, '')


# rename sensors in df
new_col_names = []
for i in range(len(col_names)-1):
    new_col_names.append('Sensor ' + str(i+1))
new_col_names += col_names[-1:]
stats.columns = new_col_names

# save
save_path = file_path.rsplit('.', 1)[0] + '_stats.csv'

try:
    stats.to_csv(save_path)
    print('save successful')
except:
    print('save unsuccessful')




'''   Create offset tables from data    '''

# calculate up_stats_table
''' column names 2'''
col_names_2 = []
for x in range(len(col_names)-1):
    temp2 = [col_names[x], col_names[x] + '_ref', col_names[x] + '_offset']
    col_names_2 = col_names_2 + temp2

stats_table = pd.DataFrame(columns=col_names_2, index=['']*len(up_temps))

def offset(x,y):
    res = [None]*len(x)
    i = 0
    while i < len(res):
        temp = x[i] - y[i]
        res[i] = temp
        i += 1
    return res

# fill up_stats_table with hysteresis data
for i in range(len(col_names)-1):
    stats_table.loc[:, col_names[i]] = hys_stats.loc['sensor mean', col_names[i]].to_list()
    stats_table.loc[:, col_names[i] + '_ref'] = hys_stats.loc['reference mean', col_names[i]].to_list()
    stats_table.loc[:, col_names[i] + '_offset'] = offset(hys_stats.loc['reference mean', col_names[i]].to_list(),
                                                          hys_stats.loc['sensor mean', col_names[i]].to_list())

stats_table = stats_table.replace(np.nan, '')

''' rename columns now'''
table_cols = []
for x in range(len(col_names)-1):
    temp_list = ['Sensor ' + str(x+1) + ' Reading', 'Sensor ' + str(x+1) + ' Reference',
                 'Sensor ' + str(x+1) + ' Offset']
    table_cols = table_cols + temp_list
stats_table.columns = table_cols


# save
save_path = file_path.rsplit('.', 1)[0] + '_offset_tables.csv'

try:
    stats_table.to_csv(save_path, index=None)
    print('save successful')
except:
    print('save unsuccessful')





