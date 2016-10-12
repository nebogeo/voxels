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
	

#city="BD"
#x_org,y_org = 7,18
#x_val,y_val = 7,18

city="LT"
x_org,y_org = 20,20
x_val,y_val = 20,21

#city="MK"
#x_org,y_org = 9,24
#x_val,y_val = 10,25

vox_image = '../data/voxels/'+city+'/'+city+'_'+str(x_val)+'.'+str(y_val)+'/vox390.'+city+'.'
ndvi_image = '../data/voxels/'+city+'/ndviPositive.'+city+'.section.tif'

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

def material(value, ndvi, x, y, i, greenonly):
        col = -1
        vox_thresh = 0.01
        ndvi_thresh = 0.2
        mat = MELON
        low_thresh = 2
        building_col=0
        if greenonly: building_col=-1
        
        if value>=vox_thresh:        
                # tree
                if i >= 9 and i <=70 and ndvi >= ndvi_thresh:
                        col = 0 
                        mat = 18 # leaves
                        #if value>=0.2: mat=17 # wood

                # grass
                elif i <= low_thresh and ndvi >= ndvi_thresh:
                        col = 0 # grass 
                        mat = 2 # grass

                # building
                elif i > low_thresh and i <= 70 and ndvi < ndvi_thresh:
                        col = building_col 
                        mat = 45 # brick block

                # shrub
                elif i > low_thresh and i <= 8 and ndvi >= ndvi_thresh:
                        col = 13 
                        mat = 35 # wool
                        #if value>=0.2: mat=17 # wood

                # road
                elif i <= low_thresh and ndvi < ndvi_thresh:
                        col = building_col
                        mat = 7 # bedrock

        #if ndvi >= ndvi_thresh and col > 0:
        if col >= 0:
                xx = x-127
                yy = y-127
		mc.setBlocks(xx,i,yy, xx+2,i,yy+2, mat, col)
		#mc.setBlocks(127-x,i,y-127,
                #             (127-x)+1,i+1,(y-127)+1, WOOL.id, col)
	
def get_ndvi(ndvi,x,y):
        size = 260
        ydiff = 1-(y_val-y_org)
        xdiff = x_val-x_org
        return ndvi[x+(ydiff*size)][y+(xdiff*size)]

def png_convert(images):
        ndvi = load_ndvi_image()
        # draw the base layer at -1
        size = 260/3
        for x in range(0,size):
                for y in range(0,size):
                        xx = x*3
                        yy = y*3
                        material(1,get_ndvi(ndvi,x,y),xx,yy,-1,False)
                        
	for i, image in enumerate(images):
		print "layer", i
		for x, line in enumerate(image):
			for y, value in enumerate(line):
                                xx = x*3
                                yy = y*3
                                #if x>50 and y>0 and x<100 and y<50:
                                material(value, get_ndvi(ndvi,x,y), xx, yy, i, True)
		print "layer", i, "complete"
	
	return

# create an array of each image for this section
images = [process_image(x_val, y_val, x) for x in range(0,71)]

bulldoze()
png_convert(images)

