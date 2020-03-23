# magic-z-reports
Tool for accounting of z-reports created by iZettle cashregister. The script works by automatically categorizing the products in a z-report by their label and summing each of the categories. These sums are then used to work out the accounting figures for each category.

The workflow is as follows:
1. Run the script on one ore more z-reports
2. Copy and paste the results into the accounting software
3. ???
4. PROFIT

### Prerequisites
You have to have the command `pdftotext` from the package `poppler-utils` installed to be able to run the script.
The script is tested on version `0.62.0`.

### Product labels in iZettle
The script currently supports 6 product labels. The labels are: `Öl, Cider, Sprit, Vin, Alkfritt, Mat`. The labels have to follow the format `[label],[product-name]`. A valid product name would for example look like this:
`Cider, Somersby Pear`, `Sprit, 4 cl` or `Öl, Brooklyn, Brooklyn IPA`.  
The script relies on these labels to produce the correct accounting assistance output.

#### What to do if a product doesn't have a label?
Products without a valid label are going to appear like this:
```
Bokföringshjälp:
--------------------------
  100.00 kr - Pop Art
--------------------------
OBS! OVANSTÅENDE RADER SAKNAR KATEGORI OCH MÅSTE DÄRFÖR HANTERAS MANUELLT!
```
If the product belongs to one of the labels it can be added manually to the corresponding list in the beginning of the script, in this case `list_Alkfritt`. Products added to these lists are treated as having the associated label.

**Make sure to use the correct category when adding products manually!**

These lists are only intended to work as a temporary fix, the labels should be updated in iZettle as soon as possible.

## Usage
The script is used with one command.
```
python3 zreport.py "file1.pdf" ["file2.pdf" ...]
```
You may specify more than one file if they are from the same date (event).
The file paths may be either the full or the relative filepath.

### Output
Here is some example output:
```
-------------------------------------------
Date: Feb 20, 2020
Card: 16965.0   Cash: 0
Refunds: 0.0   Total: 16965.0

Bokföringshjälp:
--------------------------
   20.00 kr - Märke
--------------------------
OBS! OVANSTÅENDE RADER SAKNAR KATEGORI OCH MÅSTE DÄRFÖR HANTERAS MANUELLT!

Försäljning (kredit)
  240.00 kr - Försäljning läsk
 6600.00 kr - Försäljning öl
 2515.00 kr - Försäljning cider
  220.00 kr - Försäljning vin
 5810.00 kr - Försäljning sprit
 1560.00 kr - Försäljning mat

Inköp och Lager (Inköp på debet & Lager på kredit)
 5610.00 kr - Inköp öl & Öllager
 2137.75 kr - Inköp cider & Ciderlager
 2498.30 kr - Inköp sprit & Spritlager
  187.00 kr - Inköp vin & Vinlager
```

### Troubleshooting
The script will throw a date error if given z-reports with different dates. This is to prevent z-reports from different events accidentally being parsed together.

The script throws a parsing error if the sum of all the sales for all the parsed products does not match the sum provided by iZettle. The most likely cause of this error is a broken regex. This could be due to an invalid product name or iZettle making changes to the z-report format.

All the relevant debug-prints are left as comments in the script. When debugging a regex it helps to use an online regex tester like https://regexr.com/ or https://regex101.com/.
