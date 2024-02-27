import PySimpleGUI as sg
import random

def printField(field:list) -> bool:
    ySize = len(field)
    if ySize >= 3 or type(field[0])==type(list()):
        xSize = len(field[0])
        i = 0
        while i < ySize:
            j = 0
            while j < xSize:
                if field[i][j]>=0:
                    print(" ", end = "")
                print(str(int(field[i][j])), end = " ")
                j += 1
            print("\n")
            i += 1
        return True
    else:
        print("Bad table")
        return False

def generateField(cols: int=10, rows: int=4, mines: int=10, xClick:int = 0, yClick:int = 0):
    if (cols>=3) and (rows>=3) and (float(mines/(rows*cols))<0.75 and (mines+9<=rows*cols)) :   #if size and amount of mines valid
        field = [[False for i in range(cols)] for j in range(rows)]             #assign grid of False bools, for mine locations
        if xClick < 2:                                                      #if first click at any edge, move away from edge
            xClick = 2
        elif xClick >= cols:
            xClick = cols-1
        if yClick < 2:
            yClick = 2
        elif yClick >= rows:
            yClick = rows-1
        
        y = yClick-1                                                        #add temp mines around click, so planting step avoids tiles later
        while y <= yClick+1:
            x = xClick-1
            while x<= xClick+1:
                field[y-1][x-1] = True
                x+=1
            y+=1
        
        planted = 0
        while planted < mines:                                              #keep planting until counter reaches
            x, y = (random.randint(0,cols-1), random.randint(0,rows-1)) #attempt random
            if field[y][x] == False:    #if ground was clear,
                field[y][x] = True      #do plant,
                planted += 1            #and increment counter
        y = yClick-1
        
        while y <= yClick+1:                                                #remove temp mines
            x = xClick-1
            while x<= xClick+1:
                field[y-1][x-1] = False
                x+=1
            y+=1
        
        proximities = [[0 for i in range(cols)] for j in range(rows)]
        for ex in range(cols):
            for why in range(rows):
                proximities[why][ex] += mineCount(ex, why, field)
                if field[why][ex]:
                    proximities[why][ex] = proximities[why][ex] * (-1)
        
    else:                                                                                       #if invalid field
        print("error: size<(3*3) or mines>75% or non-mines<9")
        proximities = list([False])                                                                   #return empty
        pristinefield = list([False])
    
    pristinefield = [[0 for i in range(cols)] for j in range(rows)]     #directly output as dugfield, to track digging and marked mines
    
    return proximities, pristinefield

def mineCount(ex, why, booleanOrDugField) -> int:           #on being provided dugfield, counts Marks
    count = 0
    y = why-1
    while y <= why+1:
        x = ex-1
        while x <= ex+1:
            try:
                if y>=0 and x>=0 and int(booleanOrDugField[y][x])==1:   #counts Trues for booleans, or specifically 1s, for dugfield
                    count += 1
            except IndexError:
                pass #it's ok
            x+=1
        y+=1
    return count

#        (x, y, dig/mark, dugfield, minefield, window, event): click function targets specific square, and either marks it, or reads it and reveals it. In both cases, this function also provides the user feedback
def click(ex, why, mode, dugs, mines, windows, events):
    if 0<=why<=len(mines)-1:        #sanitize, to prevent window[event] reaching outside the intended area when used in pySolver, with manual input events
        if 0<=ex<=len(mines[0])-1:  #TODO: move checks to pySolver
            if mode:                                            #if (intent to dig)
                if dugs[why][ex] == 0:                               #if neither dug(2) nor marked(1)                                   #-----------
                    dugs[why][ex] = 2                                    # set spot to dug(2), and                                      #
                    if (mines[why][ex]<0):                               # display result                                               #
                        windows[events].update('L', button_color=('white','red'))                                                       #
                        windows['-MESSAGE-'].update('Boom :(')                                                                          #
                    else:                                                                                                               #    Dig
                        windows[events].update(mines[why][ex], button_color=('white','black'))                                          #
                        windows['-MESSAGE-'].update('Clear!')                                                                           #
                elif dugs[why][ex] == 1:                             #else if marked(1), prevent and inform                             #
                    windows['-MESSAGE-'].update('No Danger Allowed')                                                                    #
                else:                                                       #else, dug(2) spot was just clicked, only notify            #
                    windows['-MESSAGE-'].update('No Backtracking Allowed')                                                              #-----------
            else:                                                       #else (intent to mark)
                if dugs[why][ex] != 2:                                #if not dug(2)                                                    #-----------
                    dugs[why][ex] = int(not bool(dugs[why][ex]))  #toggle (1)<->(0) (method for fun)                                    #
                    if dugs[why][ex]:                                    # if finally marked(1),                                        #
                        windows[events].update('🚩', button_color=('red', '#788bab'))  #display mark                                    #
                        windows['-MESSAGE-'].update('Smart.')                                                                           #
                    else:                                                                                                               #    Mark
                        windows[events].update('', button_color=('black', '#283b5b'))  #display mark                                    #
                        windows['-MESSAGE-'].update('Wise.')                                                                            #
                else:                                                                                                                   #
                    windows['-MESSAGE-'].update('Funny.')                                                                               #-----------
    return dugs, mines


def pySolver(dugs, mines, windows, events):
    if mines[0] == False:                   #wash our hands first
        print("Can't solve a Bad Table")
        return
    
    boolField = [[False for i in range(len(mines[0]))] for j in range(len(mines))]
    for y in range(len(mines)):
        for x in range(len(mines[0])):
            boolField[y][x] = bool(mines[y][x] < 0)             #legibility bool()
    
    somethingClicked = True
    while somethingClicked:                 #go on as long as stuff is done
        somethingClicked = False
        for y in range(len(mines)):
            for x in range(len(mines[0])):
                if dugs[y][x] == 2:
                    minesNotFound = int(mines[y][x] - mineCount(x, y, dugs))    #mineCount dugfield counts Marks around the x y spot (instances of dugfield[y][x]==1)
                    print(minesNotFound)
                    if minesNotFound == 0:
                        for yClick in range(y-1, y+2):
                            for xClick in range(x-1, x+2):
                                try:
                                    print("Try at " + str(xClick) + ", " + str(yClick) + ", with event: ")
                                    dugs, mines = click(xClick, yClick, True, dugs, mines, windows, (yClick,xClick))
                                except IndexError:
                                    print("IndexError handled at " + string(xClick) + ", " + string(yClick))    #it's ok
            #   if minesLeft[y][x] == 0:
#           #       dig(all surrounding)
#           #       somethingClicked = true
#        #def rule 1():
#            #set modeIntent to Mark
#            #for (all dug spaces):
#            #   minesLeft[y][x] = minefield[y][x] - minesConfirmedSurrounding[y][x]
###            #   if minesLeft[y][x] == undugSurroundingSpaces[y][x]
#            #       mark(all surrounding)
#            #       somethingClicked = true
#    
    return dugs, mines


def pySweeper(MAX_COLS:int = 10, MAX_ROWS:int = 10, MINES:int = 10) -> (bool, int, int, int):
    generatedYet = False    #flipped once, on successful minefield generation
    Regenerate = False      #returned as output, tracking intent to rerun pySweeper(true), instead of exiting everything(false)
    interactMode = False    #tracks marking known mine locations(false) vs digging up a square(true)
    
    sg.theme('Dark Blue 3') #default button color tuple: ('#FFFFFF', '#283b5b')
    #layout is a list[list[]] type.
    # each [list] is a row
    # each sg.element(), seperated by commas, placed left to right in row
    layout = [[sg.Text('Mineing', font='Default 25')], [sg.Text(auto_size_text=True, key='-MESSAGE-', font='Default 20', text='<>')]]
    #Customization input line
    layout += [[
    sg.Text('Columns(>2): ', font='Default 10'), sg.InputText(default_text=MAX_COLS, key='-COLUMNS-', size=(3,1)),
    sg.Text('Rows(>2): ', font='Default 10'), sg.Input(default_text=MAX_ROWS, key='-ROWS-', size=(3,1)),
    sg.Text('Mines(<75%):', font='Default 10'), sg.Input(default_text=MINES, key='-MINES-', size=(4,1))
    ]]
    layout += [[sg.Button('Toggle Mode', button_color=('black', 'White')), sg.Text(size=(12,1), key='-MODE-', font='Default 20', text='🚩💣?')]]
    #Add the board, a grid of empty buttons
    layout += [[sg.Button(str(''), size=(4, 2), pad=(0,1), border_width=1, key=(row,col)) for col in range(MAX_COLS)] for row in range(MAX_ROWS)]
    #last row of control buttons
    layout += [[
    sg.Button('Solver Step', button_color=('black', 'green')), 
    sg.Button('Reset', button_color=('black', 'white')), 
    sg.Button('Exit', button_color=('white', 'red'))
    ]]
    
    window = sg.Window('Minesweeper', layout)
    while True:         # The Event Loop
        event, values = window.read()
        print(event, values)
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        if event == 'Reset':
            Regenerate = True   #set intent to rerun pySweeper after exit, and then
            break               #exit
        if event == 'Solver Step':
            if generatedYet:
                dugfield, minefield = pySolver(dugfield, minefield, window, event)                            #run solver once
                window['-MESSAGE-'].update('Solved')
            else:
                window['-MESSAGE-'].update('No table...')
            continue
        if event == 'Toggle Mode':
            if generatedYet:
                interactMode = not interactMode     #toggle
                if interactMode:
                    window['-MODE-'].update('💣')    #to dig     (notice how emoji ruins indentation alignment in npp)
                else:
                    window['-MODE-'].update('🚩')    #to mark
            else:
                interactMode = not interactMode     #toggle
                if interactMode:
                    window['-MODE-'].update('💣: Dig')    #visual fluff     (notice how emoji ruins indentation alignment in npp)
                else:
                    window['-MODE-'].update('🚩: Mark')
            continue
        
        
        #if loop reaches past this point, there's been a click on a tile
        yDig, xDig = event
        if not generatedYet:
            if not interactMode:                #if mode in default(mark), therefore probably unchanged. Tutorial setup
                window['-MESSAGE-'].update('Toggle Mode to start digging!')
                window['-MODE-'].update('🚩: Mark')
                continue    #tutorial failed
            else:
                minefield, dugfield = generateField(int(values['-COLUMNS-']), int(values['-ROWS-']), int(values['-MINES-']), xDig+1, yDig+1)
                if printField(minefield) == False:  #validity check is in print function
                    window['-MESSAGE-'].update('Bad table >:(')
                    continue                        #if invalid, do not set generatedYet flag, do not update boxes
                generatedYet = True
            
        
        print(window[event].ButtonColor)
        #perform click
        dugfield, minefield = click(xDig, yDig, interactMode, dugfield, minefield, window, event)
        #^ this? I take no questions at this time (readability)
    
    window.close()
    return Regenerate, int(values['-COLUMNS-']), int(values['-ROWS-']), int(values['-MINES-'])

cols, rows = (10,8)
mines = 20

minefield = list()      #establish scope
dugfield = list()

regenerate = True
while regenerate:
    regenerate = False
    regenerate, cols, rows, mines = pySweeper(cols, rows, mines)
