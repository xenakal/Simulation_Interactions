from main import*

map_to_test_name = ["My_new_map", "My_new_map1"]
for name in map_to_test_name:
    print("processing "+str(name))
    App(name).main()
