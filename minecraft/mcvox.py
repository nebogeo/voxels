#!/usr/bin/env python
# Minecraft LiDAR voxel visualisation
# Copyright (C) 2016 Foam Kernow, Francesca Sargent, Dave Griffiths
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PIL import Image
import numpy, math, sys

# requires Raspberry Pi version
sys.path.append("/opt/minecraft-pi/api/python/")

from mcpi import minecraft
from mcpi.block import *

mc = minecraft.Minecraft.create()

# choose your city and area	

#city="BD"
#x_org,y_org = 7,18
#x_val,y_val = 7,18

city="LT"
x_org,y_org = 20,20
x_val,y_val = 20,20

#city="MK"
#x_org,y_org = 9,24
#x_val,y_val = 9,24

do_third = True
xthird = 1
ythird = 2    
do_green_only = False

threed_print = True # thickens voxels

vox_image = '../data/voxels/'+city+'/'+city+'_'+str(x_val)+'.'+str(y_val)+'/vox390.'+city+'.'
ndvi_image = '../data/voxels/'+city+'/ndviPositive.'+city+'.section.tif'

# clears the world 
def bulldoze():
	size=360
	height=255 
	print("bulldozing")
	mc.setBlocks(-size/2,0,-size/2,size/2,height,size/2,AIR)
	mc.setBlocks(-size/2,-1,-size/2, size/2,-1,size/2,WOOL,1)
	# change this
	#box(WOOL,point(-size/2,-1,-size/2),point(size,1,size))
	print("finished bulldozing")

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

# load the vegetation index map
def load_ndvi_image():
	img = Image.open(ndvi_image)
	numpy_array = numpy.array(img)
	image_array = normalise(numpy_array)
	return image_array

# write the material for the density and vegetation index
def material(value, ndvi, x, y, i, greenonly):
        col = -1
        vox_thresh = 0.01
        ndvi_thresh = 0.2
        mat = MELON
        low_thresh = 2
        building_col=0
        size = 260
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
                xx = 127-x
                yy = y-127
		if do_third:
                        if threed_print:
                                # thicken so at 1mm per block it's 3mm print
                                mc.setBlocks(xx,i-2,yy, xx+4,i,yy+4, mat, col)
                        else:
                                mc.setBlocks(xx,i,yy, xx+2,i,yy+2, mat, col)
                else:
                        mc.setBlocks(xx,i,yy, xx,i,yy, mat, col)

# get correct section of ndvi map	
def get_ndvi(ndvi,x,y):
        size = 260
        ydiff = 1-(y_val-y_org)
        xdiff = x_val-x_org
        return ndvi[x+(ydiff*size)][y+(xdiff*size)]


def build(images):
        ndvi = load_ndvi_image()
        # calculate region if we are doing a third of the voxel map
        if do_third:
                size = 260/3
                xstart = size*xthird
                xend = size*(xthird+1)
                ystart = size*ythird
                yend = size*(ythird+1)
                block_size = 3
        else:
                # do the whole map
                size = 260
                xstart = 0
                xend = size
                ystart = 0
                yend = size
                block_size = 1
        
        worldx = 0 # minecraft world pos
        worldy = 0
        
        # draw the base layer at -1
        for x in range(xstart,xend):
                for y in range(ystart,yend):
                        material(1,get_ndvi(ndvi,x,y),worldx,worldy,1,False)
                        worldy+=block_size
                worldx+=block_size
                worldy=0
                
        # draw the rest of the layers
        for ri, image in enumerate(images):
                i = 70-ri
                i+=1
                print "layer", i
                worldx = 0 # minecraft pos
                worldy = 0
                for x in range(xstart,xend):
                        line = image[x]
                        for y in range(ystart,yend):
                                material(line[y], get_ndvi(ndvi,x,y), worldx, worldy, i, do_green_only)
                                worldy+=block_size
                        worldx+=block_size
                        worldy=0
 		print "layer", i, "complete"
	
	return

# create an array of each image for this section
images = [process_image(x_val, y_val, x) for x in range(0,71)]
images.reverse()
bulldoze()
build(images)

