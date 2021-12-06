# coding=UTF-8
from subprocess import Popen, PIPE
import sys, re, locale

# Lista över produkter/kategorier som ska räknas som öl
list_Ol = [
"Öl",
"pÖl",
]

# Lista över produkter/kategorier som ska räknas som cider
list_Cider = [
"PCider 2019",
"Cider",
"Cidraie original",
"pCider",
"Vikbo Cider Rabarber",
"Crush",
"Somersby Pear",
"Sommersby Secco",
"Vikbo Cider Rabarber",
"Xide Kiwi Cucumber",
"Bulmers Zesty Blood orange",
]

# Lista över produkter/kategorier som ska räknas som sprit
list_Sprit = [
"Sprit",
]

# Lista över produkter/kategorier som ska räknas som vin
list_Vin = [
"Vin",
"Bubbel",
"Aniara",
"Freixenet Cava (glas)",
"Freixenet Cava (hel flaska)",
"Jacob’s Creek Chardonnay",
"Prosecco FLASKA",
"Les Oliviers Rosé (ett glas)",
"Les Oliviers Rosé (hel flaska)",
"Sun Gate Chardonnay (glas)",
"Sun Gate Chardonnay (hel flaska)",
"Jacob’s Creek Chardonnay Bubbel",
]

# Lista över produkter/kategorier som ska räknas som alkoholfritt
list_Alkfritt = [
"Alkfritt",
"Läsk",
"Pop Art",
"Drycker",
"Alkfri drink",
]

# Lista över produkter/kategorier som ska räknas som mat
list_Mat = [
"Mat",
"Billys Pan Pizza",
]

def main():
    locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')
    inp = ""
    for i in range(1,len(sys.argv)):
        p = Popen(['pdftotext', '-layout', '-nopgbrk', sys.argv[i], '-'], stdout=PIPE)
        out, _ = p.communicate(None)
        out = out.decode(encoding = 'UTF-8')
        if not 'date' in locals():
            date = getDate(out.split('\n'))
        if date and date == getDate(out.split('\n')):
            inp += out
        else:
            if date:
                print("DATE ERROR: The reports don't have the same date! Error on file",'"{0}"'.format(sys.argv[i]))
                return
    
    # Debug-print
    print(inp)

    lines = inp.split('\n')
    card, cash = getPayments(lines)
    discounts = getDiscounts(lines)
    categorys = getProductSales(lines)

    # Debug-prints
    print(card)
    print(cash)
    print(discounts)
    print(categorys)

    if sum(categorys.values())+ discounts == (card+cash):
        print("\n-------------------------------------------")
        print("Date:", getDate(lines))
        print("Card:", card, "  Cash:",cash)
        print("Refunds:", getNettoTotal(lines)-(card+cash), "  Total:", getNettoTotal(lines))
        print("")
        if getNettoTotal(lines)-(card+cash) != 0:
            print("ALERT!!! Report has refunds!!! Check report for more details")
        if discounts != 0:
            print("ALERT!!! Report has disounts, make sure you handle them correctly")
        print("Bokföringshjälp:")
        print("--------------------------")

        unhandledProducts = False
        for k,v in categorys.items():
            if k not in list_Ol and k not in list_Cider and k != "Sprit" and k not in list_Mat and k not in list_Vin and k not in list_Alkfritt:
                print('{0:8.2f} kr - {1}'.format(v, k))
                unhandledProducts = True
        if unhandledProducts:
            print("--------------------------")
            print("OBS! OVANSTÅENDE RADER SAKNAR KATEGORI OCH MÅSTE DÄRFÖR HANTERAS MANUELLT!\n")

        sold_Ol = 0.0
        sold_Cider = 0.0
        sold_Sprit = 0.0
        sold_Vin = 0.0
        sold_Alkfritt = 0.0
        sold_Mat = 0.0
        for k,v in categorys.items():
            if k in list_Ol:
                sold_Ol += v
            if k in list_Cider:
                sold_Cider += v
            if k in list_Sprit:
                sold_Sprit += v
            if k in list_Vin:
                sold_Vin += v
            if k in list_Alkfritt:
                sold_Alkfritt += v
            if k in list_Mat:
                sold_Mat += v

        print("Försäljning (kredit)")
        print('{0:8.2f} kr - {1}'.format(sold_Alkfritt, "Försäljning läsk"))
        print('{0:8.2f} kr - {1}'.format(sold_Ol, "Försäljning öl"))
        print('{0:8.2f} kr - {1}'.format(sold_Cider, "Försäljning cider"))
        print('{0:8.2f} kr - {1}'.format(sold_Vin, "Försäljning vin"))
        print('{0:8.2f} kr - {1}'.format(sold_Sprit, "Försäljning sprit"))
        print('{0:8.2f} kr - {1}'.format(sold_Mat, "Försäljning mat"))
        print("\nInköp och Lager (Inköp på debet & Lager på kredit)")
        print('{0:8.2f} kr - {1}'.format(sold_Ol*0.71, "Inköp öl & Öllager"))
        print('{0:8.2f} kr - {1}'.format(sold_Cider*0.76, "Inköp cider & Ciderlager"))
        print('{0:8.2f} kr - {1}'.format(sold_Sprit*0.43, "Inköp sprit & Spritlager"))
        print('{0:8.2f} kr - {1}'.format(sold_Vin*0.85, "Inköp vin & Vinlager"))
    else:
        print("PARSING ERROR: There seems to be some problem with the parsing of the file")

def getProductSales(lines):
    """This function takes a list of lines and returns a map with the sales for each category.
    The categories are not predefined but are instead created dynamically.
    If a product does not have a category-prefix ("Öl," "Cider," etc) a new category is created using the product's name."""

    # This regex is using 3 match groups. Group 1 retrieves the category, group 2 retrieves the sum without VAT, group 3 retrieves the sum with VAT.
    # \s* before group 1 is to remove any leading whitespace.
    # Group 1 matches everything up until a ',' or 3 consecutive spaces.
    # \d+\s+ before group 2 filters out the number of items sold.
    # \s+[\d,]+\d\d\s+ before group 3 filters out the VAT.

    
    productregex = re.compile("\s*([A-ö+\s\d]*),?.+?\s{3}\d+\s\s+([\d\s]+,\d\d)\s+[\d,]+\d\d\s+([\d\s]+,\d\d)")
    categorys = {}

    sumSold  = 0
    for l in lines:
        match = productregex.match(l)
        if match and match.group(2) == match.group(3):
            sumSold += locale.atof(match.group(2).replace(' ',''))
            category = match.group(1).strip()
            if category in categorys.keys():
                categorys[category] += locale.atof(match.group(2).replace(' ',''))
                # Debug print
                #print(match.group(1), match.group(2),match.group(3))
            else:
                categorys[category] = locale.atof(match.group(2).replace(' ',''))
    
    # Debug print
    #print(categorys)
    return categorys

def getPayments(lines):
    """This function takes a list of lines and returns a tuple with the total card and cash payments."""
    card_paymentsregex = re.compile("\s*Kort\s*\(\d+\)\s*([\d\s]+,\d\d)\s*")
    cash_paymentsregex = re.compile("\s*Kontant\s*\(\d+\)\s*([\d\s]+,\d\d)\s*")
    cash = 0
    card = 0
    for l in lines:
        card_match = card_paymentsregex.match(l)
        cash_match = cash_paymentsregex.match(l)
        if card_match:
            card += locale.atof(card_match.group(1).replace(' ',''))
        elif cash_match:
            cash += locale.atof(cash_match.group(1).replace(' ',''))
    return (card, cash)

def getDiscounts(lines):
    """This function takes a list of lines and returns the total sum of discounts"""
    dateregex = re.compile("\s*Rabatt\s+\d+\s+(-?\d+\,\d\d)\s+[\d,]+\d\d\s+-?\d+\,\d\d")
    for l in lines:
        match = dateregex.match(l)
        if match:
            return locale.atof(match.group(1))
    return 0;

def getDate(lines):
    """This function takes a list of lines and returns the date"""
    dateregex = re.compile("\s*.+?\s+([A-Z][a-z]{2} \d\d?, \d{4}) \d\d:\d\d\s*")
    for l in lines:
        match = dateregex.match(l)
        if match:
            return match.group(1)

def getNettoTotal(lines):
    """This function takes a list of lines and returns the net sum of sales"""
    nettoregex = re.compile("\s*Totalt Netto\s+([\d\s]+,\d\d)\s+[\d,]+\d\d\s+[\d\s]+,\d\d\s*")
    total = 0
    for l in lines:
        match = nettoregex.match(l)
        if match:
            total += locale.atof(match.group(1).replace(' ',''))  
    return total

main()