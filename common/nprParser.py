from dataclasses import dataclass

@dataclass
class NPRData:
    pseudoranges: list[float] = None

def nprParser(filePath) -> list[NPRData]:
    data: list[NPRData] = []
    with open(filePath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = [float(x) for x in line.split()]
            data.append(NPRData(pseudoranges=line))

    return data

