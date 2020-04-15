
# This dictionary specifies information for different aux channels. Per channel it lists the channel number, the range (minimum,maximum) value encoded, the number of encoded values (values will be automatically recoded to ordinal values 0,1,2 etc) and whether to 'recode' these identified ordinal values to new values. This allows the data class to clean up the signal considerably. The frame, stimulus and position channels are reated in a special way.

auxchannels = {
    "shutter":    {"nr": 0,  "range": [0,5], "nvalues": 2},
    "frame":      {"nr": 3,  "range": [0,5], "nvalues": None},
    "task":       {"nr": 7,  "range": [0,5], "nvalues": 10},
    "stimulus":   {"nr": 8,  "range": [0,5], "nvalues": None},
    "leftvalve":  {"nr": 9,  "range": [0,5], "nvalues": 2},
    "rightvalve": {"nr": 10, "range": [0,5], "nvalues": 2},
    "leftlick":   {"nr": 11, "range": [0,5], "nvalues": 2, "recode": [1,0]},
    "rightlick":  {"nr": 12, "range": [0,5], "nvalues": 2, "recode": [1,0]},
    "position":   {"nr": 14, "range": [0,5], "nvalues": None},
    "righteye":   {"nr": 16, "range": [0,5], "nvalues": 2, "recode": [0,1]},
    "lefteye":    {"nr": 17, "range": [0,5], "nvalues": 2, "recode": [1,0]}
    }
