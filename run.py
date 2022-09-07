import os
import sys

main_path = os.getcwd()
coll_path = main_path + '/coll/'
generic_path = '/cengage/scripts/generics/'

sys.path.append(main_path)
sys.path.append(coll_path)
sys.path.append(generic_path)

import metadata as META


