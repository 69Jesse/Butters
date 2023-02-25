from utils import (
    _Position,
)

from enum import Enum


class Position(_Position, modulo=None): pass
AwayPosition = Position(-1, -1)


class Direction(Enum):
    right = Position.right
    down = Position.down
    left = Position.left
    up = Position.up

    def __int__(self):
        return {
            Direction.right: 0,
            Direction.down: 1,
            Direction.left: 2,
            Direction.up: 3,
        }[self]


STANDARD_LEVEL_LINES: list[str] = [
    '060606060606060606060606060626060628010101010106060101280601010101800106060101010606060601010106060601010101010101010606060601010101010101010606062801010606060101012806060101010606060601010106060606060606060606060606',
    '060606060606060606062606060101010101010106010106060106060101015506010106060106060606060106060606060102062806280106022806060101060106060606010106060101060101062806800106060101010101010101010106060606060606060606060606',
    '060606060606060606060606060101010128060606010606060106060606060601800106060106212801020601550106060101010101060606060606060106060654210606060606060126062801010606010106060101060201010606012806060606060606060606060606',
    '060606060606060606060606062601020106280155060606060101015406010106012806062806010153010206210606062106060606010101010106062806010153010606060606060101010106010101800106060601010106010101010606060606060606060606060606',
    '060606060106060601062806060180060101280601010106060652065206520652065206060101010106010101060106065201520126010601060106060106010601060606060106060101010601062806010106062806010601060106550106060606060606060106060106',
    '060605060606051406060506060101012801011401012806060126010101011401010105050101010101041454030306060112131319131501010106060114010101015401010105060114010101010601800106052814012801010601010106060614050606060506060506',
    '060606060606031406060606062801010101011801012806131313201313131502010106062801010303051401545406060606050101281701010106061213130106121519201313061426140106140401800106061419150106140101012406060101010106140606060606',
    '060506142801010602010128068024140112201313131913132013150314011801170106060101141315011424140106051201012801011413151313051420131313131505260514060101010101240111010614061913131313131305060514222806060606061413131315',
    '060606060606060614060606062201280606280414262806060106060606550118010106060101060606060114010106060128010101010114013706131313370601060605010506020514010301060101010106281101010101018001010106240512060606060606060606',
    '161601061405030101010305160601281413280101012806160601013714130155011213160654010101141301121616162601060106041419151602160101010106060101010106160551060606010101800106160601012806370101010106161301060606060606060606',
    '060603060606060606030606060101282401010101052806063201010101062804120106060606010606060112152006060101280101010105140106063201010602050106060106060126010606060106800106060101010101010101010106060606060606060606060606',
    '060606060606060606060606063201010101010101012806060606010606060201800106060101570101280601510106060101370106010601010106060101050606010305260506060106060101010101012806062837010157010101573206060606060606060606060606',
    '060606060606060606060606060101280106223701290106060157010305010151515106320101010101010101010132060101010101010101010106060157010506260606010106065201011101012806800106062801010501010106010106060606060606060606060606',
    '062606060606060606060606050905121313282401013203062812150414130157010106060114023701180101010606060114282201140101012806060114130112150101540103060101141315010101800106060101010101010101010106060606060606050505060606',
    '800101010101530101010132010106060601010106060601010628013206010601283706010101010106210601010106010101010601010106060606015701060101010101015706010106280101550628010106010606060606010106060626010101010101010101010101',
    '060380030606062806060606060322030627010101013206060309030505050101060106220101121313280201060106050805142417015301010128010122140814010254050101050905142214015301010106240128180114010201010106060606060606060606060606',
    '060606060606060303050129062401010132062801010101060103032803120101055537060101010112151301060106050905020118281801020602268022060114131501010128010201060101140101015701190606065201060101010101010124060101060606060606',
    '060606020606060303260303060128022801010101010132065701023201510101370101060101020101010303030303132013020101010606060606060101240101010101020128010101010101015701050905018001010101010101012201060606060606060606060606',
    '060101010502020502020206062857011001011128372206062401010522280501010106131319131313131313201313060101060606060101010106032201062606280157010103032832050905062401800103030101010101060101010103060606050606060605060606',
    '060305030503050305030503060101280101260101280106063201010101010101013206060101020209020102020106060101285301800153280106060101010501010105010106220101010154015401010122010101010101010101010101060606060606060606060606',
    '060606010106060602010106068055060603062806060602060606060606060106060606060606060606290606060606062801060601060606060606020606060601060606260628280606060206060606060601010606060606060606545406060506060606060101060606',
    '281724182417241824142814191513152015201519152015241426172418241724172480201519151915201520152013281724182418241724172414191520151915201520151915241824172417241828182414201520152015191519151915241724172918241724182414',
    '060206060206240602060206320101010101280101010132320101010157285701010132320101010101280101010132020101060605260506010102060151010112201301510106065101010114281401015106060101010114011401800106060606060101010101060606',
    '801022112210291122102811090508050805080509050805281022112210221122102211090508050905090508050905221122112210221022112210080508050905080509050805281122102210281022102211080509050805090509050926221122102211221022100101',
    '060606060606060606060606010101010101010101018006015703260328020201030106010132010101010101510106010103030301020228030106280132010101010101510106015703030332020232030106010101010101540101540106060606060101010128010106',
    '030105060606060606143722030111010180012801140128035505010101010101142013020102010106060101010101012801010606260601280128010101010606060601015101030303280106060101510101320101010101010153015701012428020101280101510101',
]
