# f = open('demo.txt', mode='a')
# f = open('demo.txt', mode="r")
# contents = f.read()
# f.write('Add content!\n')
# contents = f.read()
# file_content =  f.readlines()
# f.close()

# print(f.readline())
# print(f.readline())
# print(f.readline())
# print(f.readline())
# print(f.readline())
# print(f.readline())
# print(f.readline())

# line = f.readline()

# while line:
#     print(line)
#     line = f.readline()

# f.close()

# for line in file_content:
#     print(line[:-1])

# print(contents)
# user_input = input('Please enter input: ')

with open('demo.txt', mode='w') as f:
    # line = f.readline()
    # while line:
    #     print(line)
    #     line = f.readline()
    f.write('Testing if this closes...')
    f.write('\n')

user_input =  input('Testing: ')
print('Done!')