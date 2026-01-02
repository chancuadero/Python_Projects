import hashlib

def hash_file(file1, file2):
    
    hasher1 = hashlib.sha256()
    hasher2 = hashlib.sha256()

    with open(file1, 'rb') as file:

        chunks = 0
        while chunks != b'':
            chunks = file.read(1024)
            hasher1.update(chunks)

    with open(file2, 'rb') as file:

        chunks = 0
        while chunks != b'':
            chunks = file.read(1024)
            hasher2.update(chunks)

    return hasher1.hexdigest(), hasher2.hexdigest()

message1, message2 = hash_file('Beginner/PDF/python.pdf','Beginner/PDF/sololearn.pdf')

if message1 != message2:
    print("PDFs are not identical")
else:
    print("PDFs are identical")