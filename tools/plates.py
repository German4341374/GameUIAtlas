"""Lay out the four inspection screens as portable SVG, with embedded studio renders."""
import base64
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
W, H = 1280, 760
SERIF, SANS, MONO = 'Georgia', 'Arial', 'Consolas'


def rect(x,y,w,h,fill,r=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'


def path(d,c,w=1):
    return f'<path d="{d}" stroke="{c}" stroke-width="{w}" fill="none"/>'


def text(x,y,s,size,color,font=SANS,weight=400,spacing=0):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{spacing}" fill="{color}">{escape(s)}</text>')


def photo(key,x,y,w,h):
    data=(ROOT/'studies'/key/'model'/'studio.png').read_bytes()
    encoded=base64.b64encode(data).decode('ascii')
    return (f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" '
            f'xlink:href="data:image/png;base64,{encoded}"/>')


def apex():
    bg,ink,dim,rule,lime='#18171C','#FAF4E6','#C1BFC2','#5E5C62','#CDF595'
    out=[rect(0,0,W,H,bg),text(38,54,'APEX POST',34,ink,SANS,700,-1),
         text(865,50,'DEPOT 03     /     PIT LANE     /     17',16,dim,MONO),
         path('M38 72H1242',rule),photo('apex',36,109,782,550),
         text(42,98,'01     VEHICLE INSPECTION',13,dim,MONO,400,2),
         text(851,143,'HARBOR RUN  /  PM SHIFT',15,lime,MONO),
         text(846,223,'Parcel',79,ink,SANS,700,-3),text(846,301,'Runner 17',74,ink,SANS,700,-3),
         path('M852 332H1240',rule),text(852,373,'Cargo bay',21,ink),text(852,407,'Both straps locked.',28,lime),
         text(852,463,'Front tires',21,ink),text(852,499,'Soft compound fitted.',27,ink),
         text(852,551,'No charge to inspect the car.',18,dim),rect(852,594,389,62,lime),
         text(886,634,'RETURN TO DISPATCH',23,bg,MONO,700),
         path('M38 687H1242',rule),text(38,728,'FLEET  /  017',18,ink,MONO),
         text(850,728,'NEXT STOP   →   HARBOR CIRCUIT',17,dim,MONO)]
    return 'Parcel Runner 17',out


def vesper():
    bg,ink,dim,metal='#291F25','#F4E6CF','#D2BAA7','#B89363'
    out=[rect(0,0,W,H,bg),path('M28 28H1252V732H28Z',metal),
         text(57,77,'Vesper Abbey',32,ink,SERIF),text(965,73,'VESTRY   ·   FOLIO VIII',15,dim,MONO),
         path('M56 99H1224',metal),photo('vesper',485,116,734,516),
         text(60,174,'A RELIC FOR THE WEST TOWER',14,metal,MONO,700,2),
         text(55,257,'The vigil',76,ink,SERIF),text(55,340,'censer',83,ink,SERIF),
         text(59,400,'“Keep it lit until the last bell.”',26,dim,SERIF),
         path('M59 437H434',metal),text(60,483,'Material',17,metal),
         text(60,517,'Cast bronze, brass chain',26,ink,SERIF),
         text(60,567,'Quest',17,metal),text(60,600,'Light the west brazier',25,ink,SERIF),
         path('M56 654H1224',metal),text(59,703,'VIII   /   SACRISTY INVENTORY',16,dim,MONO),
         text(905,703,'Carry the censer   →',29,ink,SERIF)]
    return 'The vigil censer',out


def relay():
    bg,ink,mut,orange,rule='#DEE0CC','#162824','#40564B','#F6BF6B','#91A495'
    out=[rect(0,0,W,H,bg),rect(0,0,W,72,ink),text(34,48,'RELAY NINE   /   FIELD SERVICE',28,bg,MONO,700),
         text(1011,45,'CASE 09    ·    VHF',16,orange,MONO),text(33,141,'Channel recovery',57,ink,SANS,700,-2),
         text(845,131,'PRIMARY LINK     /     NO CARRIER',16,mut,MONO),
         photo('relay',35,169,690,486),rect(751,168,493,477,ink),
         text(780,214,'RX–09     /     FRONT PANEL',18,orange,MONO),
         path('M780 234H1212',rule),text(778,276,'Standby frequency',20,bg),
         text(776,345,'146.520',66,bg,MONO,700),text(1093,345,'MHz',23,orange,MONO),
         text(780,404,'PACKETS HELD',16,bg,MONO),text(1085,404,'18 / 18',24,orange,MONO),
         text(780,454,'BACKUP CARRIER',16,bg,MONO),text(1085,454,'READY',24,orange,MONO),
         path('M780 483H1212',rule),rect(780,521,430,68,orange),
         text(802,565,'SWITCH TO BACKUP',26,ink,MONO,700),
         path('M34 672H1245',mut),text(36,716,'LOG 019    /    RIDGE STATION',18,mut,MONO),
         text(753,716,'The packet cache survives a channel change.',20,ink)]
    return 'RX-09 channel recovery',out


def pollen():
    paper,ink,berry,rule='#F9EFD6','#324538','#953F40','#B8A782'
    out=[rect(0,0,W,H,paper),rect(0,0,22,H,'#557C64'),text(61,67,'Pip’s orchard notebook',36,ink,SERIF),
         text(1017,62,'DAY 03  /  KITCHEN',17,berry,MONO),path('M62 88H1224',rule),
         text(60,151,'A press for sunpears',54,ink,SERIF),photo('pollen',60,181,666,469),
         text(772,219,'RECIPE     08',16,berry,MONO,700,2),text(769,280,'Before you turn',40,ink,SERIF),
         text(769,330,'the handle…',40,ink,SERIF)]
    for i,(mark,title,sub) in enumerate([('1','Fill the basket','3 ripe sunpears'),('2','Set the cup','Under the little green spout')]):
        y=390+85*i
        out += [rect(773,y-22,30,30,'#D9DEBC',14),text(782,y,mark,19,ink,SERIF),
                text(818,y,title,23,ink,SANS,700),text(818,y+30,sub,19,ink)]
    out += [rect(772,562,429,66,ink,33),text(839,605,'Press the pears',28,paper,SERIF),
            path('M62 673H1224',rule),text(62,719,'Fig. 8   ·   Beech basket and cast frame',22,ink,SERIF),
            text(1065,714,'PIP & POLLEN',15,berry,MONO)]
    return 'Orchard press',out


if __name__=='__main__':
    for key,build in [('apex',apex),('vesper',vesper),('relay',relay),('pollen',pollen)]:
        title,items=build()
        (ROOT/'studies'/key/'detail.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"><title>{escape(title)}</title>\n'
            + '\n'.join(items)+'\n</svg>\n', encoding='utf-8')
