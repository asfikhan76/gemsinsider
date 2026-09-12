import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ROOT / 'Pages-20260911T121629Z-1-001' / 'Pages' / '2. COLLECTION'
OUTPUT = ROOT / 'src' / 'data' / 'products.json'

NAMES = {
    'AMETHYST': 'Amethyst',
    'AMETRINE': 'Ametrine',
    'AQUA': 'Aquamarine',
    'CABOCHON': 'Cabochon',
    'GRANDIDERITE': 'Grandidierite',
    'KUNZITE': 'Kunzite',
    'PERIDOT': 'Peridot',
    'RUBELLITE': 'Rubellite',
    'SPESSARTITE GARNET': 'Spessartite Garnet',
    'SPHENE': 'Sphene',
    'SPINEL': 'Spinel',
    'TANZANITE': 'Tanzanite',
    'TOPAZ': 'Topaz',
    'TOURMALINE': 'Tourmaline',
}

LABELS = r'(?:Weight|Dimension|Size|Treatment|Clarity|Color|Shape|Type|Origin|Locality|Hardness|PRICE)'
ENTRY_CODE = r'[A-Z]{2,4}-\s*\d+'


def clean(value):
    value = re.sub(r'\s+', ' ', value).strip()
    value = re.sub(r'\s+([.,$])', r'\1', value)
    value = re.sub(r'([.,])\s+', r'\1', value)
    value = re.sub(r'(?<=\d)\s+(?=\d)', '', value)
    return value.strip(' -:')


def document_text(path):
    with zipfile.ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read('word/document.xml'))
    namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs = []
    for paragraph in root.findall('.//w:p', namespace):
        text = ' '.join(node.text or '' for node in paragraph.findall('.//w:t', namespace))
        if text.strip():
            paragraphs.append(text)
    return '\n'.join(paragraphs)


def field(entry, labels):
    pattern = rf'(?:{labels})\s*:\s*(.*?)(?=\s+(?:{LABELS})\s*:|\s+{ENTRY_CODE}\b|$)'
    match = re.search(pattern, entry, re.IGNORECASE)
    return clean(match.group(1)) if match else ''


def parse_entries(path):
    text = re.sub(r'(?<!\s)(?=(?:Weight|Dimension|Size|Treatment|Clarity|Color|Shape|Type|Origin|Locality|Hardness|PRICE)\s*:)', ' ', document_text(path), flags=re.IGNORECASE)
    chunks = re.split(r'(?=TITLE\s*:)', text, flags=re.IGNORECASE)
    return [clean(chunk) for chunk in chunks if re.search(r'TITLE\s*:', chunk, re.IGNORECASE)]


def main():
    products = []
    for folder in sorted(COLLECTIONS.iterdir()):
        if not folder.is_dir():
            continue
        key = folder.name.rsplit(' (', 1)[0]
        category = NAMES.get(key)
        if not category:
            continue
        document = next(folder.glob('*.docx'), None)
        if not document:
            continue
        entries = parse_entries(document)
        asset_folder = ROOT / 'src' / 'assets' / 'gems' / re.sub(r'[^a-z0-9]+', '-', key.lower()).strip('-')
        videos = sorted(asset_folder.glob('*.mp4'), key=lambda path: int(re.search(r'(\d+)', path.stem).group(1)))
        for index, video in enumerate(videos):
            entry = entries[index] if index < len(entries) else ''
            title_match = re.search(r'TITLE\s*:\s*(.*?)(?=\s+(?:Weight|Dimension|Size|Treatment|Clarity|Color|Shape|Origin|Locality|Hardness|PRICE)\s*:|\s+' + ENTRY_CODE + r'\b|$)', entry, re.IGNORECASE)
            title = clean(title_match.group(1)) if title_match else f'{category} {index + 1}'
            products.append({
                'id': f'{category}-{index + 1}',
                'name': title or f'{category} {index + 1}',
                'category': category,
                'media': f'./assets/gems/{video.parent.name}/{video.name}',
                'requirements': {
                    'weight': field(entry, 'Weight'),
                    'dimension': field(entry, 'Dimension|Size'),
                    'treatment': field(entry, 'Treatment'),
                    'clarity': field(entry, 'Clarity'),
                    'color': field(entry, 'Color'),
                    'shape': field(entry, 'Shape|Type'),
                    'origin': field(entry, 'Origin|Locality'),
                    'hardness': field(entry, 'Hardness'),
                    'price': field(entry, 'PRICE'),
                },
            })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(products, indent=2, ensure_ascii=False) + '\n')
    print(f'Generated {len(products)} products in {OUTPUT}')


if __name__ == '__main__':
    main()