from typing import (
    Optional,
)


__all__ = (
    'Emoji',
    'emoji_width',
)


emojis: dict[Optional[str | int], str] = {
    None: '<:B:987480731766902844>',
    '🔴': '<:B:980206144754700351>',
    '🟥': '<:B:980206144855343114>',
    '🟠': '<:B:980206144826007552>',
    '🟧': '<:B:980206144666624050>',
    '🟡': '<:B:980206144914063471>',
    '🟨': '<:B:980206144880513054>',
    '🟢': '<:B:980206144620486716>',
    '🟩': '<:B:980206144524009472>',
    '🔵': '<:B:980206144482078781>',
    '🟦': '<:B:980206144612102227>',
    '🟣': '<:B:980206144708550697>',
    '🟪': '<:B:980206144737910874>',
    '🟤': '<:B:980206144578551849>',
    '🟫': '<:B:980206144578551909>',
    '⚪': '<:B:980206144855371826>',
    '⬜': '<:B:980206144754692146>',
    '⚫': '<:B:1026624376520577094>',
    '⬛': '<:B:1026624377271361577>',
    0: '<:B:994581962146713702>',
    '0': '<:B:994581962146713702>',
    1: '<:B:980206144725344256>',
    '1': '<:B:980206144725344256>',
    2: '<:B:980206144482054144>',
    '2': '<:B:980206144482054144>',
    3: '<:B:980206144511418399>',
    '3': '<:B:980206144511418399>',
    4: '<:B:980206144515612793>',
    '4': '<:B:980206144515612793>',
    5: '<:B:980206144570134668>',
    '5': '<:B:980206144570134668>',
    6: '<:B:980206144536580157>',
    '6': '<:B:980206144536580157>',
    7: '<:B:980206144658239508>',
    '7': '<:B:980206144658239508>',
    8: '<:B:980206144742101023>',
    '8': '<:B:980206144742101023>',
    9: '<:B:980206144410759261>',
    '9': '<:B:980206144410759261>',
    10: '<:B:980206144733712404>',
    '10': '<:B:980206144733712404>',
    11: '<:B:980206144691769354>',
    '11': '<:B:980206144691769354>',
    12: '<:B:980206144662437928>',
    '12': '<:B:980206144662437928>',
    13: '<:B:980206144800817202>',
    '13': '<:B:980206144800817202>',
    14: '<:B:980206144406564876>',
    '14': '<:B:980206144406564876>',
    15: '<:B:980206144863764490>',
    '15': '<:B:980206144863764490>',
    16: '<:B:980206144704364554>',
    '16': '<:B:980206144704364554>',
    17: '<:B:980206144758882304>',
    '17': '<:B:980206144758882304>',
    18: '<:B:994577671793168465>',
    '18': '<:B:994577671793168465>',
    19: '<:B:994577672971767848>',
    '19': '<:B:994577672971767848>',
    20: '<:B:1002027370972184576>',
    '20': '<:B:1002027370972184576>',
    21: '<:B:1002027372285001768>',
    '21': '<:B:1002027372285001768>',
    22: '<:B:1002027373589438494>',
    '22': '<:B:1002027373589438494>',
    23: '<:B:1002027375036485672>',
    '23': '<:B:1002027375036485672>',
    24: '<:B:1002027375866945597>',
    '24': '<:B:1002027375866945597>',
    25: '<:B:1002027377217519677>',
    '25': '<:B:1002027377217519677>',
    26: '<:B:1002027378945568808>',
    '26': '<:B:1002027378945568808>',
    'a': '<:B:980206144704376892>',
    'A': '<:B:980206144704376892>',
    'b': '<:B:980206144716947476>',
    'B': '<:B:980206144716947476>',
    'c': '<:B:980206144834387988>',
    'C': '<:B:980206144834387988>',
    'd': '<:B:980206144133951530>',
    'D': '<:B:980206144133951530>',
    'e': '<:B:980206144754679858>',
    'E': '<:B:980206144754679858>',
    'f': '<:B:980206144737902604>',
    'F': '<:B:980206144737902604>',
    'g': '<:B:980206144708558848>',
    'G': '<:B:980206144708558848>',
    'h': '<:B:980206144482082867>',
    'H': '<:B:980206144482082867>',
    'i': '<:B:980206144884707348>',
    'I': '<:B:980206144884707348>',
    'j': '<:B:980206144859549736>',
    'J': '<:B:980206144859549736>',
    'k': '<:B:980206144331059271>',
    'K': '<:B:980206144331059271>',
    'l': '<:B:980206144888926228>',
    'L': '<:B:980206144888926228>',
    'm': '<:B:980206144876314674>',
    'M': '<:B:980206144876314674>',
    'n': '<:B:980206144943456297>',
    'N': '<:B:980206144943456297>',
    'o': '<:B:980206144750514176>',
    'O': '<:B:980206144750514176>',
    'p': '<:B:980206144876314704>',
    'P': '<:B:980206144876314704>',
    'q': '<:B:980206144712765440>',
    'Q': '<:B:980206144712765440>',
    'r': '<:B:1001180153117954193>',
    'R': '<:B:1001180153117954193>',
    's': '<:B:1001180154669846548>',
    'S': '<:B:1001180154669846548>',
    't': '<:B:1001180156129464380>',
    'T': '<:B:1001180156129464380>',
    'u': '<:B:1001180157270306886>',
    'U': '<:B:1001180157270306886>',
    'v': '<:B:1001180158130147379>',
    'V': '<:B:1001180158130147379>',
    'w': '<:B:1001180159988211893>',
    'W': '<:B:1001180159988211893>',
    'x': '<:B:1001180161443643582>',
    'X': '<:B:1001180161443643582>',
    'y': '<:B:1001180162735485038>',
    'Y': '<:B:1001180162735485038>',
    'z': '<:B:1001180164245426226>',
    'Z': '<:B:1001180164245426226>',
    '⬇️': '<:B:980221350692134942>',
    '⬅️': '<:B:980221350696341525>',
    '↙️': '<:B:980221350750871642>',
    '↘️': '<:B:980221350570496040>',
    '➡️': '<:B:980221350662787192>',
    '⬆️': '<:B:980221350595690536>',
    '↖️': '<:B:980221350666965053>',
    '↗️': '<:B:980221350583087134>',
    '📘': '<:B:980221350608240640>',
    '💥': '<:B:980221350591496222>',
    '💡': '<:B:980221350591479818>',
    '🚅': '<:B:980221350767644702>',
    '👏': '<:B:980221350637600828>',
    '🤡': '<:B:980221350654410772>',
    '😢': '<:B:980221351010898030>',
    '🎯': '<:B:980221350713118730>',
    '🗂️': '<:B:980221350750859304>',
    '🌎': '<:B:980221350692147200>',
    '🧐': '<:B:980221350801207296>',
    '🌫️': '<:B:980221350771818517>',
    '🎲': '<:B:980221350696325151>',
    '💎': '<:B:980221350788628490>',
    '❔': '<:B:980221350893457488>',
    '🔒': '<:B:980221350822150174>',
    '💰': '<:B:980221350335610931>',
    '🅾️': '<:B:980221350750851132>',
    '🅿': '<:B:980221350784426004>',
    '👇': '<:B:980221350398545992>',
    '👈': '<:B:980221350721519686>',
    '👉': '<:B:980221350734086174>',
    '👆': '<:B:980221350830555196>',
    '👊': '<:B:980221350759260160>',
    '📌': '<:B:980221350641795143>',
    '❓': '<:B:980221350423691276>',
    '🚀': '<:B:980221350939594783>',
    '🚨': '<:B:980221350977355796>',
    '📜': '<:B:980221351069618196>',
    '💀': '<:B:980221350847348766>',
    '🔹': '<:B:980221350457274420>',
    '🔸': '<:B:980221350826348554>',
    '😭': '<:B:980221350755049554>',
    '⭐': '<:B:980221350838943785>',
    '💦': '<:B:980221350838943827>',
    '🎉': '<:B:980221350704742464>',
    '👍': '<:B:980221350922813501>',
    '🎩': '<:B:980221350985744425>',
    '🚩': '<:B:980221350868287599>',
    '🏆': '<:B:980221350805389312>',
    '🎮': '<:B:980221351132557322>',
    '❌': '<:B:980221350650195980>',
    '🔃': '<:B:985277625238970418>',
    '🔄': '<:B:985277626753105920>',
    '🃏': '<:B:985277627898167316>',
    '🚙': '<:B:985277629315809320>',
    '👥': '<:B:985277630762844160>',
    '♣️': '<:B:985277631769501706>',
    'clubs_background': '<:B:985277633128460379>',
    '⚔️': '<:B:985277634294448128>',
    '♦️': '<:B:985277635405971568>',
    'diamonds_background': '<:B:985277636911693844>',
    'grey_circle': '<:B:985277638417477692>',
    'grey_square': '<:B:985277640413962280>',
    '♥️': '<:B:985277643547086917>',
    'hearts_background': '<:B:985277645619077232>',
    '🏠': '<:B:985277648194383902>',
    '🚔': '<:B:985277650543198218>',
    '🧧': '<:B:985277652640354345>',
    '♠️': '<:B:985277654250946661>',
    'spades_background': '<:B:985277655383429221>',
    '🛠️': '<:B:985277656427790356>',
    '🚆': '<:B:985277657925161031>',
    '👋': '<:B:985277659028271214>',
    '🆓': '<:B:1001182414225289218>',
    'correct': '<:B:1001180147954757642>',
    'correct_filled': '<:B:1001180149326291074>',
    'incorrect': '<:B:1001180150743978117>',
    'incorrect_filled': '<:B:1001180152077750342>',
    'green_1': '<:B:1008872178097332284>',
    'green_2': '<:B:1008872179213021246>',
    'green_3': '<:B:1008872180903329803>',
    'green_4': '<:B:1008872182602014870>',
    'green_5': '<:B:1008872184292327496>',
    'green_6': '<:B:1008872185663868978>',
    'green_7': '<:B:1008872187073134653>',
    'green_8': '<:B:1008872188633432134>',
    'green_9': '<:B:1008872190567010395>',
    'red_0': '<:B:1012519244493230142>',
    'red_1': '<:B:1008872269084377129>',
    'red_2': '<:B:1008872270892113970>',
    'red_3': '<:B:1008872272452395098>',
    'red_4': '<:B:1008872273769398283>',
    'red_5': '<:B:1008872275342278703>',
    'red_6': '<:B:1008872277129048155>',
    'red_7': '<:B:1008872278618022039>',
    'red_8': '<:B:1008872281143005226>',
    'red_9': '<:B:1008872282581643348>',
    'red_10': '<:B:1012519146086473749>',
    'red_11': '<:B:1012519147780968509>',
    'red_12': '<:B:1012519148779221053>',
    'red_13': '<:B:1012519150381445241>',
    'red_14': '<:B:1012519151811698759>',
    'red_15': '<:B:1012519152705093633>',
    'red_16': '<:B:1012519153862721597>',
    'red_17': '<:B:1012519155590766673>',
    'red_18': '<:B:1012519157125890068>',
    'red_19': '<:B:1012519158409334834>',
    'red_20': '<:B:1012519159709565049>',
    'red_21': '<:B:1012519160783306815>',
    'red_22': '<:B:1012519162431668266>',
    'red_23': '<:B:1012519164373643335>',
    'red_24': '<:B:1012519165728403506>',
    'red_25': '<:B:1012519246116425748>',
    'red_26': '<:B:1012519247517339648>',
    'grey_1': '<:B:1008882420055015514>',
    'grey_2': '<:B:1008882421896318976>',
    'grey_3': '<:B:1008882423284633691>',
    'grey_4': '<:B:1008882424387747840>',
    'grey_5': '<:B:1008882425457287198>',
    'grey_6': '<:B:1008882427650920469>',
    'grey_7': '<:B:1008882429047615558>',
    'grey_8': '<:B:1008882429920038934>',
    'grey_9': '<:B:1008882431388045365>',
    'transparent_1': '<:B:1008891627445690479>',
    'transparent_2': '<:B:1008891628959825972>',
    'transparent_3': '<:B:1008891630562062438>',
    'transparent_4': '<:B:1008891632046846022>',
    'transparent_5': '<:B:1008891633342873651>',
    'transparent_6': '<:B:1008891635209347152>',
    'transparent_7': '<:B:1008891636710899712>',
    'transparent_8': '<:B:1008891637969191022>',
    'transparent_9': '<:B:1008891639357517824>',
    '🥵': '<:B:1009628823014363176>',
    '🏓': '<:B:1009628824511721562>',
    '🥱': '<:B:1009628825774194790>',
    '🔥': '<:B:1010380773632774246>',
    'paddle_left': '<:B:1009628819180761098>',
    'paddle_right': '<:B:1009628817821794305>',
    'ball': '<:B:1009628820367757353>',
    '⏬': '<:B:1009910978936316066>',
    '⏫': '<:B:1009910980299464745>',
    '👞': '<:B:1009910981452906537>',
    'buttonstyle_blue_circle': '<:B:1010384030979600394>',
    'buttonstyle_blue_square': '<:B:1010384031654879243>',
    'buttonstyle_green_circle': '<:B:1010384032825090170>',
    'buttonstyle_green_square': '<:B:1010384034309877890>',
    'buttonstyle_red_circle': '<:B:1010384037875032065>',
    'buttonstyle_red_square': '<:B:1010384038923612171>',
    '💼': '<:B:1012499874756960376>',
    '🔓': '<:B:1012563007500460112>',
    '🍀': '<:B:1012566007317012500>',
    'red_a': '<:B:1012491107256504441>',
    'red_b': '<:B:1012491108686774362>',
    'red_c': '<:B:1012491109974421544>',
    'red_d': '<:B:1012491111555670086>',
    'red_e': '<:B:1012491121886253136>',
    'red_f': '<:B:1012491122666381333>',
    'red_g': '<:B:1012491124100829294>',
    'red_h': '<:B:1012491125937934406>',
    'red_i': '<:B:1012491127275921448>',
    'red_j': '<:B:1012491128509038653>',
    'red_k': '<:B:1012491129914138704>',
    'red_l': '<:B:1012491131445067806>',
    'red_m': '<:B:1012491132694974465>',
    'red_n': '<:B:1012491134129410048>',
    'red_o': '<:B:1012491135547080724>',
    'red_p': '<:B:1012491136771821598>',
    'red_q': '<:B:1012491137858146375>',
    'red_r': '<:B:1012491139540062279>',
    'red_s': '<:B:1012491141503004815>',
    'red_t': '<:B:1012491142857768990>',
    'red_u': '<:B:1012491144095084544>',
    'red_v': '<:B:1012491145223352410>',
    'red_w': '<:B:1012491146586505356>',
    'red_x': '<:B:1012491147974819912>',
    'red_y': '<:B:1012521488336818206>',
    'red_z': '<:B:1012521489444118660>',
    'blue_backspace': '<:B:1012568624734679140>',
    'red_backspace': '<:B:1012543254174126152>',
    'weird_blue_square': '<:B:1012568595504578590>',
    '💩': '<:B:1013144128223182878>',
    '🧱': '<:B:1013144124356042912>',
    '🪙': '<:B:1013144125572399155>',
    '👑': '<:B:1013144126780354651>',
    'chart_down': '<:B:1013154186352926750>',
    'chart_mid': '<:B:1013154188487823451>',
    'chart_up': '<:B:1013154189855162458>',
    'plus': '<:B:1018327929794596995>',
    'skip': '<:B:1018329111904653433>',
    'border_blue_0': '<:B:1019718696027037726>',
    'border_blue_1': '<:B:1019718697285337170>',
    'border_blue_2': '<:B:1019718698497486919>',
    'border_blue_3': '<:B:1019718699927748628>',
    'border_blue_4': '<:B:1019718701173461152>',
    'border_blue_5': '<:B:1019718702406565928>',
    'border_blue_6': '<:B:1019718703446757487>',
    'border_blue_7': '<:B:1019718705330012290>',
    'border_blue_8': '<:B:1019718707695587358>',
    'border_blue_9': '<:B:1019718709692088422>',
    'border_blue_10': '<:B:1023689503057133608>',
    'border_blue_11': '<:B:1023689504856473765>',
    'border_blue_12': '<:B:1023689506865553448>',
    'border_blue_13': '<:B:1023689508287414332>',
    'border_blue_arrows_clockwise': '<:B:1019718711051038902>',
    'border_blue_plus': '<:B:1019718712464506890>',
    'border_blue_skip': '<:B:1019718713546653747>',
    'border_green_0': '<:B:1019718715253731398>',
    'border_green_1': '<:B:1019718716495249482>',
    'border_green_2': '<:B:1019718717933891722>',
    'border_green_3': '<:B:1019718719376723988>',
    'border_green_4': '<:B:1019718720760856656>',
    'border_green_5': '<:B:1019718722254020648>',
    'border_green_6': '<:B:1019718723403268137>',
    'border_green_7': '<:B:1019718724577660950>',
    'border_green_8': '<:B:1019718727635308604>',
    'border_green_9': '<:B:1019718729677951038>',
    'border_green_arrows_clockwise': '<:B:1019718731900928060>',
    'border_green_plus': '<:B:1019718733498949633>',
    'border_green_skip': '<:B:1019718737592594625>',
    'border_red_0': '<:B:1019718739433893959>',
    'border_red_1': '<:B:1019718740838993930>',
    'border_red_2': '<:B:1019718741925306500>',
    'border_red_3': '<:B:1019718743703687230>',
    'border_red_4': '<:B:1019718745154916412>',
    'border_red_5': '<:B:1019718747331768330>',
    'border_red_6': '<:B:1019718749655416864>',
    'border_red_7': '<:B:1019718752515932271>',
    'border_red_8': '<:B:1019718858858307665>',
    'border_red_9': '<:B:1019718883936043048>',
    'border_red_10': '<:B:1023687647325073551>',
    'border_red_11': '<:B:1023687648738541578>',
    'border_red_12': '<:B:1023687650177208320>',
    'border_red_13': '<:B:1023687651443888282>',
    'border_red_arrows_clockwise': '<:B:1019718885148217424>',
    'border_red_plus': '<:B:1019718886511345744>',
    'border_red_skip': '<:B:1019718909802315946>',
    'border_yellow_0': '<:B:1019718911110955188>',
    'border_yellow_1': '<:B:1019718912700596356>',
    'border_yellow_2': '<:B:1019718913816272997>',
    'border_yellow_3': '<:B:1019718915171033170>',
    'border_yellow_4': '<:B:1019718916534177842>',
    'border_yellow_5': '<:B:1019718917796659350>',
    'border_yellow_6': '<:B:1019718918874599476>',
    'border_yellow_7': '<:B:1019718921378603028>',
    'border_yellow_8': '<:B:1019718923094069258>',
    'border_yellow_9': '<:B:1019718924255907862>',
    'border_yellow_10': '<:B:1023688192911736904>',
    'border_yellow_11': '<:B:1023688194253930556>',
    'border_yellow_12': '<:B:1023688195633840228>',
    'border_yellow_13': '<:B:1023688196971839579>',
    'border_yellow_arrows_clockwise': '<:B:1019718925354807357>',
    'border_yellow_plus': '<:B:1019718926902501386>',
    'border_yellow_skip': '<:B:1019718929402318958>',
    'border_purple_0': '<:B:1019721457678430268>',
    'border_purple_1': '<:B:1019721458794106880>',
    'border_purple_2': '<:B:1019721460077580359>',
    'border_purple_3': '<:B:1019721461281333271>',
    'border_purple_4': '<:B:1019721462518648923>',
    'border_purple_5': '<:B:1019721463885991976>',
    'border_purple_6': '<:B:1019721465391755295>',
    'border_purple_7': '<:B:1019721466729730118>',
    'border_purple_8': '<:B:1019721468097073162>',
    'border_purple_9': '<:B:1019721469384736798>',
    'border_purple_arrows_clockwise': '<:B:1019721470408138874>',
    'border_purple_plus': '<:B:1019721472106831992>',
    'border_purple_skip': '<:B:1019721473620987944>',
    'border_orange_0': '<:B:1023689767751270540>',
    'border_orange_1': '<:B:1023689769416413294>',
    'border_orange_2': '<:B:1023689771123478528>',
    'border_orange_3': '<:B:1023689772646023288>',
    'border_orange_4': '<:B:1023689774038528140>',
    'border_orange_5': '<:B:1024453457161228308>',
    'border_orange_6': '<:B:1024453458448896091>',
    'border_orange_7': '<:B:1023699677411016754>',
    'border_orange_8': '<:B:1023699678438633533>',
    'border_orange_9': '<:B:1023699680103772180>',
    'border_orange_10': '<:B:1023699681374634084>',
    'border_orange_11': '<:B:1023699683010416640>',
    'border_orange_12': '<:B:1023699684344205332>',
    'border_orange_13': '<:B:1023701155739615263>',
    'border_black_0': '<:B:1026624219792031754>',
    'border_black_1': '<:B:1026624220605714434>',
    'border_black_2': '<:B:1026624221994033323>',
    'border_black_3': '<:B:1026624223323627591>',
    'border_black_4': '<:B:1026624224472862780>',
    'border_black_5': '<:B:1026624225622118460>',
    'border_black_6': '<:B:1026624226700054528>',
    'border_black_7': '<:B:1026624227899621477>',
    'border_black_8': '<:B:1026624229136945182>',
    'border_black_9': '<:B:1026624230311350342>',
    'border_black_10': '<:B:1026624231141814376>',
    'border_black_11': '<:B:1026624232999899236>',
    'border_black_12': '<:B:1026624234253987922>',
    'border_black_13': '<:B:1026624235440971866>',
    'joker_black': '<:B:1026624236619579482>',
    'joker_blue': '<:B:1026622870811574303>',
    'joker_orange': '<:B:1026622872090837042>',
    'joker_red': '<:B:1026622873554657330>',
    'joker_yellow': '<:B:1026622875064606810>',
}


def Emoji(name: Optional[str | int]) -> str:
    if isinstance(name, str):
        name = name.replace(' ', '')
    return emojis[name]


emoji_width = '　    '
