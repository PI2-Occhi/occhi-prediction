import json

def build_json(command, right_eye, left_eye):
  commands_json = {
    'forward': command == 'START MOVEMENT',
    'backward': command == 'REVERSE MOVEMENT',
    'left': right_eye == left_eye == 'Left',
    'right': right_eye == left_eye == 'Right',
    'stop': command == 'STOP MOVEMENT',
    'turn': command == '180 DEGRESS MOVEMENT',
  }
  
  return json.dumps(commands_json)