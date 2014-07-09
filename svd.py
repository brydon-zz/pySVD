'''
This program performs basic image compression on a file using the SVD.

The file user loads a file in via the command line, or we assume they mean to open my half dome picture.

After the file is loaded in 

Created on 2014-04-01

@author: Brydon Eastman
@website: beastman.ca

'''

import sys, os, numpy, pylab, time
from multiprocessing import Process, Queue

def main(fileName):
		image = pylab.imread(fileName)

		print "Our image is %d x %d\n"%(image.shape[1],image.shape[0])
		totNums = 3*image.shape[1]*image.shape[0]
		print "So we're storing %d numbers"%(totNums)

		# show the initial image
		pylab.imshow(image)
		pylab.show()

		print "Splitting the image into red, green, and blue matrices..."
		R = image[:,:,0]
		G = image[:,:,1]
		B = image[:,:,2]
		print "Done!"

		""" Fancy Multithreading function """
		def doSVD(q,R,colour='red'):
			def SVD(R,colour):
				U,S,V = numpy.linalg.svd(R,full_matrices=True)
				print "There are %d \"%s\" singular values ranging from %f to %f"%(S.size,colour,S[0],S[-1])
				return U,S,V,colour
			q.put(SVD(R,colour))

		print "Calculating the SVDs"

		""" Queues up the three SVD functions """
		q = Queue() #Queue is such a weird word.
		p1 = Process(target=doSVD, args=(q,R,'red'))
		p2 = Process(target=doSVD, args=(q,B,'blue'))
		p3 = Process(target=doSVD, args=(q,G,'green'))

		p1.start()
		p2.start()
		p3.start()

		""" Get the results, unordered!!! """
		r1 = q.get()
		r2 = q.get()
		r3 = q.get()

		""" This only returns after all 3 processes have died 
				So later in the code I reference Ur as the "red" U, 
				similarly with Ug and Ub.
				I /could/ just store my results in as key/val pairs
				in a dictionary. But I got lazy, and this following
				for loop only takes 3 iterations and worst case 6 
				comparisons. It's probably just as efficient as
				setting up key/val pairs in the dictionary,
			  just a little more convuluted.
		"""
		
		for x in [r1,r2,r3]:
			if x[-1] == "red":
				Ur = x[0]
				Sr = x[1]
				Vr = x[2]
			elif x[-1] == "green":
				Ug = x[0]
				Sg = x[1]
				Vg = x[2]
			elif x[-1] == "blue":
				Ub = x[0]
				Sb = x[1]
				Vb = x[2]


		""" Now that we have the SVD in full, ask the user 
				how many terms of the outer product they wanna
				use for the compressed image. We sit in a loop
				so they can experiment with different k vals.
				An empty string, q, exit, or quit will exit them
				from the loop.
		"""
		while True:
			k = raw_input("Please enter the number of terms to keep from the outer product form of the SVD: ")
			if k in ['q','','exit','quit']:
				break
			else:
				try:
					k = int(k)
				except:
					continue

			numNums = k*(1+Ur.shape[1]+Vr.shape[0])+k*(1+Ug.shape[1]+Vg.shape[0])+k*(1+Ub.shape[1]+Vb.shape[0])
			print "With %d terms we are only storing %d numbers!"%(k,numNums)
			print "That's %d percent"%(100.*numNums/totNums)
			r = numpy.zeros(R.shape)
			g = numpy.zeros(R.shape)
			b = numpy.zeros(R.shape)

			for i in range(k):
				r += Sr[i]*numpy.outer(Ur[:,i],Vr[i])
				g += Sg[i]*numpy.outer(Ug[:,i],Vg[i])
				b += Sb[i]*numpy.outer(Ub[:,i],Vb[i])
			
			# make the image out of the the three RGB arrays
			# the first swap axes cmd gets us our RGB array
			# the second is a 'transpose' of the associated 2D array.
			compressedImage = numpy.array([r,g,b]).swapaxes(0,2).swapaxes(0,1)

			# these two lines use numpy 'fancy indexing', it's awesome
			compressedImage[compressedImage>255]=255 	# anything over 255 has to be scaled down
			compressedImage[compressedImage<0]=0			# anything under 0 has to be scaled up

			# just gotta make sure we have the right data type in here.
			compressedImage = numpy.array(compressedImage,image.dtype)

			# output it why not
			pylab.imsave("compressed_image.jpg", compressedImage)

			# Just for comparison purposes
			print "Here is five randomly sampled locations in the original matrix verse their representation in our approximate matrix\n"

			X = numpy.random.random_integers(image.shape[1],size=5)
			Y = numpy.random.random_integers(image.shape[0],size=5)

			for index,i in enumerate(X):
				j = Y[index]
				print image[j,i]
				print compressedImage[j,i]
				print ""

			# actually bother to show the thing
			pylab.imshow(compressedImage)
			pylab.show()

		
if __name__ == '__main__':
    fileName = "halfDomeSmall.jpg"
    if len(sys.argv) > 1:
        if len(sys.argv) > 1:
            if os.path.isfile(sys.argv[1]):
                fileName = sys.argv[1]
    main(fileName)
