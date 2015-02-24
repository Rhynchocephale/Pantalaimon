import os
import subprocess
import shutil
import hashlib
import time
from datetime import datetime as dt

imageExtension = ('.jpg','.JPG','.jpeg','.JPEG','.bmp','.BMP','.png','.PNG','.gif','.GIF','.tiff','.TIFF') #list of extensions we recognise as images

def minuslen(thing):
    return -len(thing[0])

def now():
    return "# "+str(dt.now())+" "

def md5(filename):
    with open(filename,'rb') as file_to_check:
        # read contents of the file
        data = file_to_check.read()    
        # pipe contents of the file through
        myMd5 = hashlib.md5(data).hexdigest()
    return myMd5

#parse a config file line to only keep the relevant information
def configLine(myString):
    return myString.split(":")[-1].replace(" ","").replace("\n","")

#checks if a string can be parsed as a positive int
def is_int(s):
    try:
        a = int(s)
        if (a >= 0):
            return True
        else:
            return False
    except ValueError:
        return False

def copyPictures(picturePath,daemonPath,deleteFromInput,doRename,logFile):

    anythingNew = 0 #has any picture been copied?

    getCreation = ("exiftool","-s","-createDate")
    getModif = ("exiftool","-s","-fileModifyDate")

    listOfPics = []
    if os.path.exists(picturePath):        
        for folder in os.walk(picturePath): #lists the directories, subdirs, subsubdirs, etc. in folder
            for f in os.listdir(folder[0]): #for each file in the current subdirectory
                if f.endswith(imageExtension): #if it is an image
                    foldername = folder[0]
                    if not foldername.endswith("/"): #make sure the absolute path to the folder ends with one, and only one, slash
                        foldername += "/"
                    listOfPics.append(foldername+f) #adds the absolute path to the picture in the list of pictures
    
    toCopy = len(listOfPics)
    if toCopy > 1:
        logFile.write(now()+" "+str(toCopy)+" images to copy\n")
    else:
        logFile.write(now()+" "+str(toCopy)+" image to copy\n")

    if listOfPics!=[]: #if there are pictures to sort
                
        #checks if output folder exists, if not, create it
        if not os.path.exists(daemonPath):
            os.makedirs(daemonPath)
            logFile.write(now()+"No output folder detected. Created it.\n")

        #i=1
        numberOfPics = len(listOfPics)
        for f in listOfPics:
            #print(str(i)+"/"+str(numberOfPics)) #displays advancement of the copy
            #i+=1
            process = subprocess.Popen(getCreation+(f,), stdout=subprocess.PIPE) #gets image creation date
            output = process.communicate()[0]
            if(not output): #if no image creation date present in metadata
                process = subprocess.Popen(getModif+(f,), stdout=subprocess.PIPE) #check file creation date instead
                output = process.communicate()[0]
                #WRITE IN LOG
            #splitting the datetime into smaller parts. Deals with formats day:month:year and day/month/year
            dateTaken = output.split()[2].replace("/",":").split(":")
            hourTaken = output.split()[3].replace("/",":").split(":")
                        
            yearTaken = dateTaken[0]+"/"
            monthTaken = dateTaken[1]+"/"
            
            #creating subfolders into the input folder
            if not os.path.exists(daemonPath+yearTaken):
                os.makedirs(daemonPath+yearTaken)
                    
            if not os.path.exists(daemonPath+yearTaken+monthTaken):
                os.makedirs(daemonPath+yearTaken+monthTaken)
                        
            #creating the path to where the image will be copied. Without extension, for now.
            if(doRename):
                #format of newName: year-month_hour:minute
                newName = daemonPath+yearTaken+monthTaken+dateTaken[2]+"-"+dateTaken[1]+"_"+hourTaken[0]+":"+hourTaken[1]
            else:
                newName = daemonPath+yearTaken+monthTaken+f.split("/")[-1].split(".")[-2]
                        
            imageToCopy = True #will the image be copied?
            #if there is already an image with the same name, try adding a number between parenthesis after the name, until finding a non-taken name
            if os.path.exists(newName+"."+f.split(".")[-1]):
                current_md5 = md5(f)
                if(md5(newName+"."+f.split(".")[-1]) == current_md5): #if image already present, do not copy it again
                    imageToCopy = False
                else:
                    j = 1;
                    while os.path.exists(newName+" ("+str(j)+")."+f.split(".")[-1]):
                        if(md5(newName+" ("+str(j)+")."+f.split(".")[-1]) == current_md5): #if image already present, do not copy it again
                            imageToCopy = False
                            break
                        j+=1
                    newName = newName+" ("+str(j)+")"
            newName = newName+"."+f.split(".")[-1] #adding the extension
                    
            if(imageToCopy):
                original_md5 = md5(f)
                shutil.copyfile(f,newName)
                md5_returned = md5(newName)

                # Finally compare original MD5 with freshly calculated, and remove copied file if error
                if original_md5 != md5_returned:
                    #WRITE IN LOG
                    logFile.write(now()+f+" ERROR WHILE COPYING\n")
                    os.remove(newName)
                else:
                    #an image has been copied
                    logFile.write(now()+f+" copied\n")
                    anythingNew += 1
                            
                if deleteFromInput: #remove original file if needed
                    os.remove(f)
                    
            elif deleteFromInput: #if image already existing, and should not have been
                logFile.write(now()+f+" ALREADY EXISTING. DID NOT COPY.\n")
                
        #remove the now supposedly empty (unless a copy has failed) subdirectories
        if(deleteFromInput):
            for folder in sorted(os.walk(picturePath),key=minuslen): #list of all the paths, sorted by length (longest first, since they are the deepest in the structure)
                if ((not os.listdir(folder[0])) or (all([filename.startswith(".") for filename in os.listdir(folder[0])]))): #checks that folder is empty, or at least only contains hidden files
                    os.system("rm -rf "+folder[0])
            
        if not os.path.exists(picturePath):
            os.makedirs(picturePath)
                    
        if anythingNew:
            if anythingNew > 1: #checks for plural
                logFile.write(now()+"Copied "+str(anythingNew)+" images.\n")
            else:
                logFile.write(now()+"Copied "+str(anythingNew)+" image.\n")
            
    return anythingNew

def createGallery(daemonPath, imgWidth, logFile):
                                       
    galleryPath = daemonPath+"gallery/"
    timeToRefresh = 30 #number of seconds between each automatic refresh of the page

    if os.path.exists(daemonPath): #if output folder exists
                    
        #-----Writing the menu
        myMenu = '\t\t<ul class="nav">\n' 
        listOfYears = sorted(os.listdir(daemonPath)) #lists folders in output folder, alphabetically sorted
        if "gallery" in listOfYears: #the gallery folder will be created in the output folder. If it has been created previously, do not take it into account.
            listOfYears.remove("gallery")
        for year in listOfYears:
            myMenu += '\t\t\t<li class="nav-item">\n\t\t\t\t<a href="#">'+year+'</a>\n\t\t\t\t<ul class="nav sub-nav">\n' #first level of the menu
            for month in sorted(os.listdir(daemonPath+year)): #lists months folders in the current year folder
                #adding the months in the submenu, with links to their html page
                myMenu += '\t\t\t\t\t<li class="sub-nav-item"><a href="'+galleryPath+year+'/'+month+'.html">'+month+'</a></li>\n'
            myMenu += '\t\t\t\t</ul>\n\t\t\t</li>\n'
        myMenu+='\t\t</ul>\n\t\t<br><br>\n'
        #-----End of menu
                    
        #will be present respectively at the top & bottom of each generated html file
        header = '<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<meta charset="utf-8"/>\n\t\t<meta http-equiv="refresh" content="'+str(timeToRefresh)+'">\n\t\t<title>%s</title>\n\t\t<link rel="stylesheet" type="text/css" href="/tmp/Pantalaimon/style.css">\n\t</head>\n\t<body>\n'
        footer = '\n\t<body>\n</html>'

        #totally remove gallery folder prior to recreating it.
        if os.path.exists(galleryPath):
            os.system("rm -rf "+galleryPath)
        os.makedirs(galleryPath)
                        
        #We will now create all the html files, one per month, stored in the gallery directory, in folders named after their year
        for year in listOfYears: #for each year
            os.makedirs(galleryPath+year) #creates the folder
            for month in os.listdir(daemonPath+year): #for each month                                
                monthFile = open(galleryPath+year+'/'+month+".html","w")
                monthFile.write(header.replace('%s',str(month)+'-'+str(year))) #writes the header, and changes the title of the html page: month-year
                monthFile.write(myMenu)
                #list of all absolute paths of pics in the folder
                listOfPics = ["file://"+daemonPath+str(year)+'/'+str(month)+'/'+pic for pic in os.listdir(daemonPath+year+'/'+month) if pic.endswith(imageExtension)]
                for pic in sorted(listOfPics):
                     #date, format "dd-mm hh-mm". The [:11] is there to get rid of the number between parenthesis that are there to differenciate between pics taken at the exact same minute
                    dateTaken = pic.split("/")[-1].split(".")[-2].replace("_"," ")[:11]
                    #adding each pic to the html, with a link to the file, and displaying the date it was taken when hovering
                    picHtml = '\t\t<div class="img"><a target="_blank" href="'+pic+'"><img src="'+pic+'" title="'+dateTaken+'"%s"></a></div>\n'
                    if imgWidth: #adding the width, if width!=0. Else, leave original.
                        picHtml = picHtml.replace("%s",' width="'+str(imgWidth))
                    else:
                        picHtml = picHtml.replace("%s","")
                    monthFile.write(picHtml)
        
                monthFile.write(footer)
                monthFile.close()
                logFile.write(now()+"gallery for "+month+"-"+year+" created.\n")
                    
        #writes the root gallery html file, that will just contain the menu
        galleryFile = open(galleryPath+"gallery.html","w+")
        galleryFile.write(header.replace('%s','My Gallery'))
        galleryFile.write(myMenu)
        galleryFile.write(footer)
        galleryFile.close()
        logFile.write(now()+"gallery created.\n")
        
        return True

def launchEverything(logFile):
    listOfYes = ("y","Y","yes","YES")
    configFile = open("/tmp/Pantalaimon/config","r")
    config = configFile.readlines()
    
    picturePath = configLine(config[0]) #input folder
    daemonPath = configLine(config[1]) #output folder
    deleteFromInput = True if (configLine(config[2]) in listOfYes) else False #delete images from input folder?
    doRename = True if (configLine(config[3]) in listOfYes) else False #rename pictures when copying them?
    
    if not picturePath.endswith("/"): #make sure the absolute path to the folder ends with one, and only one, slash
        picturePath += "/"
    if not daemonPath.endswith("/"): #make sure the absolute path to the folder ends with one, and only one, slash
        daemonPath += "/"
    logFile = open(logFile,"a+")
    logFile.write(now()+" Launching\n")
    #try to copy pictures. Return true if any picture has been copied.
    anythingNew = copyPictures(picturePath,daemonPath,deleteFromInput,doRename,logFile)
    if anythingNew:
        imgWidth = configLine(config[4])
        if not is_int(imgWidth): #if what is in the config file is not a positive int, reset to a set value
            imgWidth = 300
                
        #creates the html gallery inside the output folder
        createGallery(daemonPath,imgWidth,logFile)
    logFile.close()
    return True
