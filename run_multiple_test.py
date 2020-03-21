from main import*

map_to_test_name = ["My_new_map"]
for name in map_to_test_name:
    print("processing "+str(name))
    App(name).main()
