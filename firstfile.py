from datetime import datetime, timedelta
from pytz import timezone
import pytz,sys
from collections import defaultdict
import os.path,h5py,csv
import numpy as np

dataset_csv = defaultdict(list)
group_csv = defaultdict(list)
count = 0

# Callable function to be used in recursive visit of the HDF file
# It stores dataset information in the dictionary container dataset_csv and
# group information in group_csv
def recursive_visit(node_name):
    global count
    node = f.get(node_name)
    cond = bool(node)

    if cond:
        if isinstance(node, h5py.Dataset):
            count = count+1
            try:
                datatype = node.dtype
                dataset_csv[node.name].extend(list([node.shape, node.size, datatype]))
                pass
            except:
                datatype = "Not understood"
                dataset_csv[node.name].extend(list([node.shape, node.size, datatype]))
        elif isinstance(node, h5py.Group):
            node_keys= node.keys()
            group_csv[node.name].extend(node.items())
            for i in node_keys:
                count = count+1
                recursive_visit(i)
    if not cond:
        pass


file_name = "1541962108935000000_167_838.h5"

# Converting from UNIX time to UTC and CERN time
unix_nano_time = int(file_name.split("_")[0])
dt = datetime.fromtimestamp(unix_nano_time//1000000000)
print "Unix Time in Nanoseconds converted to human-readable format: ",dt
#print type(dt)
utc = pytz.utc
cern = timezone('Europe/Zurich')
utc_time = utc.localize(dt)
cern_time = cern.localize(dt)
print "UTC Time: ", utc_time
print "CERN Time(Zurich time): ",cern_time

#sys.exit()


base_dir = os.path.dirname(os.path.abspath(__file__))


with h5py.File(file_name, mode='r') as f:
    file_keys,base_groups = [],[]
    file_items = list(f.items())
    f.visit(recursive_visit)


fin_keys = dataset_csv.keys()
print len(fin_keys), count

# Saving the records in respective csv files

with open("dataset_records.csv","w") as csv_file:
    writer = csv.writer(csv_file)
    for key, value in dataset_csv.items():
        writer.writerow([key, value])

csv_file.close()

with open("group_records.csv","w") as csv_file:
    writer = csv.writer(csv_file)
    for key, value in group_csv.items():
        writer.writerow([key, value])

csv_file.close()


# Image Retrieval

imageData_gr = "/AwakeEventData/XMPP-STREAK/StreakImage/streakImageData"
im_height = "/AwakeEventData/XMPP-STREAK/StreakImage/streakImageHeight"
im_width = "/AwakeEventData/XMPP-STREAK/StreakImage/streakImageWidth"

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from scipy.signal import medfilt

with h5py.File(file_name, mode='r') as f:
    im = f.get(imageData_gr)
    im = np.array(im)
    im_h = np.array(f.get(im_height))[0]
    im_w = np.array(f.get(im_width))[0]
    print im.shape, im_h, im_w
    im = np.reshape(im,(im_h,im_w))
    filtered_im = medfilt(im)
    #img = Image.fromarray(filtered_im,mode='P')
    #img.save('my.png')
    #img.show()
    plt.imshow(filtered_im)
    plt.savefig("filtered_im.png")
    plt.show()
    #print im




