from heuristic import *
from helper import *

VG, EG = read_graph(r"Spd_Inst_Rid_Final2\Spd_RF2_20_27_211.txt")
final_edges, solution_info = iterative_mbvst_with_lp_file(VG, EG, max_iter=50, randomize=False)
