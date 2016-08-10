import os
import csv
from dbfread import DBF

root_dir = os.path.dirname(__file__)
data_dir = os.path.join(root_dir, 'data')

rds_dbf_path = os.path.join(data_dir, 'Emergency_RDS_line.dbf')
output_csv = os.path.join(data_dir, 'raw_rds.csv')

with open(output_csv, 'wb') as the_output:
    csvWriter = csv.writer(the_output)
    csvWriter.writerow(['street_name', 'town'])

    # pull only columns 2, 6 and 24
    for record in DBF(rds_dbf_path, 'utf-8', [6, 24]):
        csvWriter.writerow([record['SN'], record['LTWN']])


# Insert rows into sqlite3

# GROUP BY town - verify no weird towns

# Read results and tokenize, removing stop words

# CREATE / Drop table and write tokenized words individually

# GROUP By word, town and COUNT