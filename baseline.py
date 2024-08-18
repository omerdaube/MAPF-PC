import subprocess

def parse_path_data(goals, pc):
    print(f'run experiment with {len(pc)} constraints')
    write_file(goals, pc)
    command = f"./bin/cbs -m sample_input/empty-16-16.map -a goal_seq.txt -s 2 -k {len(goals)}"
    result = subprocess.run(['wsl', '-e', 'bash', '-c', command], capture_output=True, text=True)
    text = result.stdout.strip()
    # if len(text.split("Optimal")) >=2:
    text = text.split("Optimal")[1]
    for line in text.split("\n"):
        if line == "":
            continue
        if line[0] == ',':
            csv = line.split(',')
            print(f"CBS-PC: SoC = {csv[1]}, Time = {csv[2]}")
            break
    # print(text)
    soc = 0
    total_time = 0    
    first_time = True
    finished = []
    number_of_goals = [0] * len(goals)
    while goals != []: 
        # print(goals, "\n -------------------------------------")
        stopped = []
        need_to_change_goal = []
        # print(goals)
        # print(number_of_goals)
        # print(finished)
        min_time = float("inf")
        agent = 0
        goals_to_file = [x[:2] for x in goals]

        # print(goals_to_file)
        write_file(goals_to_file)
        command = f"./bin/cbs -m sample_input/empty-16-16.map -a goal_seq.txt -s 2 -k {len(goals)}"
        result = subprocess.run(['wsl', '-e', 'bash', '-c', command], capture_output=True, text=True)
        text = result.stdout.strip()
        # if len(text.split("Optimal")) >=2:
        text = text.split("Optimal")[1]
        for line in text.split("\n"):
            if line == "":
                continue
            if line[0] == ',':
                continue
            else:
                if line[0:5] == "Agent":
                    agent = int(line[6])
                else:
                    arrive_to_first_goal = int(line.split("->")[0].split("@")[1])
                    stopped.append((agent, arrive_to_first_goal))

        correct_idx = 0
        map = {}
        for i in range(len(stopped)):
            while correct_idx in finished:
                correct_idx += 1
            map[stopped[i][0]] = correct_idx
            stopped[i] = (correct_idx, stopped[i][1])
            correct_idx += 1
            # if tup[0] 
        sorted_stopped = sorted(stopped, key=lambda x: x[1])
        # print(sorted_stopped)
        # print(map)
        min_time = 0 
        save_idx = 0
        for tup in sorted_stopped:
            should_continue = False  # Flag to track whether to continue the outer loop

            for constraint in pc:
                if constraint[2] == tup[0] and constraint[3] == number_of_goals[tup[0]] \
                and constraint[1] >= number_of_goals[constraint[0]] - 1:
                    should_continue = True  # Set the flag to continue the outer loop
                    # print(constraint)
                    break  # Exit the inner loop

            if should_continue:
                continue  # Continue the outer loop
            
            min_time = tup[1]
            save_idx = tup[0]
            break  # Exit the outer loop once min_time is set
        
        do_not_move = []
        for tup in sorted_stopped:
            for constraint in pc:
                if constraint[2] == tup[0] and constraint[3] == number_of_goals[tup[0]] \
                and constraint[1] >= number_of_goals[constraint[0]] - 1:
                    if tup[0] not in do_not_move:  # Set the flag to continue the outer loop
                        do_not_move.append(tup[0])
                    # print(constraint)
        # print(f"{do_not_move=}")
        # for tup in sorted_stopped:
        #     if tup[1] <= min_time:
        #         need_to_change_goal.append(tup[0])
        need_to_change_goal = [save_idx]
        # print(f"min_time = {min_time} v. first = {sorted_stopped[0][1]}") 
        if min_time == 0:
            if len(map) > 1:
                print("No solution")
                return
            else:
                # print(goals)
                break
        # exit(0)
        # print(len(goals))
        # print(min_time)
        # print(len(goals) * min_time )
        soc += len(goals) * min_time
        # numbers of goals
        # need_to_change_goal
        agent = 0
        for line in text.split("\n"):
            if line == "":
                continue
            if line[0] == ',':
                csv = line.split(',')
                # soc += int(csv[1])
                if first_time:
                    first_time = False
                    # print(f"CBS-PC: SoC = {csv[1]}, Time = {csv[2]}")
                total_time += float(csv[2])
            else:
                if line[0:5] == "Agent":
                    # print(line)
                    agent = int(line[6])
                    line = line.split(": ")[1]
                    # print(line)
                    end_time = int(line.split("->")[-2].split('@')[1])
                    end_time = min(end_time, min_time)
                    # end_time = min_time
                    # print("og end_time ",int(line.split("->")[-2].split('@')[1]))
                    # print("og min_time ",min_time)
                    arr = line.split("->")[end_time].split("@")[0][1:-1].split(", ")
                    # print(arr)
                    tup = (int(arr[1]), int(arr[0]))
                    if map[agent] in need_to_change_goal or tup == goals[agent][1]:
                        number_of_goals[map[agent]] += 1

                        if goals[agent][2:] == []:
                            finished.append(map[agent])
                            goals[agent] = []
                        else:
                            goals[agent] = goals[agent][1:]
                    else:
                        # print(goals)
                        # print(agent)
                        # print(f"{agent=}, {number_of_goals[agent]=}, {goals[agent]=}")
                        # if goals[agent][min(number_of_goals[agent] + 1, len(goals[agent])-1)] != tup:
                        if map[agent] not in do_not_move:
                            goals[agent][0] = tup
                            
                else:
                    continue
        goals = [x for x in goals if x != []]
    # print(soc, total_time)
    print(f"Baseline: SoC = {soc}, Time = {round(total_time,4)}")


# 
def write_file(list_of_lists, tuples_list=None):
    with open("goal_seq.txt", "w") as file:
        # Write the length of the outer list
        file.write(f"{len(list_of_lists)}\n")

        for inner_list in list_of_lists:
            # Write the length of the inner list
            line = f"{len(inner_list)-1}"
            # Flatten the tuples and join elements with tabs
            for tup in inner_list:
                line += "\t" + "\t".join(map(str, tup))
            # Write the line to the file
            file.write(line + "\n")
        if tuples_list != None:
            file.write("temporal cons:\n")
            # Write each tuple on a new line, with elements separated by tabs
            for t in tuples_list:
                line = "\t".join(map(str, t))
                file.write(line + "\n")
