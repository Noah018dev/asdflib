from sys import argv
from hashlib import md5, sha512, sha3_384, shake_128, sha1
from lzma import compress
from base64 import b85encode, b32hexencode
import time, sys



Code = open(argv[1], 'r').read()
SecurityKeys = {
    'MD5': md5(Code.encode('utf8')).hexdigest(),
    'SHA-512': sha512(Code.encode('utf8')).hexdigest(),
    'SHA-3-384': sha3_384(Code.encode('utf8')).hexdigest(),
    'SHA-1': sha1(Code.encode('utf8')).hexdigest(),
    'SHAKE-128' : shake_128(Code.encode('utf8')).hexdigest(4)
}
Metadata = {
    "CreationTime" : {
        "User" : time.strftime('%m-%d-%Y, %I:%M:%S %p'),
        "System" : time.strftime('%Y-%m-%d|%H:%M:%S'),
        "AbsoluteTimestamp" : time.time()
    },
    "AsdfexeVersion" : md5(open(__file__, 'rb').read()).hexdigest(),
    "PythonVersion" : f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}.{sys.version_info.releaselevel}'
}

MetadataSecurity = sha1(str(Metadata).encode('ascii')).hexdigest()
HeaderSeprarator = chr(0)
BodyStartCode = ''.join(list(map(chr, range(0, 22))))
EncodedSecurityKeys = b85encode(compress(str(SecurityKeys).encode('ascii'))).decode('ascii')
Header = f'''ASDF.1{HeaderSeprarator}"The next section of the header is the security data. It is not encoded, however, changing them will break the application no matter what you do."{HeaderSeprarator}{str(SecurityKeys)}{HeaderSeprarator}{str(Metadata)}{HeaderSeprarator}{MetadataSecurity}{HeaderSeprarator}{EncodedSecurityKeys}{HeaderSeprarator}No like actually this header is very hard to hack and inject code. I bet you can't lol - Noah018{BodyStartCode}'''
Body = compress(str(Code).encode('ascii'))

with open('compiled.asdf', 'wb') as File :
    File.write(Header.encode('utf-8') + Body)
    File.close()