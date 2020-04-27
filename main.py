import numpy as np 
import sys 

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout




# Character Codes for input file parsing 

Unpopulated_Char = '.'
Populated_Char = "*"


# Neighbor table for a flat grid, 8 neighbors per cell.
Neigh = []
for i in {-1,0,1}:
    for j in {-1,0,1}:
        if not ( (i==j) and (i==0)):
            Neigh.append((i,j))

# Evolution Matrix respective the rules of the Game of Life
Populated = True
Unpopulated = False
Evolve_Matrix = [ [Unpopulated, Unpopulated, Unpopulated, Populated, Unpopulated, Unpopulated, Unpopulated, Unpopulated, Unpopulated] ,
[Unpopulated, Unpopulated, Populated, Populated, Unpopulated, Unpopulated, Unpopulated, Unpopulated, Unpopulated]]
 


    
class cell :

    # Cell initializer takes as imputs its grid position and its state code (character)
    def __init__ (self, position_X, position_Y, state_code) :
        print (state_code)
        self.position_X = position_X
        self.position_Y = position_Y
        if state_code == Populated_Char :
            self.status = Populated
        else:
            self.status = Unpopulated
           
        self.state_code= state_code
        self.neighbors = 0
     
    # Returns status code (character)
    def get_state_code (self) :
        return self.state_code
     
    def print (self) :

        print (self.position_X, self.position_Y," is ",self.status, self.nextstatus, self.neighbors)

    # Increments the living neighbors counter
    def addlivingneighbor(self) :
        self.neighbors +=1

    # Propagate the status for neighboring cells : 
    # calls "addlivingneighbor" for each neighbor if the cell is populated 
    def propagate_state(self) :
        if (self.status==Populated) :
            for i,j in Neigh:
                try :  
                    Cells[self.position_X+i][self.position_Y+j].addlivingneighbor()
                except KeyError : continue
                except IndexError : continue

    # Updates the cell status based on its previous status and the amount of living neighbors
    def evolve (self) : 
        self.nextstatus = Evolve_Matrix[self.status][self.neighbors]
        self.neighbors = 0
        self.status = self.nextstatus
        if (self.status == Populated) :
            self.state_code = '*'
        else:
            self.state_code = '.'        
        
        
    


class topology (GridLayout):

    def __init__(self, **kwargs):
        super(topology, self).__init__(**kwargs)
        self.cellpositions = []#do nothing

    def create (self, x, y, generation):
        self.generation = generation

        self.init_x = 1
        self.init_y = 0
        self.rows = x
        self.cols = y

        
        for i in range (1, self.rows+1) :
            Cells[i] = {}

    def append (self, char_code):
       
        self.init_y +=1
        if (self.init_y > self.cols) :
            self.init_x +=1
            self.init_y = 1
        Cells[self.init_x][self.init_y] = cell(self.init_x,self.init_y, char_code)
        self.cellpositions.append((self.init_x,self.init_y))
     
        self.add_widget(Label(text=char_code))
        
     
    def evolve_cells (self, source):
        
       # Requests all (populated) cells to propagate their status to their neighbors
       
        for i,j in self.cellpositions :
            Cells[i][j].propagate_state()
            
       # Request all cells to update their status     
        for i,j in self.cellpositions :
            Cells[i][j].evolve()    
        
       # Rebuild the display grid 
        self.clear_widgets()        
        
        for i,j in self.cellpositions :  
            code = Cells[i][j].get_state_code()   
       
            self.add_widget(Label(text=code))

        self.generation +=1
        
       # Store results in output file
        self.printfile("output_"+str(self.generation)+".dat")
        return self.generation

    def printfile (self,filename) :
        f = open (filename,'w')
          
        count = 0
        retval = "Generation "+str(self.generation)+"\n"
        for i,j in self.cellpositions :
            count+=1
            retval +=Cells[i][j].get_state_code()
            if (count == self.cols) :
                count =0
                retval+="\n"
        print (retval)
        f.write(retval)
        f.close()
    


class generation_lbl (Label):
    generation = StringProperty()
    
    def __init__(self, generation, **kwargs):
        super(generation_lbl, self).__init__(**kwargs)
       
        self.text = str(generation)

    def change_label (self,generation):
        self.text = str(generation)

# Global variables for topology (grid container) and cell array.

Topology = topology()
Cells = {}
    
    
def read_scenario (filename):
    file = open (filename) 
    Generation = (file.readline()).split(" ")
    assert (len(Generation)==2)
    assert (Generation[0] == "Generation")
    generation = int(Generation[1][:-2])
    assert (isinstance(generation, int))
    lines, columns = (file.readline()).split(" ")
    lines = int(lines)
    columns = int(columns)
    
    Topology.create (lines, columns, generation)    
    
    for i in range (lines-1) :
        data = (file.readline())[:-1]
        assert (len(data) == columns)
        for i in  (list(data)):
            Topology.append (i)
       
    data = (file.readline())
    if data[len(data)-1]=='\n' :
        data = data[:-1]
    assert (len(data) == columns)
    for i in  (list(data)):
            Topology.append (i)

    return generation


# Man Machine Interface (with Kivy)
class MainApp(App):
        
    generation = str(read_scenario (sys.argv[1]))
    Generation_Label = generation_lbl ("generation: "+ generation,size_hint=(1.0,0.1))
    
    def build(self):
        box = BoxLayout(orientation='vertical')
        self.title = 'Game of Life'
        grid = Topology

        generation_label = Label (text= str(self.generation))
        next = Button(text='Next Gen', size_hint=(1.0,0.1))
        next.bind(on_press=self.evolve)
        box.add_widget(next)
        box.add_widget(grid)
        box.add_widget(self.Generation_Label)
        return box
        
    def evolve (self,source):
       
        self.generation = Topology.evolve_cells(source)

        self.Generation_Label.change_label("generation: "+str(self.generation))
        
if not (len(sys.argv)==2) :
     print ("Usage : python main.py <scenario.file>")  
     exit()
   
MainApp().run()



