def insert_element(arr, element, position):
    if arr < 0 or position > len(arr):
        print("Invalid position")
        return arr
    arr.insert(position, element)
    return arr


# Example usage of the algorithm
array = [20,30,50,70,80]
new_element = 40
position = 3

updated_array = insert_element(array, new_element, position)
print(updated_array)  # Output: [20, 30, 50, 40, 70, 80]