from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image  
from win32api import GetSystemMetrics
import os
import re

# proportion of screen
propSelect = 0.25
propFull = 0.75
propImgX = 0.9
propImgY = 0.8

# initial sizing
xSize = int(GetSystemMetrics(0))
ySize = int(GetSystemMetrics(1))

# calculate thumbnail sizes
thumbX = xSize * propFull * propImgX 
thumbY = ySize * propFull * propImgY

# types of pictures accepted
picTypes = "jpg|png|gif|jfif"



def initiateTk(xProp, yProp):
    master = Tk()

    # initial sizing
    master.geometry('{}x{}'.format(int(xSize * xProp), int(ySize * yProp)))

    # label window
    master.title("Picture Labeller")

    return master


# opens file explorer, can pick a directory
def browseFiles(master):
    global folderName
    folderName = filedialog.askdirectory(initialdir="/", title="Select a File")
    master.destroy()


# finds all the pictures in the folder
def findPictures(folderName):
    pList = []

    # puts only accepted types onto the list
    for f in os.listdir(folderName):
        if re.match("[^/]*\.(" + picTypes + ")$", f):
            pList.append(f)

    return pList

def updatePic(pic):
    img = Image.open(pic)
    img.thumbnail((thumbX, thumbY), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)

    return img

# triggered event by enter
def callbackEnter(event, eEnterName):
    # get entered new name and rename file
    newName = eEnterName.get()
    fileType = os.path.splitext(picName)[1]
    os.rename(folderName + "/" + picName, folderName + "/" + newName + fileType)

    # clear entry box
    eEnterName.delete(0, END)

    # switch picture being displayed
    nextPic()


# triggered event by up arrow
def callbackOld(event, eEnterName):
    eEnterName.delete(0, END)
    # insert old name wihtout the filetype
    eEnterName.insert(0, os.path.splitext(picName)[0])

def protocolExit(master):
    master.destroy()
    quit()

def protocolLoopExit(master):
    global exit
    exit = True
    waitVar.set(1)

# set trigger to loop to next picture
def nextPic():
    waitVar.set(1)

def main():
    # initiate wait var for the gui
    global waitVar
    # exit flag in order to leave wait variable loop
    global exit
    exit = False
    # initate name of pic currently on
    global picName
    # name of selected folder
    global folderName

    # initiate the folder selection gui
    masterFolder = initiateTk(propSelect, propSelect)

    # create contents
    label = Label(text="Pick a folder from which to label pictures")
    button = Button(masterFolder, text="Browse Files", command=lambda: browseFiles(masterFolder))
    label.pack()
    button.pack()

    # able to exit gracefully
    masterFolder.protocol("WM_DELETE_WINDOW", lambda: protocolExit(masterFolder))

    # get file name from pop up, should not be closed until something is selected
    mainloop()

    # extract all relevant picture names
    picList = findPictures(folderName)

    # put up labelling gui
    masterLabel = initiateTk(propFull, propFull)

    waitVar = IntVar()
    picName = picList[0]


    # put up first picture
    img = Image.open(folderName + "/" + picList[0])
    img.thumbnail(((xSize * propFull * propImgX), (ySize * propFull * propImgY)), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    lPic = Label(image=img)
    lPic.pack()


    # show old name as reference
    lOldName = Label(masterLabel, text=picList[0])
    lOldName.pack()

    eEnterName = Entry(masterLabel, width=75, font=("Calibri 14"))
    eEnterName.focus_set()
    eEnterName.pack()

    bSkip = Button(masterLabel, text="Skip", command=nextPic)
    bSkip.pack()

    # bind events in gui
    masterLabel.bind('<Return>', lambda event: callbackEnter(event, eEnterName))
    masterLabel.bind('<Up>', lambda event: callbackOld(event, eEnterName))
    masterLabel.protocol("WM_DELETE_WINDOW", lambda: protocolLoopExit(masterLabel))
    
    # go through the rest of the pictures
    for p in picList[1:]:
        bSkip.wait_variable(waitVar)

        # if exit flag triggered last loop, leave
        if exit:
            break
        picName = p # needs to be after the wait

        # update old label
        lOldName["text"] = picName

        # update image
        newImg = updatePic(folderName + "/" + p)
        lPic.configure(image=newImg)

    # when out of pictures close application
    if not exit:
        bSkip.wait_variable(waitVar)
    masterLabel.destroy()

    # run program
    try:
        mainloop()
    except AttributeError as e:
        print("Gracefully ended early")


if __name__ == '__main__':
    main()

