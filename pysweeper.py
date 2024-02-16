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

def generateField(cols: int=10, rows: int=8, mines: int=10, xClick:int = 0, yClick:int = 0):
    if (cols>=3) and (rows>=3) and (float(mines/(rows*cols))<0.75 and (mines+9<=rows*cols)) :   #if size and amount of mines valid
        field = [[False for i in range(cols)] for j in range(rows)]             #assign grid of False bools
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
    return proximities

def mineCount(ex, why, field) -> int:
    count = 0
    y = why-1
    while y <= why+1:
        x = ex-1
        while x <= ex+1:
            try:
                if y>=0 and x>=0 and field[y][x]:
                    count += 1
            except IndexError:
                pass #it's ok
            x+=1
        y+=1
    return count

def pySweeper(MAX_COLS:int = 10, MAX_ROWS:int = 10, MINES:int = 10) -> (bool, int, int, int):
    generatedYet = False
    Regenerate = False
    print("before window", generatedYet, Regenerate)
    sg.theme('Dark Blue 3')
    # Start building layout with the top 2 rows that contain Text elements
    layout = [[sg.Text('Mineing', font='Default 25')], [sg.Text(size=(12,1), key='-MESSAGE-', font='Default 20')]]
    # Customization input
    layout += [[sg.Text('Columns(>2): ', font='Default 10')],[sg.Input(default_text=MAX_COLS, key='-COLUMNS-')]]
    layout += [[sg.Text('Rows(>2): ', font='Default 10')],[sg.Input(default_text=MAX_ROWS, key='-ROWS-')]]
    layout += [[sg.Text('Mines("safe" and <75%): ', font='Default 10')],[sg.Input(default_text=MINES, key='-MINES-')]]
    layout += [[sg.Button('Reset', button_color=('black', 'white'))]]
    layout += [[sg.Button('Solver Step', button_color=('black', 'green'))]]
    # Add the board, a grid of buttons
    layout += [[sg.Button(str(''), size=(4, 2), pad=(0,0), border_width=1, key=(row,col)) for col in range(MAX_COLS)] for row in range(MAX_ROWS)]
    # Add the exit button as the last row
    layout += [[sg.Button('Exit', button_color=('white', 'red'))]]
    window = sg.Window('Minesweeper', layout)
    print("before loop")
    while True:         # The Event Loop
        print("loopstart")
        event, values = window.read()
        print("windowread")
        print(event, values)
        print("brexit")
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        print("breset")
        if event == 'Reset':
            Regenerate = True
            break
            print("befor")
        if event == 'Solver Step':
            print("slep")
            pySolver()                            #run solver once
            continue
        print("after continue")
        yDig, xDig = event
        print("notgend")
        if not generatedYet:
            minefield = generateField(int(values['-COLUMNS-']), int(values['-ROWS-']), int(values['-MINES-']), xDig+1, yDig+1)
            if printField(minefield) == False:  #validity check is in print function
                window['-MESSAGE-'].update('Bad table >:(')
                continue                        #if invalid, do not set generatedYet flag, do not update boxes
            generatedYet = True
        
        
        if (minefield[yDig][xDig]<0):           # simulate a hit or a miss
            window[event].update('L', button_color=('white','red'))
            window['-MESSAGE-'].update('Boom :(')
        else:
            window[event].update(minefield[yDig][xDig], button_color=('white','black'))
            window['-MESSAGE-'].update('Mines left: wip')
    window.close()
    return Regenerate, int(values['-COLUMNS-']), int(values['-ROWS-']), int(values['-MINES-'])

def pySolver():
    pass

cols, rows = (10,8)
mines = 20

minefield = list(list())

regenerate = True
while regenerate:
    regenerate = False
    regenerate, cols, rows, mines = pySweeper(cols, rows, mines)
