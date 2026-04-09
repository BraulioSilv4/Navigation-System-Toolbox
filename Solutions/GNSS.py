# import math
# from itertools import combinations
# from typing import List, Tuple
#
# import numpy as np
#
# from common.Orbits.Ephemeris import Ephemeris
# from common.Orbits.ephemeris_parser import EphemerisParser
# from common.data_components import ECEF, PDOP, HDOP, LLH
# from common.functions import LS
# from common.nprParser import NPRData, nprParser
#
# r1: ECEF = ECEF(x=4918525.18, y=-791212.21, z=3969762.19)
# s10: ECEF = ECEF(x=-5845119.0, y=-14047494.0, z=21837689.0)
#
# ########################################################################################################################
# ################################################ Exercise 1 ############################################################
# ########################################################################################################################
# true_range = r1.range(s10)
# print(f"True range between observer and satellite: {true_range:.4f} m")
#
# pseudorange = r1.pseudorange(s10, offset=500e-6)
# print(f"Pseudorange between observer and satellite with 500 microseconds offset: {pseudorange:.4f} m")
#
#
# ########################################################################################################################
# ################################################ Exercise 2 ############################################################
# ########################################################################################################################
# # z = Hx
# # a) z -> 8x1   vector of pseudorange measurements - the expected distance between the observer and each satellite
# # b) H -> 8x4   observation matrix, used to calculate DOP
# # c) x -> 4x1   State vector, holds unknowns we are trying to estimate (x, y, z, clock bias)
# # d) H^T -> 4x8
# # e) H^T * H -> 4x4
# # f) (H^T * H)^-1 -> 4x4
# # g) (H^T * H)^-1 * H^T -> 4x1
#
# ########################################################################################################################
# ################################################ Exercise 3 ############################################################
# ########################################################################################################################
# hthinv = np.array(
#     [
#         [1.108, -0.148, 0.491, 0.608],
#         [-0.148, 0.386, 0.165, -0.011],
#         [0.491, 0.165, 1.152, 0.590],
#         [0.608, -0.011, 0.590, 0.570]
#     ]
# )
# pdop = PDOP(hthinv)
# print(f"PDOP value: {pdop:.4f}")
#
# ########################################################################################################################
# ############################################## Exercise 4 & 5 ##########################################################
# ########################################################################################################################
# eph_parser: EphemerisParser = EphemerisParser(file="../data/ub1.ubx.2056.540000b.eph")
# orb: List[Tuple[int, Ephemeris]] = eph_parser.parse()
#
# svn_true_range = {}
# svn_pseudo_range = {}
#
# curr_offset = 500e-6
# start = 536400
# for i in range(3600):
#     for svn, eph in orb:
#         pos_at_tx, niter = eph.sat_position_at_tx(r=r1, t_rx=start + i) # compute satellite position at transmission time
#         enu = r1.ecef_to_enu(target=pos_at_tx)
#         elevation = enu.elevation()
#         if elevation > 10.0:
#             true_range = r1.range(pos_at_tx)
#             pseudorange = r1.pseudorange(pos_at_tx, offset=curr_offset)
#             svn_true_range[svn] = svn_true_range.get(svn, []) + [true_range]
#             svn_pseudo_range[svn] = svn_pseudo_range.get(svn, []) + [pseudorange]
#
#     curr_offset += 0.4e-6
#
#
# # plot the ranges & pseudoranges for each satellite
# # import matplotlib.pyplot as plt
# #
# # for svn in dict_svn_range.keys():
# #     plt.figure(figsize=(10, 5))
# #     plt.plot(dict_svn_range[svn], label='True Range')
# #     plt.plot(dict_svn_range_with_offset[svn], label='Pseudorange with offset')
# #     plt.title(f'Satellite SVN {svn}')
# #     plt.xlabel('Time (s)')
# #     plt.ylabel('Range (m)')
# #     plt.legend()
# #     plt.grid()
# #     plt.show()
#
# ########################################################################################################################
# ################################################ Exercise 6 ############################################################
# ########################################################################################################################
# r3 = ECEF(x=4918510.02634744, y=-791215.407423002, z=3969631.08558596)
#
# npr_data: list[NPRData] = nprParser("../data/npr.txt")
# pseudo_ranges: list[float] = [npr.pseudoranges[0] for npr in npr_data]  # Pseudoranges for the first epoch (t=536400.0 seconds)
# orb_above_10_deg = []
# for svn, eph in orb:
#     pos_at_tx, niter = eph.sat_position_at_tx(r=r1, t_rx=536400.0)
#     enu = r1.ecef_to_enu(target=pos_at_tx)
#     elevation = enu.elevation()
#     if elevation > 10.0:
#         orb_above_10_deg.append(eph)
#
# prange_sats: list[tuple[float, Ephemeris]] = list(zip(pseudo_ranges, orb_above_10_deg))
# position, estimate, _, niter = LS(guess=ECEF(0.0,0.0,0.0), prange_sats=prange_sats, trx=536400.0, max_iter=10, debug=True)
#
# print(f"Estimated position: {position}, clock bias: {estimate:.4f} m, estimated error: {position.range(r1)}  (1mm precision achieved in {niter} iterations)")
#
# ########################################################################################################################
# ################################################ Exercise 7 ############################################################
# ########################################################################################################################
# class CombinationResult:
#     size: int
#     max_pdop, min_pdop = float('-inf'), float('inf')
#     max_pdop_combo, min_pdop_combo = None, None
#     max_hdop, min_hdop = float('-inf'), float('inf')
#     max_hdop_combo, min_hdop_combo = None, None
#
# resdata: list[CombinationResult] = []
#
# for size in range(4, len(prange_sats) + 1):
#     res = CombinationResult()
#     for combo in combinations(prange_sats, size):
#         _, _, H, _ = LS(guess=r3, prange_sats=list(combo), trx=536400.0, max_iter=10, debug=False)
#         r3_rot = r3.ecef_to_llh().to_rotation()
#
#         hthinv = np.linalg.inv(H.T @ H)
#         hthinv_enu = r3_rot @ hthinv[:3, :3] @ r3_rot.T
#
#         pdop = PDOP(hthinv_enu)
#         hdop = HDOP(hthinv_enu)
#         if pdop > res.max_pdop:
#             res.max_pdop = pdop
#             res.max_pdop_combo = combo
#
#         if pdop < res.min_pdop:
#             res.min_pdop = pdop
#             res.min_pdop_combo = combo
#
#         if hdop > res.max_hdop:
#             res.max_hdop = hdop
#             res.max_hdop_combo = combo
#
#         if hdop < res.min_hdop:
#             res.min_hdop = hdop
#             res.min_hdop_combo = combo
#
#     resdata.append(res)
#
# for res in resdata:
#     print("---------------------------------------------")
#     print(f"Min PDOP: {res.min_pdop:.4f} with combination: {[orb.SVN for _, orb in res.min_pdop_combo]}")
#     print(f"Max PDOP: {res.max_pdop:.4f} with combination: {[orb.SVN for _, orb in res.max_pdop_combo]}")
#     print("---------------------------------------------")
#     print(f"Min HDOP: {res.min_hdop:.4f} with combination: {[orb.SVN for _, orb in res.min_hdop_combo]}")
#     print(f"Max HDOP: {res.max_hdop:.4f} with combination: {[orb.SVN for _, orb in res.max_hdop_combo]}")
#
# ########################################################################################################################
# ################################################ Exercise 8 ############################################################
# ########################################################################################################################
# error = 0.0
#
# for i in range(len(npr_data[0].pseudoranges)):
#     pseudo_ranges = [npr.pseudoranges[i] for npr in npr_data]
#     prange_sats = list(zip(pseudo_ranges, orb_above_10_deg))
#     position, estimate, _, _ = LS(guess=r3, prange_sats=prange_sats, trx=536400.0 + i, max_iter=10, debug=False)
#     error += position.range(r1)
#
# error /= len(npr_data[0].pseudoranges)
# print(f"Average error over all epochs: {error:.4f} m")
