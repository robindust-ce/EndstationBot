help_message = "*Admin Commands* (*SV group only*): %0A %0A" + \
               "@EndstationBot help - display this help message %0A %0A" + \
               "@EndstationBot forceopen - force the basement status to open %0A %0A" + \
               "@EndstationBot forceclose - force the basement status to closed %0A %0A" + \
               'Pass the keyword "silent" so that changes in the basement status will not be broadcasted %0A %0A' + \
               'Example "@EndstationBot forceclose silent" %0A %0A' + \
               "*General Commands*: %0A %0A" + \
               "@EndstationBot basementstatus - returns the basement status (open/closed) %0A %0A" + \
               "@EndstationBot basementinfo - returns basic information about Endstation %0A %0A" + \
               "Messages in the Wohnheim Group containing keywords related to the basement will be answered with the basement status %0A %0A" + \
               "General commands have a cooldown period. Only general commands but not admin commands will be ignored during the cooldown period %0A %0A" + \
               "All messages directed towards EndstationBot need to be longer than 5 and shorter than 120 characters"


baseinfo_message = 'Hello, I am *EndstationBot*. You can use me to query wether the community room (\"Endstation\") is currently opened. %0A' + \
                   'You can find \"Endstation\" in the basement of house 134. The entrance is right next to the elevator. You can also enter through the bicycle basement. %0A %0A' + \
                   "\"Endstation\" has a bar, couches, a billiard table, foosball tables, a community printer and can be used for study sessions. %0A" + \
                   "All dorm residents and friends are welcome! \U0001F37B"