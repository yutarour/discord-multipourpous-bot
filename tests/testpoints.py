import json
   
# JSON data:
x = '{"500150174925193246": [{"points": 101}]}'
  
# python object to be appended
y = {"pin":110096}
  
# parsing JSON string:
z = json.loads(x)
   
# appending the data
z.update(y)
  
# the result is a JSON string:
print(json.dumps(z)) 