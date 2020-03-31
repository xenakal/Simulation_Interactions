from main import*
import constants




map_to_test_name = ["complet_map_to_test_des-activation","test_alex_2_kalman_centralisé_4_no_obstruction",
"test_alex_2_kalman_distributé_4_no_obstruction","test_antoine_problème_centralisé_4","test_antoine_solution_centralisé_4",
"text_alex_1_kalman_centralisé_4","text_alex_1_kalman_distribué_4"]


kalman_distributed = [False,False,True,False,True,False,False,True]
kalman_type = [4,4,4,4,4,4,4]
t_stop = [20,20,20,20,10,10,20]

constants.MapPath.folder = "to_test"
for name,kalman_distributed_elem,kalman_type_elem,t_stop_elem  in zip(map_to_test_name,kalman_distributed,kalman_type,t_stop):
    print("processing "+str(name))
    App(name,kalman_distributed_elem,kalman_type_elem,t_stop_elem).main()

