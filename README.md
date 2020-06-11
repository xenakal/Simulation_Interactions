<h1> Master thesis : Multi-agent system</h1>

As part of the reseach to conceptualize a **multi-agent system** aimed for the recognition and tracking of several
targets in a room, this simulator was developped to validate several ideas.

The system develloped is composed of two types of agent : the agent-camera and the agent-user.
    
   - The **agent-cameras** collect and filter the data.
    
   - The **agent-users** receive estimates from several agent-cameras and combine them 
      to reconstruct the target's trajectories 

<h2> Quick start guide </h2>

Four scenario, corresponding to the case study presented in the thesis, are available to be tested.\

1. Run the file *main.py* is run and the GUI interface shoud appear on the *simulation tab*. 
<img src="images/simulation_tab.png" width="40%">

<h2> Folders </h2>

   - **src**,  contains the source code
   - **maps**, contains several maps used as input for the system - new maps can be created with the *create map tab* in the GUI interface.
   - **results**, contains results of a simulation - a new file named after the map is created after each simulation and data can be saved/plotted by enabling the option in the *constants.py* file.\
   (SAVE_DATA=TRUE and PLOT_DATA = TRUE)
   - **to_share**, contains genral results that shows the overall possiblities given by simulations. Results are classified  as they are used in the 
   chapter of the thesis. 
    


<h2> Dependancies </h2>
To be able use the simulator fully, the following libraries are necessary:  
    
 1. **numpy** - available at https://numpy.org/
 2. **filterpy** - kalman filtering algorithm, available at https://filterpy.readthedocs.io/en/latest/
 3. **pygame** - to use the GUI interface, available at: https://www.pygame.org/news\
    (required if USE_GUI == TRUE in the constants.py file)  
 4. **sklearn** - to use the pca-method, available at: https://scikit-learn.org/stable/\
    (required if AGENT_MOVE == TRUE, in the constants.py file)  
 5. **matplolib** - https://matplotlib.org/ \
    (required if PLOT == TRUE or to use some plot_function, in the constants.py file)  
     
 The librairies can be all downloaded using pip.  
<h2> License </h2>
