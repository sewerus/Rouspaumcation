from os import listdir, mkdir
from tqdm import tqdm
from copy import deepcopy
import numpy

from demand import Demand
from path import Path
from re import findall


def get_traffic(file_name):
    floor_position = file_name.find('_')
    if floor_position == -1:
        return ""
    else:
        return file_name[0:floor_position]


def get_test(file_name):
    floor_position = file_name.find('_')
    dot_position = file_name.find('.')
    if floor_position == -1 or dot_position == -1:
        return ""
    else:
        return file_name[(floor_position + 1):dot_position]


class Rouspaumcation:
    def __init__(self):
        # network input parameters
        self.iterations_amount = 2000
        self.S = 320
        self.K = 7
        self.candidate_paths = 30
        self.storage_size = 0
        # test input parameters
        self.data_directory = "Euro16"
        self.result_directory = self.data_directory + "_results"
        self.net_file = ""
        self.pat_file = ""
        self.spec_file = ""
        self.traffics = []
        self.tests = []
        # network file parameters
        self.V_amount = 0
        self.V = []
        self.E_amount = 0
        self.E = []
        self.edges_matrix = []
        self.P_i_j = []
        self.delta_e_i_j_p = []
        # number of paths between every two nodes in .pat file
        self.k = 30

        self.show_start_information()
        self.get_test_data()
        self.select_data_directory()
        if self.check_files():
            print("All the necessary files are in the directory")
            self.read_net_file()
            self.read_pat_spec_file()
            self.do_all_test()
        else:
            print("Please, check files in directory and then run this program again.")

    def show_start_information(self):
        print("Dynamic routing, space and spectrum allocation (RSSA)"
              " of unicast demands in flex-grid network with assistive storage")
        print("\nBy Seweryn Panek & Maciej Drzewinski")
        print("Wroclaw University of Science and Technology, Poland")

    def get_test_data(self):
        print("\nPlease, now enter network parameters:")
        self.K = int(input("Number of cores (ex. 1, 7, 12): "))
        self.candidate_paths = int(input("Number of candidate paths (ex. 10, 20, 30): "))
        self.storage_size = int(input("Size of Assistive Storage (ex. 0, 10, 20, ..., 100): "))

    def select_data_directory(self):
        print("\"Selection of data directory with .dem, .spec .net and .pat files")
        self.data_directory = input("Enter name of data directory (ex. 'Euro16'): ")
        self.result_directory = self.data_directory + "_results"

    def check_files(self):
        files = listdir(self.data_directory)
        net_files = [title for title in files if title[-4:] == ".net"]
        pat_files = [title for title in files if title[-4:] == ".pat"]
        spec_files = [title for title in files if title[-5:] == ".spec"]
        dem_files = [title for title in files if title[-4:] == ".dem"]

        if len(net_files) == 1:
            self.net_file = net_files[0]
            print("Founded .net file: " + self.net_file)
        else:
            print("It is not possible to choose .net file.")
            return False
        if len(pat_files) == 1:
            self.pat_file = pat_files[0]
            print("Founded .pat file: " + self.pat_file)
        else:
            print("It is not possible to choose .pat file.")
            return False
        if len(spec_files) == 1:
            self.spec_file = spec_files[0]
            print("Founded .spec file: " + self.spec_file)
        else:
            print("It is not possible to choose .spec file.")
            return False
        if len(dem_files) == 0:
            print("There are no .dem files.")
            return False

        dem_traffics = list(map(get_traffic, dem_files))
        dem_tests = list(map(get_test, dem_files))

        dem_error_files = [part for part in dem_traffics if part == ""] + [part for part in dem_tests if part == ""]
        if len(dem_error_files) > 0:
            print("There are problems in .dem files with their names.")
            return False

        self.traffics = sorted(list(set(list(map(int, dem_traffics)))))
        self.tests = sorted(list(set(list(map(int, dem_tests)))))

        dem_start_traffic = self.traffics[0]
        dem_end_traffic = self.traffics[-1]
        dem_start_test = self.tests[0]
        dem_end_test = self.tests[-1]

        print("Traffics of .dem files from " + str(dem_start_traffic) + " to " + str(dem_end_traffic))
        print("Tests of .dem files from " + str(dem_start_test) + " to " + str(dem_end_test))

        return True

    def read_net_file(self):
        net_file = open(self.data_directory + "/" + self.net_file, "r")
        net_lines = net_file.readlines()
        net_file.close()
        self.V_amount = int(findall('[0-9]+', net_lines[0])[0])
        self.V = range(self.V_amount)
        self.E_amount = int(findall('[0-9]+', net_lines[1])[0])
        self.E = range(self.E_amount)
        for i in range(self.V_amount):
            self.edges_matrix.append([])
            edges_line = net_lines[2 + i]
            v_edges = findall('[0-9]+', edges_line)
            for j in range(self.V_amount):
                if int(v_edges[j]) > 0:
                    self.edges_matrix[-1].append(1)
                else:
                    self.edges_matrix[-1].append(0)

    def read_pat_spec_file(self):
        pat_file = open(self.data_directory + "/" + self.pat_file, "r")
        pat_lines = pat_file.readlines()
        spec_file = open(self.data_directory + "/" + self.spec_file, "r")
        spec_lines = spec_file.readlines()
        spec_file.close()
        pat_file.close()

        # prepare P_i_j
        path_index = 0
        for v_i in range(self.V_amount):
            self.P_i_j.append([])
            for v_j in range(self.V_amount):
                self.P_i_j[-1].append([])
                if v_i != v_j:
                    for n in range(self.k):
                        path_edges = list(map(int, findall('[0-9]+', pat_lines[path_index + 1])))
                        path_spec = list(map(int, findall('[0-9]+', spec_lines[path_index + 1])))
                        path = Path(v_i, v_j, path_edges, path_spec)
                        self.P_i_j[-1][-1].append(path)
                        path_index += 1
        # prepare delta_e_p_i_j
        for e in self.E:
            self.delta_e_i_j_p.append([])
            for v_i in self.V:
                self.delta_e_i_j_p[-1].append([])
                for v_j in self.V:
                    self.delta_e_i_j_p[-1][-1].append([])
                    for p in self.P_i_j[v_i][v_j]:
                        if e in p.edges:
                            self.delta_e_i_j_p[-1][-1][-1].append(1)
                        else:
                            self.delta_e_i_j_p[-1][-1][-1].append(0)

    def do_all_test(self):
        print("Network is ready to do tests")
        mkdir(self.result_directory)
        results_file = open(self.result_directory + "/all_results.txt", "w+")
        results_file.write(";;;Summed bitrate of demands;;;Number of demands;;;\n")
        results_file.write("Network Load;Test case;;All incoming; Served; Rejected;All incoming; Served; Rejected;\n")

        for traffic in self.traffics:
            for test in self.tests:
                self.do_single_test(traffic, test)
        results_file.close()

    def do_single_test(self, traffic, test):
        print("Started test " + str(traffic) + " - " + str(test) + " - storage: " + str(self.storage_size))

        # handle files
        file_name = str(traffic) + "_0" + str(test) + ".dem"
        result_file_name = str(traffic) + "_0" + str(test) + "_result.dem"
        if test > 9:
            file_name = str(traffic) + "_" + str(test) + ".dem"
            result_file_name = str(traffic) + "_" + str(test) + "_result.dem"
        dem_file = open(self.data_directory + "/" + file_name, "r")
        demands_lines = dem_file.readlines()
        dem_file.close()

        # save solution
        dem_result_file = open(self.result_directory + "/" + result_file_name, "a+")
        dem_result_file.write("Demand;Time in Storage;Start Processing Iteration;Chosen Path;Chosen Core;Chosen Slice\n")

        # read all demands
        demands = []
        for demand_line in demands_lines:
            demand_data = list(map(int, findall('[0-9]+', demand_line)))
            if len(demand_data) == 5:
                new_demand = Demand(demand_data[0], demand_data[1], demand_data[2], demand_data[3], demand_data[4])
                new_demand.add_paths(self.P_i_j[new_demand.s][new_demand.t], self.candidate_paths, self.E_amount)
                demands.append(new_demand)
            else:
                print("There is wrong data in file " + file_name + ". Demand line: " + demand_line)

        # prepare variables r_d, b_d, x_d_p, c_d_k_s, delta_e_d_p, y_n_e_k_s, B_v
        print("\tPreparing variables")
        demands_amount = len(demands)
        x_d_p = numpy.zeros((demands_amount, self.candidate_paths), dtype=int)
        c_d_k_s = numpy.zeros((demands_amount, self.K, self.S), dtype=int)
        delta_e_d_p = numpy.zeros((self.E_amount, demands_amount, self.candidate_paths), dtype=int)
        B_v = numpy.full((self.V_amount), self.storage_size, dtype=int)
        y_n_e_k_s = numpy.zeros((self.iterations_amount, self.E_amount, self.K, self.S), dtype=int)
        all_gbps = 0
        rejected_demands_counter = 0
        rejected_demands_bitrate = 0
        served_in_iteration_counter = [0 for n in range(self.iterations_amount)]
        served_in_iteration_bitrate = [0 for n in range(self.iterations_amount)]
        for d in demands:
            all_gbps += d.h
        print("\tCalculating delta_e_d_p")
        for e in self.E:
            for d_index in range(demands_amount):
                d = demands[d_index]
                for p_index in range(d.P_d_amount):
                    p = d.P_d[p_index]
                    if e in p.edges:
                        delta_e_d_p[e][d_index][p_index] = 1
        np_delta_e_d_p = numpy.array(delta_e_d_p)

        print("\tStart iterations")
        # do iterations
        iteration_demands_indices = set()
        stored_demands_indices = set()
        start_demand_index = 0
        for n in tqdm(range(self.iterations_amount)):
            #######################################################################
            # method - equation 9 - calculate D_e_k_s
            # print("\n\t\tEquation 9/21")
            #######################################################################

            # there are 9 conditions to check

            iteration_demands_indices = set()

            for d_index in range(start_demand_index, demands_amount):
                # stop if future demands
                d = demands[d_index]
                if d.a > n:
                    break
                start_demand_index += 1
                iteration_demands_indices.add(d_index)
            iteration_demands_indices = iteration_demands_indices.union(stored_demands_indices)

            iteration_demands_indices_amount = len(iteration_demands_indices)
            if iteration_demands_indices_amount == 0:
                continue

            D_e_k_s = [[[[False for d in range(iteration_demands_indices_amount)] for s in range(self.S)] for k in range(self.K)] for e in self.E]
            iteration_demands_indices_copy = numpy.array(list(iteration_demands_indices))
            for e in self.E:
                if not numpy.any(np_delta_e_d_p[e, list(iteration_demands_indices), :]):
                    continue
                for k in range(self.K):
                    for s in range(self.S):
                        # if y_n_e_k_s = 1, then D_e_k_s is empty
                        if y_n_e_k_s[n][e][k][s] == 1:
                            D_e_k_s[-1][-1][-1] = [False for i in range(len(iteration_demands_indices))]
                        else:
                            d_index_in_iteration_demands = 0
                            for d_index in iteration_demands_indices:
                                is_chosen = False
                                d = demands[d_index]
                                # calculate f_e_h_d
                                # (assumption, that for this edge we take min f_e_h_d value of all paths)
                                f_e_h_d = d.slices_on_edge[e]
                                # check y_n_e_k_(s-1) = 0                                       (8-th condition)
                                if (s > 0 and y_n_e_k_s[n][e][k][s - 1] == 0) or (s == 0):
                                    # check: s + f_e_h_d < |S|                                  (6-th condition)
                                    if s + f_e_h_d < self.S:
                                        # check: y_n_e_k_(s+1) = 0                              (9-th condition)
                                        if (s + f_e_h_d < self.S - 1 and y_n_e_k_s[n][e][k][s + f_e_h_d] == 0) \
                                                or s + f_e_h_d == self.S - 1:
                                            y_n_e_k_s_sum = 0
                                            for s_prim in range(s, s + f_e_h_d):
                                                y_n_e_k_s_sum += y_n_e_k_s[n][e][k][s_prim]
                                            # check: sum of y_n_e_k_s                           (7-th condition)
                                            if y_n_e_k_s_sum == 0:
                                                is_chosen = True
                                if is_chosen:
                                    D_e_k_s[e][k][s][d_index_in_iteration_demands] = True
                                d_index_in_iteration_demands += 1

            # print("\t\tDONE Equation 9/21")
            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            # repeating equalations 10-17
            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

            np_D_e_k_s = numpy.array(D_e_k_s)

            it_is_possible_to_choose_demand = True
            while it_is_possible_to_choose_demand and len(iteration_demands_indices) > 0:

                D_e_k_s_prim = [[[[] for i in range(self.S)] for j in range(self.K)] for k in self.E]

                #######################################################################
                # method - equation 10 - calculate c_d_prim
                # print("\t\tEquation 10/21")
                #######################################################################

                c_d_prim = [[] for i in range(demands_amount)]
                for d_index in iteration_demands_indices:
                    d = demands[d_index]
                    index_in_iteration_demands = list(iteration_demands_indices_copy).index(d_index)
                    for p_index in range(d.P_d_amount):
                        p = d.P_d[p_index]
                        for k in range(self.K):
                            for s in range(self.S):
                                if all(np_D_e_k_s[p.edges, k, s, index_in_iteration_demands]):
                                    c_d_prim[d_index].append([p_index, k, s])

                # print("\t\tDONE Equation 10/21")
                #######################################################################
                # method - equation 11 - calculate D_e_k_s_prim
                # print("\t\tEquations 11/21")
                #######################################################################

                for d_index in iteration_demands_indices:
                    d = demands[d_index]
                    for [p_index, k, s] in c_d_prim[d_index]:
                        p = d.P_d[p_index]
                        for e in p.edges:
                            if not(d_index in D_e_k_s_prim[e][k][s]):
                                D_e_k_s_prim[e][k][s].append(d_index)

                #######################################################################
                # method - equation 12 - choose min D_e_k_s_prim
                # method - equation 13 - choose demand with shortest delay
                # print("\t\tEquations 12-13/21")
                #######################################################################

                founded_min_D_e_k_s_prim = False
                D_e_k_s_prim_min_e = -1
                D_e_k_s_prim_min_k = -1
                D_e_k_s_prim_min_s = -1
                min_D_e_k_s_prim = []
                chosen_demand = demands[0]
                chosen_demand_index = -1

                for e in self.E:
                    if len(D_e_k_s_prim[e]) == 0:
                        continue
                    for k in range(self.K):
                        for s in range(self.S):
                            if len(D_e_k_s_prim[e][k][s]) == 0:
                                continue
                            # choosing min_D_e_k_s_prim
                            if not founded_min_D_e_k_s_prim:
                                founded_min_D_e_k_s_prim = True
                                D_e_k_s_prim_min_e = e
                                D_e_k_s_prim_min_k = k
                                D_e_k_s_prim_min_s = s
                                min_D_e_k_s_prim = D_e_k_s_prim[e][k][s]
                                chosen_demand_index = min_D_e_k_s_prim[0]
                                chosen_d = demands[chosen_demand_index]

                                # choose demand with shortest delay
                                for another_demand_index in min_D_e_k_s_prim[1:]:
                                    another_d = demands[another_demand_index]
                                    if another_d.l < chosen_d.l:
                                        chosen_demand_index = another_demand_index
                                        chosen_d = another_d
                            else:
                                if len(D_e_k_s_prim[e][k][s]) < len(min_D_e_k_s_prim):
                                    D_e_k_s_prim_min_e = e
                                    D_e_k_s_prim_min_k = k
                                    D_e_k_s_prim_min_s = s
                                    min_D_e_k_s_prim = D_e_k_s_prim[e][k][s]

                                    chosen_demand_index = min_D_e_k_s_prim[0]
                                    chosen_d = demands[chosen_demand_index]

                                    # choose demand with shortest delay
                                    for another_demand_index in min_D_e_k_s_prim[1:]:
                                        another_d = demands[another_demand_index]
                                        if another_d.l < chosen_d.l:
                                            chosen_demand_index = another_demand_index
                                            chosen_d = another_d
                                elif len(D_e_k_s_prim[e][k][s]) == len(min_D_e_k_s_prim):
                                    # choose resource with demand with shortest delay
                                    for another_demand_index in D_e_k_s_prim[e][k][s]:
                                        another_d = demands[another_demand_index]
                                        if another_d.l < chosen_d.l:
                                            chosen_demand_index = another_demand_index
                                            chosen_d = another_d
                                            D_e_k_s_prim_min_e = e
                                            D_e_k_s_prim_min_k = k
                                            D_e_k_s_prim_min_s = s
                                    min_D_e_k_s_prim = D_e_k_s_prim[D_e_k_s_prim_min_e][D_e_k_s_prim_min_k][D_e_k_s_prim_min_s]
                chosen_d = demands[chosen_demand_index]

                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                # break loop, it is impossible to choose demand
                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                if chosen_demand_index == - 1:
                    it_is_possible_to_choose_demand = False
                    break

                #######################################################################
                # method - equation 14 - select possible paths for this demand
                # print("\t\tEquation 14/21")
                #######################################################################

                possible_paths = []
                for [p_index, k, s] in c_d_prim[chosen_demand_index]:
                    if k == D_e_k_s_prim_min_k:
                        if s == D_e_k_s_prim_min_s:
                            if delta_e_d_p[D_e_k_s_prim_min_e][chosen_demand_index][p_index]:
                                possible_paths.append(p_index)

                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                # break loop, it is impossible to choose demand
                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                if len(possible_paths) == 0:
                    it_is_possible_to_choose_demand = False
                    break

                #######################################################################
                # method - equation 15 - select the best path from possibles
                # print("\t\tEquation 15/21")
                #######################################################################

                chosen_path_index = possible_paths[0]
                chosen_path = chosen_d.P_d[chosen_path_index]
                demands_on_chosen_path = set()
                for e in chosen_path.edges:
                    for d_on_path in D_e_k_s_prim[e][D_e_k_s_prim_min_k][D_e_k_s_prim_min_s]:
                        demands_on_chosen_path.add(d_on_path)
                for other_possible_path_index in possible_paths[1:]:
                    other_path = chosen_d.P_d[other_possible_path_index]
                    demands_on_other_path = set()
                    for e in other_path.edges:
                        for d_on_path in D_e_k_s_prim[e][D_e_k_s_prim_min_k][D_e_k_s_prim_min_s]:
                            demands_on_other_path.add(d_on_path)
                    if len(demands_on_other_path) < len(demands_on_chosen_path):
                        chosen_path_index = other_possible_path_index
                        chosen_path = other_path
                        demands_on_chosen_path = demands_on_other_path

                #######################################################################
                # method - equation 16 - allocate resources
                # print("\t\tEquation 16/21")
                #######################################################################

                x_d_p[chosen_demand_index][chosen_path_index] = 1
                for j in range(chosen_d.l):
                    if n + j >= self.iterations_amount:
                        break
                    for i in range(chosen_d.slices_on_path[chosen_path_index]):
                        if D_e_k_s_prim_min_s + i >= self.S:
                            print("\n\tError: ")
                            print("\t\tAllocating demand: " + str(chosen_demand_index))
                            print("\t\tPath: " + str(chosen_path_index))
                            print("\t\tCore: " + str(D_e_k_s_prim_min_k))
                            print("\t\tSlices from: " + str(D_e_k_s_prim_min_s))
                            print("\t\tSlices to: " + str(D_e_k_s_prim_min_s + chosen_d.slices_on_path[chosen_path_index]))
                            break
                        y_n_e_k_s[n + j][D_e_k_s_prim_min_e][D_e_k_s_prim_min_k][D_e_k_s_prim_min_s + i] = 1
                chosen_d.q = 1

                if n + chosen_d.l < self.iterations_amount:
                    served_in_iteration_counter[n + chosen_d.l] += 1
                    served_in_iteration_bitrate[n + chosen_d.l] += chosen_d.h

                #######################################################################
                # method - equation 17 - update D_e_k_s
                # print("\t\tEquation 17/21")
                #######################################################################

                np_D_e_k_s[:, :, :, list(iteration_demands_indices_copy).index(chosen_demand_index)] = False
                np_D_e_k_s[chosen_path.edges, D_e_k_s_prim_min_k, D_e_k_s_prim_min_s, :] = False

                iteration_demands_indices.remove(chosen_demand_index)
                if chosen_demand_index in stored_demands_indices:
                    stored_demands_indices.remove(chosen_demand_index)

                # print("\n Chosen demand: " + str(chosen_demand_index))
                # print("\t Chosen e: " + str(D_e_k_s_prim_min_e))
                # print("\t Chosen k: " + str(D_e_k_s_prim_min_k))
                # print("\t Chosen s: " + str(D_e_k_s_prim_min_s))
                # print("\t Chosen path: " + str(chosen_path_index))
                # save solution
                # dem_result_file.write(str(chosen_demand_index) + ";" + str(chosen_d.b) + ";" + str(n) + ";" + str(chosen_path_index) + ";" + str(D_e_k_s_prim_min_k) + ";" + str(D_e_k_s_prim_min_s) + ";\n")

            #######################################################################
            # method - equation 18 - select demands that can be stored
            # print("\t\tEquation 18/21")
            #######################################################################

            D_prim_prim = iteration_demands_indices

            #######################################################################
            # method - equation 19 - select demands that can be stored on source node
            # print("\t\tEquation 19/21")
            #######################################################################

            D_prim_prim_v = [[] for i in self.V]
            for d_index in D_prim_prim:
                d = demands[d_index]
                D_prim_prim_v[d.s].append(d_index)

            #######################################################################
            # method - equation 20 - reject demands
            # print("\t\tEquation 20/21")
            #######################################################################

            stored_demands_indices = set()
            for v_index in self.V:
                demands_sorted_by_l = sorted(D_prim_prim_v[v_index], key=lambda x: demands[x].l)
                stored_demands_indices = demands_sorted_by_l[:self.storage_size]
                for stored_demand in demands_sorted_by_l[:self.storage_size]:
                    demands[stored_demand].b += 1
                for rejected_demand in demands_sorted_by_l[self.storage_size:]:
                    rejected_demands_counter += 1
                    rejected_demands_bitrate += demands[rejected_demand].h
                    demands[rejected_demand].r = 1

            #######################################################################
            # method - equation 21 - set demands as completed
            # print("\t\tEquation 21/21")
            #######################################################################

            if n % 10 == 0:
                print("\nTraffic;\tTest;\tStorage;\tAll bitrate;\tServed bitrate;\tRejected bitrate;\tAll demands;\tServed demands;\tRejected demands;\n")
                print("Tr:\t" + str(traffic) + ";\tTe:\t" + str(test) + ";\tSt:\t" + str(self.storage_size) + ";\tAG: " + str(all_gbps) + ";\tSG:\t" + str(sum(served_in_iteration_bitrate[:n])) + ";\tRG:\t" + str(rejected_demands_bitrate) + ";\tAD: " + str(demands_amount) + ";\tSD:\t" + str(sum(served_in_iteration_counter[:n])) + ";\tRD:\t" + str(rejected_demands_counter) + ";\n\n")

        #######################################################################
        # end of test - saving results
        # print("\t\tSAVINGS RESULTS")
        #######################################################################
        dem_result_file.close()

        results_file = open(self.result_directory + "/summarized_result_" + str(traffic) + "_" + str(test) + "_" + str(self.storage_size) + ".txt", "a+")
        results_file.write(str(traffic) + ";" + str(test) + ";" + str(self.storage_size) + ";;" + str(all_gbps) + ";" + str(sum(served_in_iteration_bitrate)) + ";" + str(rejected_demands_bitrate) + ";" + str(demands_amount) + ";" + str(sum(served_in_iteration_counter)) + ";" + str(rejected_demands_counter) + ";\n")
        results_file.close()


rouspaumcation = Rouspaumcation()
