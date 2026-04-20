import datetime


def bubble_sort(a_list):
    """ Returns an ordered list
    
        Method that receives a list and returns its ordering
        using the bubble technique 

    """
    for i in range(len(a_list)-1, 0, -1):
        for j in range(i):
            if a_list[j] > a_list[j+1]:
                temp = a_list[j]
                a_list[j] = a_list[j+1]
                a_list[j+1] = temp
    return a_list


def bubble_sort_nested(a_list):
    """ Returns an ordered list
        
        Method that receives a list and returns its ordering
        using the bubble technique (only for lists containing nested data)

    """
    for index, item in enumerate(a_list):
        if a_list[index][0] == '':
            temp = a_list[index]
            del a_list[index]
            a_list.append(temp)
        else:
            continue

    for i in range(len(a_list)-1, 0, -1):
        for j in range(i):
            if type(a_list[j][0]) is str:
                break
            elif type(a_list[j][0]) is list:
                if type(a_list[j+1][0]) is list:
                    if a_list[j][0][0] > a_list[j+1][0][0]:
                        temp = a_list[j]
                        a_list[j] = a_list[j+1]
                        a_list[j+1] = temp
                elif type(a_list[j+1][0]) is datetime:
                    if a_list[j][0][0] > a_list[j+1][0]:
                        temp = a_list[j]
                        a_list[j] = a_list[j+1]
                        a_list[j+1] = temp
                else:
                    break
            elif type(a_list[j][0]) is datetime:
                if type(a_list[j+1][0]) is list:
                    if a_list[j][0] > a_list[j+1][0][0]:
                        temp = a_list[j]
                        a_list[j] = a_list[j+1]
                        a_list[j+1] = temp
                elif type(a_list[j+1][0]) is datetime:
                    if a_list[j][0] > a_list[j+1][0]:
                        temp = a_list[j]
                        a_list[j] = a_list[j+1]
                        a_list[j+1] = temp
                else:
                    break
    return a_list
