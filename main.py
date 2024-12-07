import psycopg2
conn = psycopg2.connect("host=ep-quiet-sound-a5omz81p.us-east-2.aws.neon.tech dbname=neondb user=neondb_owner password=oUrYj8HTAC6t" )



if __name__ == '__main__':
    for row in cur2
        print(row)

    for row in cur:
        print(row)


    records = cur.fetchall()

    row0 = records[0]
    row1 = records[1]

    print(type(row0))
    print(row0)
    print(row0.keys())

    for key in row0.keys():
        print(f'{key}: {row0[key]}')

    row0_dict = dict(row0)