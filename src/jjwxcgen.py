import argparse
import json
import pickle
from math import dist
from pathlib import Path
from statistics import mean

from fontTools.ttLib import TTFont
from tqdm import tqdm


def table(path):
    font = TTFont(path)
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
            table[glyf] = {
                'unicode': unicode[glyf],
                'coordinates': coordinates
            }
        except AttributeError:
            continue
        except KeyError:
            continue
    return table


fonts = [f for f in Path('examples/jjwxcfont').glob('**/*.woff2') if f.is_file()]
with open('examples/jjwxcfont.pickle', 'rb') as of:
    original = pickle.load(of)


def compare(c1: set, c2: set):
    d1 = c1.difference(c2)
    d2 = c2.difference(c1)
    distance = []
    if d2:
        for xy in d1:
            distance.append(min([dist(xy, _xy) for _xy in d2]))
    if d1:
        for xy in d2:
            distance.append(min([dist(xy, _xy) for _xy in d1]))
    if distance:
        return mean(distance)
    else:
        return 0


min_vals = []
original_list = list(original.items())


def find(c):
    candidates = []
    for k, v in original_list:
        if v['coordinates'] == c[1]['coordinates']:
            return c[0], k, c[1]['unicode'], v['unicode']
        if (len(v['coordinates'].difference(c[1]['coordinates'])) +
                len(c[1]['coordinates'].difference(v['coordinates']))) / 2 < 5:
            candidates.append((k, v))
    if not candidates:
        return c[0], None, None, None
    dists = [compare(v['coordinates'], c[1]['coordinates'])
             for _, v in candidates]
    min_val = min(dists)
    min_id = dists.index(min_val)
    min_char = candidates[min_id]
    min_vals.append(min_val)
    return c[0], min_char[0], c[1]['unicode'], min_char[1]['unicode']


for font in fonts:
    stem = Path(font).stem
    print(font, Path('examples/jjwxcmap/{}.txt'.format(stem)).exists())
    if not Path('examples/jjwxcmap/{}.txt'.format(stem)).exists():
        target = table(font)
        result = [find(c) for c in tqdm(target.items())]
        # tmp = {}
        # final = {}
        output = {}
        # with open('examples/final.json') as f:
        #     final = json.load(f)
        cnt = 0
        for item in result:
            if item[1] is None:  # unrecognized character
                cnt += 1
            else:
                # tmp[item[-2]] = item[-1]
                output[item[-2]] = item[-1]
        with open('examples/jjwxcmap/{}.txt'.format(stem), 'w', encoding='utf-8') as writer:
            # for key, value in tmp.items():
            #     if chr(value) in final:
            #         key = hex(key).replace('0x', '\\u')
            #         value = final[chr(value)]
            #         output[key] = value
            #         # print('&#x{};-{}'.format(key.replace('\\u', ''), value))
            #         writer.write('&#x{};-{}\n'.format(key.replace('\\u', ''), value))
            for key, value in output.items():
                writer.write('&#x{};-{}\n'.format(hex(key).replace('0x', ''), chr(value)))

        # with open('{}.json'.format(''.join(args.target.split('.')[:-1])), 'w') as writer:
        #     json.dump(output, writer)
