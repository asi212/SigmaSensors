import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog

print('Please ensure to use *csv file with 10s interval containing all up-trending temperatures*')

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()

# open CSV
df = pd.read_csv(file_path, index_col=0)
n_sensors = len(df.columns)
col_names = df.columns.to_list()


''' this is here because what if range and mean not included in data? will that happen?'''
# picocols_yn = False
# if col_names[-1][0:5] != 'range':
#     picocols_yn = True


''' 
Determine the steady state temperatures and the times 
at which they *ended (time = when temp increases or deceases
'''
up_times = []
down_times = []
up_temps = []
down_temps = []
t = 0
while t < len(df):
    if t > 2:
        if (df.iloc[t][-2] - df.iloc[t-3][-2] >= 1 and df.iloc[t-3][-2] - df.iloc[t-6][-2] <= 1) or \
                (df.iloc[t][-2] - df.iloc[t-3][-2] <= -1 and df.iloc[t-3][-2] - df.iloc[t-6][-2] >= -1 and
                # this max statement below says that the max temperature from -3000s to -1000s must be less than
                # the current temperature (plus 2, to be sure), otherwise it must be downtrending
                 max(df.iloc[t-300:t-100, -2]) < df.iloc[t-3][-2] + 2):  # uptrending
            up_times.append(t-3)
            up_temps.append(df.iloc[t-3][-2])
            t = t + 2 # skip 20 seconds ahead
        elif df.iloc[t][-2] - df.iloc[t-3][-2] <= -1 and df.iloc[t-3][-2] - df.iloc[t-6][-2] >= -1 \
                and max(df.iloc[t-300:t-100, -2]) > df.iloc[t-3][-2] + 2:  # downtrending
            down_times.append(t-3)
            down_temps.append(df.iloc[t-3][-2])
            t = t + 2 # skip 20 seconds ahead
    t = t + 1  # 10 seconds ahead



# remove the first time and temperature if it was a "false positive" and wasn't actually a stead state.
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



#make df that contains up_stats
up_stats = pd.DataFrame(columns=col_names, index=['temp', 'mean value', 'std dev', 'std uncertainty', 'offset',
                                                  'all sensor average',
                                               'combined wafer uncertainty', ' ']*len(up_temps))
# calculate up_stats
for i in range(len(up_temps)):
    up_stats.iloc[0+i*8][0] = 'temp = ' + str(up_temps[i])
    for c in col_names:
        up_stats.iloc[1+i*8][c] = np.mean(df[c][up_times[i]-100:up_times[i]-50])
        up_stats.iloc[2+i*8][c] = np.std(df[c][up_times[i]-100:up_times[i]-50])
        up_stats.iloc[3+i*8][c] = np.std(df[c][up_times[i]-100:up_times[i]-50])/np.sqrt(50)
        up_stats.iloc[4+i*8][c] = up_temps[i] - up_stats.iloc[1+i*8][c]
    up_stats.iloc[5+i*8][0] = np.mean(up_stats.iloc[1+i*8][:-3])
    up_stats.iloc[6+i*8][0] = np.sqrt(sum((up_stats.iloc[3+i*8][:-3]**2)))
    i += 1


#make df that contains down_stats
down_stats = pd.DataFrame(columns=col_names, index=['temp', 'mean value', 'std dev', 'std uncertainty', 'offset',
                                                    'all sensor average',
                                                    'combined wafer uncertainty', 'offset', ' ']*len(down_temps))
# calculate down_stats
for i in range(len(down_temps)):
    down_stats.iloc[0+i*8][0] = 'temp = ' + str(down_temps[i])
    for c in col_names:
        down_stats.iloc[1+i*8][c] = np.mean(df[c][down_times[i]-100:down_times[i]-50])
        down_stats.iloc[2+i*8][c] = np.std(df[c][down_times[i]-100:down_times[i]-50])
        down_stats.iloc[3+i*8][c] = np.std(df[c][down_times[i]-100:down_times[i]-50])/np.sqrt(50)
        down_stats.iloc[4+i*8][c] = down_temps[i] - down_stats.iloc[1+i*8][c]
    down_stats.iloc[5+i*8][0] = np.mean(down_stats.iloc[1+i*8][:-3])
    down_stats.iloc[6+i*8][0] = np.sqrt(sum((down_stats.iloc[3+i*8][:-3]**2)))
    i += 1


# Create rows to visually split and identify the data when viewed in a spreadsheet
up_row_holder = pd.DataFrame(columns=col_names, index=['', 'trend'])
up_row_holder.iloc[0] = '***************'
up_row_holder.iloc[1][0] = 'Uptrending'
down_row_holder = pd.DataFrame(columns=col_names, index=['', 'trend'])
down_row_holder.iloc[0] = '***************'
down_row_holder.iloc[1][0] = 'Downtrending'


#append dfs together into one df "stats"
stats = up_row_holder.append(up_stats)
stats = stats.append(down_row_holder)
stats = stats.append(down_stats)
stats = stats.replace(np.nan, '')

# rename sensors in df
new_col_names = []
for i in range(len(col_names)-2):
    new_col_names.append('Sensor ' + str(i+1))
new_col_names += col_names[-2:]
stats.columns = new_col_names

# save
save_path = file_path.rsplit('.', 1)[0] + '_stats.csv'

try:
    stats.to_csv(save_path)
    print('save successful')
except:
    print('save unsuccessful')





