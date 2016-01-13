import libarchive.public
import isoExtract






class isoExtract:

    def unpackIsoToFile(self,path):
        extrFiles=[]
        for entry in libarchive.public.file_pour('test_bitstream.iso'):
            print(entry)
            extrFiles.append(entry)

        return extrFiles

    def unpackIsoFromMemory(self,file):
        buffer_ = file
        with libarchive.public.memory_reader(buffer_) as b_iterator:
            for entry in b_iterator:
                with open('/tmp' + 'isofile'+str(entry),'wb') as f:
                    for block in entry.get_blocks:
                        f.write(block)

