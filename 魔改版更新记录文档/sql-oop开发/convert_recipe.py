import re
import sys


def parse_recipe_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    recipes = []
    current = None

    for stripped in (line.strip() for line in lines):
        # Check for end of current CASE block
        if re.match(r'CASEELSE|ENDSELECT', stripped):
            if current:
                recipes.append(current)
                current = None
            continue

        # Start of a new CASE block
        case_match = re.match(
            r'CASE\s+(?:\[\[(.+?)\]\]|ITEM_(\w+))\s*\*\s*10\s*\+\s*(\d+)\s*$',
            stripped
        )
        if case_match:
            if current:
                recipes.append(current)

            name = case_match.group(1)  # [[name]] format
            item_prefix = case_match.group(2)  # ITEM_xxx format
            recipe_num = int(case_match.group(3))

            if name:
                product_id = f'[[{name}]]'
            else:
                product_id = f'ITEM_{item_prefix}'

            current = {
                'product_id': product_id,
                'recipe_num': recipe_num,
                'ingredients': [],
                'amount': 1,
                'water': 0,
                'lot': 0,
            }
            continue

        if current is None:
            continue

        # ING:N = value
        ing_match = re.match(r'ING:(\d+)\s*=\s*(.+)$', stripped)
        if ing_match:
            idx = int(ing_match.group(1))
            value = ing_match.group(2).strip()
            while len(current['ingredients']) <= idx:
                current['ingredients'].append(None)
            current['ingredients'][idx] = value
            continue

        # AMT = N
        amt_match = re.match(r'AMT\s*=\s*(\d+)$', stripped)
        if amt_match:
            current['amount'] = int(amt_match.group(1))
            continue

        # WATER = N
        water_match = re.match(r'WATER\s*=\s*(\d+)$', stripped)
        if water_match:
            current['water'] = int(water_match.group(1))
            continue

        # LOT = N
        lot_match = re.match(r'LOT\s*=\s*(\d+)$', stripped)
        if lot_match:
            current['lot'] = int(lot_match.group(1))
            continue

    if current:
        recipes.append(current)

    return recipes


def format_qol(recipe):
    pid = recipe['product_id']
    rnum = recipe['recipe_num']

    ingredients = [ing for ing in recipe['ingredients'] if ing is not None]
    ing_str = '/'.join(f'{{{ing}}}' for ing in ingredients)

    amt = recipe['amount']
    water = recipe['water']
    lot = recipe['lot']

    args = f'{pid}, {rnum}, @"{ing_str}", {amt}'
    if lot > 0 and water == 1:
        args += f', {water}, {lot}'
    elif lot > 0:
        args += f', 0, {lot}'
    elif water == 1:
        args += f', {water}'

    return f'CALL QOL_RECIPE_DATA_SET({args})'


def main():
    if len(sys.argv) < 2:
        print('Usage: python convert_recipe.py <path_to_RECIPE_DATA.ERB>', file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    recipes = parse_recipe_data(filepath)

    print('; 由 RECIPE_DATA.ERB 自动转换生成')
    print('@QOL_RECIPE_DATA_REGISTER')
    print('#LOCALSIZE 1')
    print('#LOCALSSIZE 1')
    print('; 格式: QOL_RECIPE_DATA_SET(道具ID, 配方号, "素材列表", 产出量, 是否需要水, 素材总数)')
    print()

    for r in recipes:
        print(format_qol(r))

    print()
    print(f'; 总计转换 {len(recipes)} 条配方')


if __name__ == '__main__':
    main()
