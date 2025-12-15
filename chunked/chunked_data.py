import base64
from chunked.chunked_type import ChunkedType
from chunked.simple_chunked import SimpleChunked


def split_string(s: str, size: int) -> list[str]:
    return [s[i:i + size] for i in range(0, len(s), size)]


class ChunkedData:
    def __init__(self, data, type, source, max_chunk_size=1000):
        self.initial = data
        self.max_size = max_chunk_size
        self.type = type
        self.source = source
        self.chunks = []

    def proceed(self):
        split = split_string(self.initial, self.max_size)
        total = len(split)
        for i in range(total):
            chunk_type = ChunkedType.Nan
            if i == 0:
                chunk_type = ChunkedType.Start
            elif i == total - 1:
                chunk_type = ChunkedType.End
            if total == 1:
                chunk_type = ChunkedType.Both
            self.chunks.append(f"{self.type}|{self.source}|{chunk_type.value[0]}|{split[i]}")
            #self.chunks.append(split[i])

    def get_proceed(self):
        self.proceed()
        return self.chunks

    @staticmethod
    def restore(chunked: list) -> str:
        restored = ""
        for chunk in chunked:
            restored += chunk.split("|")[3]
        return restored

    @staticmethod
    def simple(chunked: str) -> SimpleChunked:
        print(f'CH: {chunked}')
        data = chunked.split("|")
        t = data[0]
        source = data[1]
        ch_type = ChunkedData.get_type(data[2])
        content = chunked[(len(t) + len(source) + len(data[2]) + 3):]
        return SimpleChunked(t, source, ch_type, content)

    @staticmethod
    def get_type(stype):
        if stype == "START": return ChunkedType.Start
        elif stype == "END": return ChunkedType.End
        elif stype == "BOTH": return ChunkedType.Both
        elif stype == "NAN": return ChunkedType.Nan
        else: return ChunkedType.Nan
