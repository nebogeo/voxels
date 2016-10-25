#!/usr/bin/env python
from PIL import Image
import numpy, math
import scipy.misc as smp
import sys, os

# Size, always square
size = int(sys.argv[1])
# X value of source tile
x_val = int(sys.argv[2])
# Y value of source tile
y_val = int(sys.argv[3])
# Max Z value of source tile
z_val = int(sys.argv[4])
# X value to start crop
crop_x = int(sys.argv[5])
# Y value to start crop
crop_y = int(sys.argv[6])

ndvi_image = "data/ndviPositive.LT.lemingtonRd.tif"
#vox_image = 'data/MK/vox390.MK.'
#vox_image = 'data/LT_'+str(x_val)+'.'+str(y_val)+'/vox390.LT.'
vox_image = 'data/BD_vox/vox390.BD.'

ndvi_offs_x=0
ndvi_offs_y=260

# range conversion - not so effective, but could be used elsewhere...
def convert(old_value):
	old_max = 1
	old_min = 0
	new_max = 255
	new_min = 0
	old_range = old_max - old_min
	new_range = new_max - new_min
	value = (((old_value - old_min) * new_range) / old_range) + new_min
	return int(value)

# Find minimum and maximum of image
def find_min_max(array):
	mins_maxs = []
	for line in array:
		mins_maxs.append(min(line))
		mins_maxs.append(max(line))
	return min(mins_maxs), max(mins_maxs)

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


def categorise(value, ndvi, x, y, z):
        col = -1
        vox_thresh = 0.01
        ndvi_thresh = 0.2
        if value>=vox_thresh:        
                if z >= 9 and z <=70 and ndvi >= ndvi_thresh:
                        col = 5 # tree
                elif z < 2 and ndvi >= ndvi_thresh:
                        col = 4 # grass
                elif z >= 1.0 and z <= 70 and ndvi < ndvi_thresh:
                        col = 7 # building
                elif z >= 1.0 and z <= 8 and ndvi >= ndvi_thresh:
                        col = 13 # shrub
                elif z < 2 and ndvi < ndvi_thresh:
                        col = 15 # road

        return col

minecraft_cols = {-1:(255,255,255),
                  5:(127,255,127),
                  4:(200,255,200),
                  7:(255,127,64),
                  13:(0,255,0),
                  15:(0,0,0)}

def get_colour(value,ndvi,x,y,z):
        ret = minecraft_cols[categorise(value,ndvi,x,y,z)]
        sc = convert(value)/255.0
        sc*=4
        return (int(ret[0]*sc),
                int(ret[1]*sc),
                int(ret[2]*sc))

def plot_cross(images, y, ndvi):
	# creating new grayscale image
	new = Image.new('RGB', (260, z_val))
        print(y)
	# enumerate over images
	for z in range(0,z_val):
                image = images[z]
		# grab 'line' of image
		line = image[y]
		for x, value in enumerate(line):
			# place pixel in x position, at image index, with density value                        
			new.putpixel((x, (z_val-1) - z), 
                                     get_colour(value,ndvi[y+ndvi_offs_x][x+ndvi_offs_y],x,y,z))
	new.save("data/out/{0:04d}.png".format(y))
	return

def safe_plot(pixels,x,y,c):
        if x>0 and x<pixels.size[0] and y>0 and y<pixels.size[1]:
                pixels.putpixel((x,y),c)

def safe_plot_mul(pixels,x,y,c):
        if x>0 and x<pixels.size[0] and y>0 and y<pixels.size[1]:
                e = pixels.getpixel((x,y))                
                pixels.putpixel((x,y),(int(e[0]+c[0]*0.4),
                                       int(e[1]+c[1]*0.4),
                                       int(e[2]+c[2]*0.4)))


def plot_smear(images, start, end, ndvi):
	# creating new grayscale image
	new = Image.new('RGB', (260*2, 260*2))

        for y in range(start,end):
                offs = y
                # enumerate over images
                for z in range(0,z_val):
                        image = images[z]
                        # grab 'line' of image
                        line = image[y]
                        for x, value in enumerate(line):
                                # place pixel in x position, at image index, with density value                        
                                safe_plot_mul(new,x+int(offs/1.5),(((420-1) - z)-(offs/2)),
                                              get_colour(value,ndvi[y+ndvi_offs_x][x+ndvi_offs_y],x,y,z))

	new.save("data/out/smear.png".format(y))

def png_convert(images):
        new = Image.new('RGBA', (260, 260))

	for i, im in enumerate(images):
                image = im[2]
		for x, line in enumerate(image):
			for y, value in enumerate(line):
                                new.putpixel((x, y), ((convert(value)), (convert(value)), (convert(value)), (convert(value))))
				# w, h = new.size
				# new_image = new.crop((crop_x, crop_y, crop_x + size, crop_y + size))
				# resized = new_image.resize((50, 50), Image.ANTIALIAS)

	
		directory = "data/out/bd/"
		if not os.path.exists(directory):
			os.makedirs(directory)

                filename = "mk-"+str(im[0])+"."+str(im[1])+".png"
		print directory, filename
		new.save(directory+filename)
		print "Saved!"

# create an array of each image for this section
#images = [process_image(x_val, y_val, x) for x in range(0,z_val + 1)]


images = []
for y in range(0,50):
        for x in range(0,50):
                try:
                        images.append([x,y,process_image(x, y, 2)])
                except: pass

# creates 260 images
#ndvi = load_ndvi_image()
#for i in range(0, 259):
	# i = 'line' of image
#	plot_cross(images, i, ndvi)

#plot_smear(images, 0,260, ndvi)

png_convert(images)


