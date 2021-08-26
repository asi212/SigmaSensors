import matplotlib.pyplot as plt
from math import cos, sin, pi

''' Set size and # of sensors'''
size = 300  # 200 or 300
sensors = 17 # 7 or 9 for 200mm, 13 or 17 for 300mm


wafer = plt.Circle((0,0), size/2, color='black', fill=False)
plt.rcParams["figure.figsize"] = (8,8)
ax = plt.gca()
ax.set_aspect('equal')
ax.cla() # clear things for fresh plot
ax.add_patch(wafer) # plot wafer circle

# change default plot range
ax.set_xlim((-size/2*1.1, size/2*1.1))
ax.set_ylim((-size/2*1.1, size/2*1.1))


def sensor_locations(r, angle):
    from math import cos, sin, pi
    center = [0,0]
    x = center[0] + (r * cos(angle))
    y = center[1] + (r * sin(angle))

    return x,y


# angles for different wafer setups
angles_7 = [90*(pi/180), 30*(pi/180), -30*(pi/180), -90*(pi/180), -150*(pi/180), -210*(pi/180)]
angles_9 = [90*(pi/180), 45*(pi/180), 0*(pi/180), -45*(pi/180), -90*(pi/180), -135*(pi/180), -180*(pi/180), -225*(pi/180)]
angles_13_1 = [90*(pi/180), 0*(pi/180), -90*(pi/180), -180*(pi/180)]
angles_13_2 = [(90-22.5)*(pi/180), (45-22.5)*(pi/180), (-22.5)*(pi/180), (-45-22.5)*(pi/180), (-90-22.5)*(pi/180),
               (-135-22.5)*(pi/180), (-180-22.5)*(pi/180), (-225-22.5)*(pi/180)]
angles_17_1 = [90*(pi/180), 45*(pi/180), 0*(pi/180), -45*(pi/180), -90*(pi/180), -135*(pi/180), -180*(pi/180), -225*(pi/180)]
angles_17_2 = [(90-22.5)*(pi/180), (45-22.5)*(pi/180), (-22.5)*(pi/180), (-45-22.5)*(pi/180), (-90-22.5)*(pi/180),
               (-135-22.5)*(pi/180), (-180-22.5)*(pi/180), (-225-22.5)*(pi/180)]

# change this if sensors will be in different order
sensor_order = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]

# plot center sensor
ax.plot(0,0, 'o', color='black')
if size == 300:
    ax.text(-12,-12,'Sensor 1', size=7)
if size == 200:
    ax.text(-8,-8,'Sensor 1', size=7)

# plot 8" 7 sensors
if size == 200 and sensors == 7:
    for i, angle in enumerate(angles_7):
        ax.plot(sensor_locations(83, angle)[0], sensor_locations(83, angle)[1], 'o', color='black')
        ax.text(sensor_locations(83, angle)[0]-8, sensor_locations(83, angle)[1]-7, 'Sensor ' + str(sensor_order[i]), size=7)

# plot 8" 9 sensors
if size == 200 and sensors == 9:
    for i, angle in enumerate(angles_9):
        ax.plot(sensor_locations(83, angle)[0], sensor_locations(83, angle)[1], 'o', color='black')
        ax.text(sensor_locations(83, angle)[0]-8, sensor_locations(83, angle)[1]-7, 'Sensor ' + str(sensor_order[i]), size=7)

# plot 12" 13 sensors
if size == 300 and sensors == 13:
    for i, angle in enumerate(angles_13_1):
        ax.plot(sensor_locations(83, angle)[0], sensor_locations(83, angle)[1], 'o', color='black')
        ax.text(sensor_locations(83, angle)[0]-11, sensor_locations(83, angle)[1]-12, 'Sensor ' + str(sensor_order[i]), size=7)
    for i, angle in enumerate(angles_13_2):
        ax.plot(sensor_locations(132, angle)[0], sensor_locations(132, angle)[1], 'o', color='black')
        ax.text(sensor_locations(132, angle)[0]-11, sensor_locations(132, angle)[1]-12, 'Sensor ' + str(sensor_order[i]), size=7)

# plot 12" 17 sensors
if size == 300 and sensors == 17:
    for i, angle in enumerate(angles_17_1):
        ax.plot(sensor_locations(83, angle)[0], sensor_locations(83, angle)[1], 'o', color='black')
        ax.text(sensor_locations(83, angle)[0]-12, sensor_locations(83, angle)[1]-12, 'Sensor ' + str(sensor_order[i]), size=7)
    for i, angle in enumerate(angles_17_2):
        ax.plot(sensor_locations(132, angle)[0], sensor_locations(132, angle)[1], 'o', color='black')
        ax.text(sensor_locations(132, angle)[0]-12, sensor_locations(132, angle)[1]-12, 'Sensor ' + str(sensor_order[i]), size=7)



#fig.savefig('plotcircles.png')