from GeoApp.DataManager import DataManager

dm = DataManager()
dm.load_contents()

lst = dm.get_uniques()

path = dm.get_path_by_unique(lst[0])

path = dm.get_path_by_unique('a')
