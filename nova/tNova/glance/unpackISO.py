import libarchive.public


with open('test_bitstream.iso', 'rb') as f:
    buffer_ = f.read()
    with libarchive.public.memory_reader(buffer_) as e:
        for entry in e:
            with open('/tmp/' +"_"+ str(entry), 'wb') as f:
                for block in entry.get_blocks():
                    f.write(block)
                    print(block)

