#!/usr/bin/env python
import numpy as np
import cv2

#------ VALORI PREDEFINITI --------
H_MIN = 26
S_MIN = 75
V_MIN = 67
H_MAX = 256
S_MAX = 256
V_MAX = 256

IMAGE_WIDTH=160
IMAGE_HEIGHT=120

#------ FINESTRE -----------
mainGui="Immagine acquisita"
hsvWindow="Immagine HSV"
thresholdWindow="Immagine rilevata"
settingWindow="Imposta soglia"
blurWindow="Immagine con filtro Blur"

#------ IMPOSTAZIONI ELABORAZIONE ----------
enableElab=False

def onTrackbarSlide(*args):
    pass




def createSlider():
	
	cv2.namedWindow(settingWindow,1);
	
	#metodo che crea le trackbar(label, finestra, valore da cambiare, valore massimo,action listener)
	cv2.createTrackbar("H-min",settingWindow, H_MIN, 256, onTrackbarSlide)
	cv2.createTrackbar("S-min",settingWindow, S_MIN, 256,onTrackbarSlide)
	cv2.createTrackbar("V-min",settingWindow, V_MIN, 256,onTrackbarSlide)
	cv2.createTrackbar("H-max",settingWindow, H_MAX, 256, onTrackbarSlide)
	cv2.createTrackbar("S-max",settingWindow, S_MAX, 256,onTrackbarSlide)
	cv2.createTrackbar("V-max",settingWindow, V_MAX, 256,onTrackbarSlide)
	cv2.createTrackbar("Elaborazione I/O",settingWindow,0,1,onTrackbarSlide)
	


# ------- MAIN -------------


cv2.namedWindow(mainGui,1)
#imposto la sorgente per l'acquisizione
# 0 -> cam predefinita
# 1 -> cam esterna
capture = cv2.VideoCapture(0);
width,height = capture.get(3),capture.get(4)

createSlider()

rectErosione = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
rectDilataz = cv2.getStructuringElement( cv2.MORPH_RECT,(8,8))

capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)


#loop principale del programma
while True:

	#definisco la variabile per i frame catturati
	_,cameraFeed = capture.read()
	cameraFeed = cv2.flip(cameraFeed,1)
	
	#variabile su cui salvo l'immagine HSV
	hsvFrame = cv2.cvtColor(cameraFeed,cv2.COLOR_BGR2HSV)


	

	#filtro hsvFrame cercando solo un determinato range di colori
	minColor=np.array((cv2.getTrackbarPos("H-min",settingWindow),cv2.getTrackbarPos("S-min",settingWindow),cv2.getTrackbarPos("V-min",settingWindow)))
	maxColor=np.array((cv2.getTrackbarPos("H-max",settingWindow),cv2.getTrackbarPos("S-max",settingWindow),cv2.getTrackbarPos("V-max",settingWindow)))
	thresholded=cv2.inRange(hsvFrame,minColor, maxColor);
	
	#Verifico se e' stata abilitata l'elaborazione
	enableElab=cv2.getTrackbarPos("Elaborazione I/O",settingWindow)
	
	#applico erosione e dilatazione 
	if enableElab:
		cv2.erode(thresholded, thresholded,rectErosione)
		cv2.erode(thresholded, thresholded,rectErosione)
		cv2.erode(thresholded, thresholded,rectErosione)
		
		cv2.dilate(thresholded, thresholded, rectDilataz)
		cv2.dilate(thresholded, thresholded, rectDilataz)
		cv2.dilate(thresholded, thresholded, rectDilataz)
	
	#applico Hough
	circles = cv2.HoughCircles(thresholded, cv2.cv.CV_HOUGH_GRADIENT, dp=2, minDist=120, param1=100, param2=40, minRadius=10, maxRadius=60)
	
	#ATTENZIONE circles e una matrice 1xnx3
	#print circles
	found=False
	if circles is not None:
		maxRadius=0
		x=0
		y=0
		
		for i in range(circles.size/3):
			circle=circles[0,i]
			if circle[2]>maxRadius:
				found=True
				radius=int(circle[2])
				maxRadius=int(radius)
				x=int(circle[0])
				y=int(circle[1])
			
			
	if found:
		#cv2.circle(cameraFeed, (c[0],c[1]), c[2], (0,255,0),2)
		cv2.circle(cameraFeed, (x,y), maxRadius, (0,255,0),2)
		#salvo le coordinate trovate in un file
		out_file = open("coordinate.txt","w")
		out_file.write(str(x)+";"+str(y))
		out_file.close()	
	else:
		out_file = open("coordinate.txt","w")
		out_file.write("0;0")
		out_file.close()		
		
	
	#visualizzo le immagini 
	cv2.imshow(mainGui,cameraFeed)
	#cv2.imshow(hsvWindow, hsvFrame)
	cv2.imshow(thresholdWindow,thresholded)
	
	if cv2.waitKey(33)==27:
		break



