from PIL import Image
import numpy, math, sys

sys.path.append("/opt/minecraft-pi/api/python/")

from mcpi import minecraft
from mcpi.block import *

mc = minecraft.Minecraft.create()

def bulldoze():
	size=360
	height=255 
	print("bulldozing")
	mc.setBlocks(-size/2,0,-size/2,size/2,height,size/2,AIR)
	mc.setBlocks(-size/2,-1,-size/2, size/2,-1,size/2,WOOL,1)
	# change this
	#box(WOOL,point(-size/2,-1,-size/2),point(size,1,size))
	print("finished bulldozing")
	

# X value of source tile
x_val = 20
# Y value of source tile
y_val = 21
# Max Z value of source tile
z_val = 70
# X value to start crop
crop_x = 0  
# Y value to start crop
crop_y = 0

vox_image = '../data/LT_20.21/vox390.LT.'
#vox_image = 'tif/vox390.MK.'
ndvi_image = "../data/ndviPositive.LT.lemingtonRd.tif"

# Removing 'nan' from lists - replacing with 0.0 for now, creating new array
def normalise(array):
	data = []
	for line in array:
		new_items = [x if not math.isnan(x) else 0 for x in line]
		data.append(new_items)
	return data
	
# converting TIFF into arrays that we can work with
def process_image(x, y, z):  
	# Open image, convert to numpy array
	img = Image.open(vox_image+str(x)+'.'+str(y)+'.'+str(z)+'.tif')
	numpy_array = numpy.array(img)
	# image_array contains 260 arrays of values!
	image_array = normalise(numpy_array)
	return image_array

def load_ndvi_image():
	img = Image.open(ndvi_image)
	numpy_array = numpy.array(img)
	image_array = normalise(numpy_array)
	return image_array

# create an array of each image for this section
images = [process_image(x_val, y_val, x) for x in range(0,z_val + 1)]
def material(value, ndvi, x, y, i):
        col = -1
        vox_thresh = 0.01
        ndvi_thresh = 0.2

        if value>=vox_thresh:        
                if i >= 9 and i <=70 and ndvi >= ndvi_thresh:
                        col = 5 # tree
                elif i < 2 and ndvi >= ndvi_thresh:
                        col = 4 # grass
                elif i >= 1.0 and i <= 70 and ndvi < ndvi_thresh:
                        col = 7 # building
                elif i >= 1.0 and i <= 8 and ndvi >= ndvi_thresh:
                        col = 13 # shrub
                elif i < 2 and ndvi < ndvi_thresh:
                        col = 15 # road

        #if ndvi >= ndvi_thresh and col > 0:
        if col > 0:
		mc.setBlocks(x-127,i,y-127, x-127,i,y-127, WOOL.id, col)
		#mc.setBlocks(127-x,i,y-127,
                #             (127-x)+1,i+1,(y-127)+1, WOOL.id, col)
	
def png_convert(images):
        ndvi = load_ndvi_image()
        print (len(ndvi))
        # draw the base layer at -1
        size = 260
        for x in range(0,size):
                for y in range(0,size):
                        material(1,ndvi[x][y],x,y,-1)
                        
	for i, image in enumerate(images):
		print "layer", i
		for x, line in enumerate(image):
			for y, value in enumerate(line):
                                #if x>50 and y>0 and x<100 and y<50:
                                        
                                material(value, ndvi[x][y], x, y, i)
		print "layer", i, "complete"
	
	return

bulldoze()
png_convert(images)

