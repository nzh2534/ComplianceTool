lyst = [1, 2, 3, 4, 5, 1, 2, 3, 4, 6, 7, 1, 2, 3, 8, 9, 10, 11, 12, 1, 2]
lyst_2 = [1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 8, 9, 8, 9, 10, 11, 12, 1, 2, 3] #accidentaly gets the first 8 & 9

def sub_header_fxn(lyst):
    new_list = [0]
    new_list_values_check = [lyst[0]]
    max_value = lyst.index(max(lyst))
    index = 1
    for i in lyst[1:]:
        if i > lyst[index - 1]:
            new_list.append(lyst.index(i))
            new_list_values_check.append(i)
            index += 1
        else:
            break

    old_lyst = list(reversed(lyst[len(new_list):lyst.index(max(lyst)) + 1]))

    new_list_ending = [max_value]
    index = 1
    for i in old_lyst[1:]:
        if i < old_lyst[index -1] and i > old_lyst[index + 1] and i == old_lyst[index - 1] - 1 and i not in new_list_values_check:
            new_list_ending.append(lyst.index(i))
            index += 1
        else:
            break

    index = lyst[new_list[-1]] + 1
    missing_integers = []
    while index < lyst[new_list_ending[-1]]:
        missing_integers.append(index)
        index += 1

    starting_index = new_list[-1] + 1
    missing_list = lyst[new_list[-1] + 1 : new_list_ending[-1]]
    for i in missing_integers:
        new_list.append(missing_list.index(i) + starting_index)

    new_list = new_list + list(reversed(new_list_ending))

    return new_list

