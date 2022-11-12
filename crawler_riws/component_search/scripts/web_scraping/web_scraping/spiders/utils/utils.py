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
    'THERMALTAKE'
]

def match_brand(compo_brand: str):
    for brand in BRANDS:
        if brand in compo_brand.upper():
            return brand