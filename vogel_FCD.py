import zipfile
import numpy as np
import pandas as pd
import time

def parse_instance_from_zip(file):
    lines = file.readlines()
    instance_name = ""
    d = 0
    r = 0
    SCj = []
    Dk = []
    Cjk = []

    i = 0  # Index pentru a itera prin lines
    while i < len(lines):
        line = lines[i].decode('utf-8').strip()
        if line.startswith("instance_name"):
            instance_name = line.split('=')[1].strip().strip('";')
        elif line.startswith("d ="):
            d = int(line.split('=')[1].strip().strip(';'))
        elif line.startswith("r ="):
            r = int(line.split('=')[1].strip().strip(';'))
        elif line.startswith("SCj ="):
            SCj = list(map(int, line.split('=')[1].strip().strip('[];').split()))
        elif line.startswith("Dk ="):
            Dk = list(map(int, line.split('=')[1].strip().strip('[];').split()))
        elif line.startswith("Cjk ="):
            costs = []
            while not line.endswith("];"):
                costs.extend([x for x in line.replace('[', '').replace(']', '').replace(';', '').split() if x.isdigit()])
                i += 1
                line = lines[i].decode('utf-8').strip()
            costs.extend([x for x in line.replace('[', '').replace(']', '').replace(';', '').split() if x.isdigit()])
            Cjk = [list(map(int, costs[i:i + r])) for i in range(0, len(costs), r)]
        i += 1

    return instance_name, d, r, SCj, Dk, Cjk

def vogel_method(SCj, Dk, Cjk):
    d = len(SCj)
    r = len(Dk)
    cost_matrix = np.array(Cjk)
    solution_matrix = np.zeros((d, r))
    remaining_demand = Dk[:]
    remaining_supply = SCj[:]

    INF = 9999999  # Folosim o valoare mare pentru a reprezenta "infinity"
    iteration_count = 0  # Contor pentru iterații

    while np.any(remaining_demand) and np.any(remaining_supply):
        iteration_count += 1  # Incrementăm numărul de iterații

        # Calculăm penalizarea pentru fiecare rând și coloană
        row_penalties = []
        for i in range(d):
            row = cost_matrix[i, :]
            row_sorted = np.sort(row[row > 0])
            if len(row_sorted) > 1:
                row_penalties.append(row_sorted[1] - row_sorted[0])
            else:
                row_penalties.append(INF)

        col_penalties = []
        for j in range(r):
            col = cost_matrix[:, j]
            col_sorted = np.sort(col[col > 0])
            if len(col_sorted) > 1:
                col_penalties.append(col_sorted[1] - col_sorted[0])
            else:
                col_penalties.append(INF)

        # Alegem rândul sau coloana cu penalizarea maximă
        max_row_penalty_idx = np.argmax(row_penalties)
        max_col_penalty_idx = np.argmax(col_penalties)

        if row_penalties[max_row_penalty_idx] >= col_penalties[max_col_penalty_idx]:
            row_idx = max_row_penalty_idx
            col_idx = np.argmin(cost_matrix[row_idx, :])
        else:
            col_idx = max_col_penalty_idx
            row_idx = np.argmin(cost_matrix[:, col_idx])

        # Alocăm produsele
        allocation = min(remaining_supply[row_idx], remaining_demand[col_idx])
        solution_matrix[row_idx, col_idx] = allocation
        remaining_supply[row_idx] -= allocation
        remaining_demand[col_idx] -= allocation

        # Actualizăm matricea de costuri
        if remaining_supply[row_idx] == 0:
            cost_matrix[row_idx, :] = INF  # Folosim INF pentru a marca rândurile completate
        if remaining_demand[col_idx] == 0:
            cost_matrix[:, col_idx] = INF  # Folosim INF pentru a marca coloanele completate

    # Verificăm dacă problema a fost soluționată complet
    solved = np.isclose(np.sum(remaining_demand), 0) and np.isclose(np.sum(remaining_supply), 0)

    return solution_matrix, iteration_count, solved

def solve_vogel(zip_path, output_file):
    instances_results = []

    with zipfile.ZipFile(zip_path, 'r') as archive:
        for filename in archive.namelist():
            if filename.endswith('.dat'):
                with archive.open(filename) as file:
                    instance_name, d, r, SCj, Dk, Cjk = parse_instance_from_zip(file)

                    # Aplicăm algoritmul Vogel și măsurăm timpul de rulare
                    start_time = time.time()
                    solution_matrix, iteration_count, solved = vogel_method(SCj, Dk, Cjk)
                    end_time = time.time()

                    # Calculăm costul optim
                    optimal_cost = np.sum(solution_matrix * np.array(Cjk))

                    # Calculăm timpul de rulare
                    run_time = end_time - start_time

                    # Înregistrăm rezultatul
                    instances_results.append([instance_name, optimal_cost, iteration_count, run_time, solved])

    # Salvăm rezultatele în fișier Excel
    df = pd.DataFrame(instances_results, columns=['Instance', 'Optimal Cost', 'Iterations', 'Run Time (s)', 'Solved'])

# Calea către arhiva zip
zip_path = r'C:\Users\deniv\PycharmProjects\probleme_transport\FCD_instances.zip'
output_file = r'C:\Users\deniv\PycharmProjects\probleme_transport\FCD_results.xlsx'
solve_vogel(zip_path, output_file)