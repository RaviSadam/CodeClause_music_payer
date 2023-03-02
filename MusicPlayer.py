import random
import sys,wave, numpy, pygame,os
from pygame.locals import *
from scipy.fftpack import dct
import tkinter
from tkinter import font as tkFont
from tkinter import filedialog,messagebox
from pydub import AudioSegment


Number = 20 # number of bars
HEIGHT = 250 # HEIGHT of a bar
WIDTH = 20 #WIDTH of a bar
FPS = 10
PRE=0
volume=0.59 #Volume
pointer=0 #playlist pointer for shifting the forward or backward
firstOrSecond=True #for accessing the first or seconf temperary wave files
SONG_END_EVENT =None #User defiend Event (Ending the audio file)


curr_song="" #currently running file
file_path="" #file path chossing at the star

nframes=0 #number of frames in audio
num = nframes
wave_data=[] #wave data 
framerate=0
status="" #status of song playing stopped paused 
screen=None #pygame screen(window)
fpsclock=""
playlist=[] #playlist

bars=[]
colors=[[0,255,0],[139,0,0],[220,20,60],[255,0,0],[255,160,122],[184,134,11],[0,128,0],[0,255,255],[0,191,255],[138,43,126],[139,0,139],[255,0,255],[210,105,30]]
buttons = [ ### song controller buttons pause play previous next
    {"state": False, "old_image": pygame.image.load("Images/left.png"), "new_image": pygame.image.load("Images/left.png"), "rect": pygame.Rect(10, 360, 55, 55),"key": pygame.K_a},
    {"state": False, "old_image": pygame.image.load("Images/pause.png"), "new_image": pygame.image.load("Images/play.jpg"), "rect": pygame.Rect(80, 360, 55, 55),"key":pygame.K_b},
    {"state": False, "old_image": pygame.image.load("Images/right.png"), "new_image": pygame.image.load("Images/right.png"), "rect": pygame.Rect(150, 360, 55, 55),"key":pygame.K_c},
    {"state": False, "old_image": pygame.image.load("Images/Volume.png"), "new_image": pygame.image.load("Images/Volume.png"), "rect": pygame.Rect(220, 360, 55, 55),"key":pygame.K_d},
]







def Visualizer(nums): # for making the bar positions and heigth and width of each bar
    global wave_data,framerate,nframes
    num = int(nums)
    h = abs(dct(wave_data[0][nframes - num:nframes - num + Number]))
    h = [min(HEIGHT, int(i**(1 / 2.5) * HEIGHT / 100)) for i in h]
    draw_bars(h)

def vis(status): #satatus of songs and srawing the bars 
    global num,nframes
    if status == "stopped":
        num = nframes
        return
    elif status == "paused":
        pygame.mixer.music.pause()
    else:
        num -= framerate / FPS
        if num > 0:
            Visualizer(num)

def get_time(): #getting the time of song
    seconds = max(0, pygame.mixer.music.get_pos() / 1000)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    hms = ("%02d:%02d:%02d" % (h, m, s))
    return hms

def draw_bars(h): #drawing the dars  on screen
    bars = []
    for i in h:
        bars.append([len(bars) * WIDTH , 10 + HEIGHT - i, WIDTH - 1, i])
    for i in bars:
        pygame.draw.rect(screen, random.choice(colors), i, 0)

def draw_button(screen, button): #song controller buttons adding to main screen
    image = button["new_image"] if button["state"] else button["old_image"]
    button_surface = pygame.Surface(button["rect"].size)
    button_surface.blit(pygame.transform.scale(image, (55,55)), (0, 0))
    screen.blit(button_surface, button["rect"])



def Event(): #total events buttons,mouse,end of audion file events
    global num,volume,buttons,status,screen,pointer,SONG_END_EVENT
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.quit()
                sys.exit()
            elif event.type == SONG_END_EVENT: #end of file events and moving to next song
                pointer+=1
                Song()


            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        button["state"] = not button["state"]
                        #
                        #For handling the event of play and pause
                        #
                        if(button["key"]==pygame.K_b):
                            if(button["state"]):
                                PRE=num
                                status="paused"
                                num=1
                            else:
                                pygame.mixer.music.unpause()
                                num=PRE
                                status="playing"

                        #
                        #For handling the Volume Event
                        #
                        elif(button["key"]==pygame.K_d):
                            volume=(pygame.mixer.music.get_volume()+0.1)%1
                            pygame.mixer.music.set_volume(volume)
                        #
                        #Song forwarding
                        #

                        elif(button['key']==pygame.K_c):
                            pointer+=1
                            Song()
                        #
                        #Prevoius
                        #
                        elif(button['key']==pygame.K_b):
                            pointer-=1
                            Song()
                        #
                        #if song ended the moving forward
                        #
                        
        if num <= 0:
            status = "stopped"

        #updating the display screen with updated values/current values


        name = my_font.render("Current Song :"+curr_song, True, (0,0,0)) #name current running song
        info = my_font.render(status.upper() + " :" + get_time(), True, (0,0,0)) #playing time
        vol=my_font.render("Volume :"+str(round(volume*100)),True,(0,0,0,0)) #volume of song
        screen.fill((255,255,255))
        screen.blit(name,(20,270))
        screen.blit(info,(20,300))
        screen.blit(vol,(20,330))
        fpsclock.tick(FPS)
        for button in buttons:
            draw_button(screen, button)
        vis(status)
        pygame.display.update() #updaing the screen



#for getting the frames in wave file 

def gettingWave(filename):
    global nframes,framerate,wave_data,num,status
    status = "Playing"
    f=wave.open(filename) #opening the wave file  
    params = f.getparams() #getting the frames from wave
    nchannels, sampwidth, framerate, nframes = params[:4]
    str_data = f.readframes(nframes)
    f.close()
    wave_data = numpy.fromstring(str_data, dtype = numpy.short)
    wave_data.shape = -1, 2
    wave_data = wave_data.T
    num=nframes
    

#wave.open accets only .wav files so for the conversion of mp3 to wav 

def mp3ToWav(file_path,curr_song,firstOrSecond):
    sound = AudioSegment.from_mp3(file_path+"/"+curr_song)
    if(not firstOrSecond): 
        filename=file_path+"/result.wav"
    else:
        filename=file_path+"/result1.wav"
    sound.export(filename, format="wav")


#loading the Song

def Song():
    global file_path,curr_song,firstOrSecond
    curr_song=playlist[abs(pointer)%len(playlist)] # geeting current audio file 
    mp3ToWav(file_path,curr_song,firstOrSecond) #.mp3 to .wav converter
    if(not firstOrSecond): #taking the free file
        filename=file_path+"/result.wav"
    else:
        filename=file_path+"/result1.wav"
    firstOrSecond=not firstOrSecond
    pygame.mixer.music.load(filename) #loading the audio file
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(SONG_END_EVENT)
    pygame.mixer.music.set_volume(0.6)
    gettingWave(filename)  #wave giver


#For pygame screen called only once

def pygameScreen():
    global screen,my_font,fpsclock,file_path,SONG_END_EVENT
    status = 'stopped'
    pygame.init()
    pygame.mixer.init()
    my_font = pygame.font.SysFont('consolas', 16)
    fpsclock = pygame.time.Clock()
    screen = pygame.display.set_mode([300, 450])
    pygame.display.set_caption('Music Player')
    SONG_END_EVENT = pygame.USEREVENT + 1
    f = open(file_path+"/"+'result.wav', 'w') #creating the two temp .wav files for conversion purpose mp3->.wav
    f1=open(file_path+"/result1.wav",'w') #two files we need because when user moved to next or previous songs windows does not allow to accecss the currently using file so if one file is running then we accessing the another file
    f1.close()
    f.close()
    Song()
    Event()


#it is dialog box for selecting the songs folder

def selectDirectiry():
    global playlist,file_path
    folder_path =filedialog.askdirectory()
    file_path=folder_path         #path of folder
    b=False
    file_list=os.listdir(folder_path)
    for i in file_list:             ###getting the all .mp3 files from selected folder
        if(i[-4:]==".mp3"):
            b=True
            playlist.append(i)
    if(b):
        top.destroy()
        pygameScreen() #making the pygame screen
    else:
        messagebox.showwarning("Warning","No Songs in folder")


#starting window 

top = tkinter.Tk(className="Directiry Chooser")
top.geometry("400x300")
top.config(bg="#e43fa3")
helv36 = tkFont.Font(family='Helvetica', size=15, weight='bold')
button = tkinter.Button(top, text ="Please select the Directiry of songs", font=helv36,command = selectDirectiry,foreground="green")
button.place(x=30,y=120)

top.mainloop()
    

