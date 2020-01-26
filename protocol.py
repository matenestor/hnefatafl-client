OP_SOH = "{"                # start of header
OP_EOT = "}"                # end of transmission
OP_SEP = ","                # separator
OP_INI = ":"                # initializer of data
OP_PING = ">"               # enquiry
OP_PONG = "<"               # acknowledge

OP_CHAT = "ch"              # chat

CC_CONN = "c"               # connect
CC_READY = "rd"             # ready
CC_MOVE = "m"               # move
CC_LEAV = "l"               # leave game

SC_RESP_CONN = "rc"         # response connect
SC_RESP_RECN = "rr"         # response reconnect
SC_RESP_LEAVE = "rl"        # response leave
SC_IN_LOBBY = "il"          # client moved to lobby
SC_IN_GAME = "ig"           # client moved to game
SC_MV_VALID = "mv"          # valid move
SC_TURN_YOU = "ty"          # your's turn
SC_TURN_OPN = "to"          # opponent's turn
SC_PLAYFIELD = "pf"         # playfield
SC_GO_WIN = "gw"            # game over win
SC_GO_LOSS = "gl"           # game over loss
SC_OPN_NAME = "on"          # opponent's name
SC_OPN_MOVE = "om"          # opponent's move
SC_OPN_LEAVE = "ol"         # opponent left the game
SC_OPN_LOST = "os"          # opponent lost
SC_OPN_DISC = "od"          # opponent disconnected
SC_OPN_RECN = "or"          # opponent reconnected
SC_OPN_GONE = "og"          # opponent is gone -- instance erased
SC_MANY_CLNT = "t"          # too many clients message
SC_NICK_USED = "u"          # nick is already used
SC_KICK = "k"               # kick client
SC_SHDW = "s"               # server shutdown

RGX_VALID_FORMAT = "(?:\{(?:<|>|rc|rr,il|rr,ig,(?:ty|to),on:\w{3,20},pf:\d{100}|rl|il|ig,(?:ty|to),on:\w{3,20}|mv|gw|gl|om:\d{8}|ol|od|or|og|t|u|k|s|ch:[\w\s.!?]{1,100})\})+"
RGX_VALID_DATA =           "<|>|rc|rr,il|rr,ig,(?:ty|to),on:\w{3,20},pf:\d{100}|rl|il|ig,(?:ty|to),on:\w{3,20}|mv|gw|gl|om:\d{8}|ol|od|or|og|t|u|k|s|ch:[\w\s.!?]{1,100}"

# server regex -- valid format: (?:\{(?:<|>|c:\w{3,20}|rd|m:\d{8}|l|ok|ch:[\w\s.!?]{1,100})\})+
# server regex -- valid data:           <|>|c:\w{3,20}|rd|m:\d{8}|l|ok|ch:[\w\s.!?]{1,100}    ..in curly brackets
