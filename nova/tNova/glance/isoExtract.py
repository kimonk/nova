import libarchive.public



for entry in libarchive.public.file_pour('test_bitstream.iso'):
    print(entry)

