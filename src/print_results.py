import json

f = open('cnewsmatin.json', 'r')
data = json.load(f)
true_count = 0
false_count = 0

print('Confirmed True')
for element in data:
    if element['is_confirmed'] == True:
        true_count = true_count + 1 
        print(element['url'])
print('True: ' + str(true_count))

print('Confirmed False')
for element in data:
    if element['is_confirmed'] == False:
        false_count = false_count + 1 
        print(element['url'])
print('False: ' + str(false_count))
