BRANDS = [
    'AMD',
    'INTEL',
    'ASUS',
    'GIGABYTE',
    'MSI',
    'NZXT',
    'ACER',
    'ADATA',
    'CORSAIR',
    'CRUCIAL',
    'GOODRAM',
    'KINGSTON',
    'TEAMGROUP',
    'THERMALTAKE',
    'MARS GAMING',
    'NOX HUMMER',
    'BE QUIET!',
    'LIAN LI',
    'AEROCOOL',
    'AQUA-COMPUTER',
    'COOLER MASTER',
    'DEEPCOOL',
    'NOCTUA',
    'NOX',
    'SILVERSTONE',
    'DEMCIFLEX',
    'ARTIC SILVER',
    'ARTIC COOLING',
    '3GO',
    'ANTEC',
    'BIOSTAR',
    'EVGA',
    'RASPBERRY',
    'HIKVISION',
    'PNY',
    'HYPERX',
    'SAMSUNG',
    'SANDISK',
    'SEAGATE',
    'SILICON POWER',
    'TOSHIBA',
    'D-LINK',
    'EDIMAX',
    'NANOCABLE',
    'LOGILINK',
    'TP-LINK',
    'SYNOLOGY',
    'QNAP',
    'CONCEPTRONIC',
    'APPROX',
    'CRATIVE',
    'DELOCK',
    'EWENT',
    'KEEP OUT',
    'STARTECH.COM'
]

def match_brand(compo_brand: str):
    for brand in BRANDS:
        if brand in compo_brand.upper():
            return brand