"""
Yosuke and Josh
Project 1
2/12/17
"""

# black/white threshold
# subtract orig_image from each frame to get rid of boundary
# get rid of noise
# tracking


import numpy as np
import cv2
import cvk2
import sys

WHITE = (255,255,255)

def open(video):
    '''Opens the video and returns a VideoCapture object'''
    cap = cv2.VideoCapture(video)
    return cap

def initial_frames(cap):
    '''Reads the next frame in the video and returns a numpy array of the frame'''
    ret,frame = cap.read()
    return frame

def find_background(iterations, cap):
    '''Find the background image of the video by taking the average intensity
        of each pixel over iterations number of frames'''
    ret,original = cap.read()
    background = np.zeros((750,750,3), np.uint32)
    for i in range(iterations):
        ret,frame = cap.read()
        background += frame
    return np.true_divide(background,iterations)


def background_subtraction(frame, background,thresh):
    '''Performs background subtraction and then does binary thresholding on the result'''
    subtracted = cv2.absdiff(frame, background)
    ret, disp = cv2.threshold(subtracted,50+thresh,255,cv2.THRESH_BINARY)
    return disp

def morphological(frame):
    '''Uses morphological operators to get rid of white speckles'''
    # based on experimentation, (1,1) is too small but (3,3) is too large
    kernel = np.ones((2,2),np.uint8)
    opening = cv2.morphologyEx(frame,cv2.MORPH_OPEN,kernel)
    return opening

def init_find_contours(frame):
    '''Connected component analysis. Finds the contours of connected components and
        returns a list of the centroids'''
    copy = frame.copy()
    graycopy = cv2.cvtColor(copy,cv2.COLOR_BGR2GRAY)
    im2, contours, hierarchy = cv2.findContours(graycopy,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    centroids = []
    for j in range(len(contours)):
        # Compute some statistics about this contour.
        info = cvk2.getcontourinfo(contours[j])
        
        # Mean location
        mu = (info['mean'])
        centroids.append(mu)

    return centroids

def region_of_interest(centroid, translation):
    '''The expected position of the fly is the previous centroid plus the previous translation vector.
        This function creates a circle around the expected position and returns it as an array of Booleans'''
    mask = np.zeros((750, 750), np.uint8)
    cv2.circle(mask, cvk2.array2cv_int(centroid + translation), 25, WHITE, -1, cv2.LINE_AA )
    bmask = mask.view(np.bool)
    return bmask

def flies_in_region_of_interest(centroids,bmask):
    '''Finds all flies in a given flies region of interest and returns it as a list'''
    centroids_in_circle = []
    for i in range(len(centroids)):
        if bmask[int(round(centroids[i][1]))][int(round(centroids[i][0]))] == True:
            centroids_in_circle.append(centroids[i])
    return centroids_in_circle

def distance(v1,v2):
    '''Computes the distance between two positions'''
    return (v1[0]-v2[0])**2 + (v1[1]-v2[1])**2

def pick_new_centroid(centroids_in_circle, circle_center):
    '''Finds and returns the closest centroid to a given position. The circle_center is the
        expected position of a fly given its previous centroid location and translation vector'''
    distances = []
    for ind,centroid in enumerate(centroids_in_circle):
        distances += [distance(centroid, circle_center)]

    ind = distances.index(min(distances))
    return centroids_in_circle[ind]


def main():
    
    # video = raw_input("Enter the video filename (flies1.avi or flies2.avi): ")
    if len(sys.argv) < 3:
        print('usage: {} <video filename> <normal or binary>'.format(sys.argv[0]))
        sys.exit(1)
    video = sys.argv[1]
    if sys.argv[2] == 'normal':
        showvideo = 'normal'
    elif sys.argv[2] == 'binary':
        showvideo = 'binary'
    else:
        print "Invalid video type. Choose normal or binary"
        sys.exit(1)


    help_strs = [
        'Keys:',
        '',
        '  Esc     quit',
        '  + or =  increase threshold value',
        '  -       decrease threshold value',
    ]
    
    print '\n'.join(help_strs)

    cap = open(video)
    cap.set(1,0)
    
    # run the video for 500 iterations to find the background
    background = find_background(500, cap)
    background = background.astype(np.uint8)
    
    # open the video again and play from beginning
    cap = open(video)
    cap.set(1,0)
    
    # set up initial thresholded frame and find flies
    first = initial_frames(cap)
    first_disp = background_subtraction(first, background,0)
    first_disp_clean = morphological(first_disp)
    centroids1 = init_find_contours(first_disp_clean)
    
    # initalize centroids dictionary
    centroids_dict = {}
    for fly_num,centroid in enumerate(centroids1):
        centroids_dict[fly_num] = centroid
    
    # initalize translation dictionary to all 0's
    translation_dict = {}
    for fly_num,centroid in enumerate(centroids1):
        translation_dict[fly_num] = (0,0)

    # cv2.imwrite('after_morphological2.png',first_disp_clean)

    thresh = 0
    morph = True

    while(cap.isOpened()):
        
        ret,frame = cap.read()
        
        k = cv2.waitKey(1)
        if k < 0:
            pass
        else:
            k = chr(k)
            if k == chr(27):
                break
            elif k == '+' or k == '=':
                if 50 + thresh < 250:
                    thresh += 5
                print('Threshold value is now {}'.format(50 + thresh))
            elif k == '-':
                if 50 + thresh > 5:
                    thresh -= 5
                print('Threshold value is now {}'.format(50 + thresh))

        
        
        disp = background_subtraction(frame, background,thresh)
        disp_clean = morphological(disp)
        centroids = init_find_contours(disp_clean)
        
        # if in this frame, more flies are detected
        if len(centroids) > len(centroids_dict):
            for fly_num in range(len(centroids_dict), len(centroids)):
                centroids_dict[fly_num] = centroids[fly_num]
                translation_dict[fly_num] = (0,0)
    
    
        centroids_used = np.empty((0,2),float)
        centroids_unused = centroids[:]
        centroids_dict_copy = centroids_dict.copy()
        for fly_num,centroid in centroids_dict_copy.iteritems():
            delete_entry = False

            bmask = region_of_interest(centroid,translation_dict[fly_num])
            centroids_in_circle = flies_in_region_of_interest(centroids, bmask)
            
            # if a centroid has already been assigned to a fly, remove it from centroids_in_circle
            c_in_circle_copy = centroids_in_circle
            for i in range(len(c_in_circle_copy)-1,-1,-1):
                if (c_in_circle_copy[i] in centroids_used):
                    del centroids_in_circle[i]
        
            # if centroids_in_circle is empty, pick an unused centroid
            if len(centroids_in_circle) == 0:
                if len(centroids_unused) != 0:
                    new_centroid = pick_new_centroid(centroids_unused, centroid + translation_dict[fly_num])
                
                else: # if there are no more unused centroids, delete the fly
                    del centroids_dict[fly_num]
                    del translation_dict[fly_num]
                    delete_entry = True
            
            # otherwise pick a new centroid from centroids_in_circle
            else:
                new_centroid = pick_new_centroid(centroids_in_circle, centroid + translation_dict[fly_num])
            
            if delete_entry: # don't update entries if it has been deleted
                continue
            
            # update dictionaries and used/unused lists
            translation_dict[fly_num] = new_centroid - centroids_dict[fly_num] # new - old centroid
            centroids_dict[fly_num] = new_centroid
            centroids_used = np.vstack([centroids_used,new_centroid])
            
            c_unused_copy = centroids_unused
            for i in range(len(c_unused_copy)-1,-1,-1):
                if (c_unused_copy[i] in centroids_used):
                    del centroids_unused[i]

            # display fly numbers
            cv2.putText(frame, str(fly_num),(int(new_centroid[0]),int(new_centroid[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE)

        for i in range(len(centroids)):
            cv2.circle(frame, cvk2.array2cv_int(centroids[i]), 7, WHITE, 1, cv2.LINE_AA )
    
        if showvideo == 'normal':
            cv2.imshow('frame',frame)
        elif showvideo == 'binary':
            cv2.imshow('frame', disp_clean)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

main()
