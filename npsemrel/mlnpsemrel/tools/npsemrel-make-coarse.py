import csv

rel_conversion = {
        'experiencer' : None,
        'cause'       : 'actor',
        'ficiary'     : 'undergoer',
        'patient'     : 'undergoer'
        }

fstline = True
with open('npsemrel-coarse.csv', 'wt') as outcsv:
    spamwriter = csv.writer(outcsv, delimiter=';', quotechar='"')

    with open('npsemrel.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in spamreader:
            if fstline:
                fstline = False
            else:
                outrel = None
                seppos = row[-1].find(';')
                if seppos > 0:
                    outrel = row[-1][:seppos]
                else:
                    outrel = row[-1]
                if rel_conversion.has_key(outrel):
                    outrel = rel_conversion[outrel]
                if not outrel:
                    continue
                row[-1] = outrel
            spamwriter.writerow(row)
