files = [
    "application",
    "audio",
    "font",
    "haptics",
    "image",
    "message",
    "model",
    "multipart",
    "text",
    "video"
]

with open('C:\\Projects\\eark\\eark-validator\\eark_validator\\ipxml\\resources\\vocabs\\IANA.txt', 'w') as iana:
    for file_name in files:
        full_name = "C:\\Users\\Z6DOC\\Downloads\\" + file_name + ".csv"
        with open(full_name, 'r') as file:
            for line in file:
                start = line.find(',') + 1
                end = line.find(',', start)
                vocabulary_item = line[start:end]
                iana.write(vocabulary_item + '\n')
                #print(vocabulary_item)

