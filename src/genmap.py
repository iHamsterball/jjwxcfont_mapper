import argparse
import json
import pickle

from fontTools.ttLib import TTFont
from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser(description='Generate coordinates map')
    parser.add_argument('file', help='source font file')
    parser.add_argument('--normal', help='input file is normal font')

    args = parser.parse_args()

    font = TTFont(args.file)
    table = {}

    '''
    def gen_helper(cname):
        cname = font['cmap'].tables[0].cmap[codepoint]
        coordinates = {
            coordinates for flag, coordinates in
            zip(font['glyf'][cname].flags, font['glyf'][cname].coordinates)
            if flag
        }
        return {
            'name': cname,
            'coordinates': coordinates
        }

    
    if args.normal:
        for code in range(33, 126):  # ASCII
            table[code] = gen_helper(code)
        for code in range(0x4E00, 0x9FA6):  # 基本汉字
            table[code] = gen_helper(code)
    else:
        for code in font['cmap'].tables[0].cmap:
            table[code] = gen_helper(code)
    '''
    unicode = {v: k for k, v in font['cmap'].tables[0].cmap.items()}
    for glyf in tqdm(font['glyf'].glyphOrder):
        try:
            coordinates = {
                coordinates for flag, coordinates in
                zip(font['glyf'][glyf].flags, font['glyf'][glyf].coordinates)
                if flag
            }
            with open('{}.json'.format(''.join(args.file.split('.')[:-1]))) as f:
                final = json.load(f)
                table[glyf] = {
                    'unicode': int(final[chr(unicode[glyf])].encode('unicode_escape').decode('utf-8').replace('\\u', ''), 16),
                    'coordinates': coordinates
                }
        except AttributeError:
            continue
        except KeyError:
            continue

    with open('{}.pickle'.format(''.join(args.file.split('.')[:-1])), 'wb') as writer:
        pickle.dump(table, writer)


if __name__ == '__main__':
    main()
