import re

callsign_pattern = re.compile(r'^[a-zA-Z]{1,2}\d[a-zA-Z]{1,3}$')

def is_valid_callsign(callsign):
    return bool(callsign_pattern.match(callsign))

# Example usage:
callsign = 'NL2MVV'
if is_valid_callsign(callsign):
    print(f"The callsign {callsign} is valid.")
else:
    print(f"The callsign {callsign} is not valid.")