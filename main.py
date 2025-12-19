from heuristic import *
from helper import *

test_file = "Spd_Inst_Rid_Final2\Spd_RF2_20_27_211.txt"

VG, EG = read_graph(test_file)
final_edges, solution_info = iterative_mbvst_with_lp_file(VG, EG, max_iter=50, randomize=False)
