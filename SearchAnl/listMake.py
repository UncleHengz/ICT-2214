def list_Maker(myFilePath):  # use this function to append links in a file to an array
    sites_array= []
    with open(myFilePath) as my_file:
        for line in my_file:
            sites_array.append(line)
    return sites_array