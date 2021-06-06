#!/usr/bin/env python

barNames = { "m" : "M",
              "w_m" : "W\\textbar M",
              "w" : "W",
              "w_g" : "W\\textbar G",
              "w_m_g" : "W\\textbar M\\textbar G",
              "m_g" : "M\\textbar G" }
           

barShortcuts = {"m" : "\\mGr",
                "w_m" : "\\wmGr",
                "w": "\\wGr",
                "w_g": "\\wgGr",
                "w_m_g": "\\wmgGr",
                "m_g" : "\\mgGr" }
                
def getTupleKey(wTitle, mTitle, gTitle):
    pKeys = [ ]
    if wTitle != "None":
        pKeys.append("w")
            
    if mTitle != "None":
        pKeys.append("m")
            
    if gTitle != "None":
        pKeys.append("g")
        
    return "_".join(pKeys)
    
def niceGroupName(group):
    return barNames[group]  
           
