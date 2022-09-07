sscript_dcodes = {
    169,
    174,
    8480,
    8482,
    8304,
    8305,
    185,
    178,
    179,
    8308,
    8309,
    8310,
    8311,
    8312,
    8313,
    8314,
    8315,
    8316,
    8317,
    8318,
    7496,
    688,
    8319,
    691,
    738,
    7511,
    8320,
    8321,
    8322,
    8323,
    8324,
    8325,
    8326,
    8327,
    8328,
    8329,
    8330,
    8331,
    8332,
    8333,
    8334,
    8336,
    8337,
    8338,
    8339,
    8340,
    8341,
    8342,
    8343,
    8344,
    8345,
    8346,
    8347,
    8348
}

sscript_to_dcode_table = {
    'sup_0': '&#8304;',
    'sup_i': '&#8305;',
    'sup_1': '&#185;',
    'sup_2': '&#178;',
    'sup_3': '&#179;',
    'sup_4': '&#8308;',
    'sup_5': '&#8309;',
    'sup_6': '&#8310;',
    'sup_7': '&#8311;',
    'sup_8': '&#8312;',
    'sup_9': '&#8313;',
    'sup_+': '&#8314;',
    'sup_-': '&#8315;',
    'sup_=': '&#8316;',
    'sup_(': '&#8317;',
    'sup_)': '&#8318;',
    'sup_d': '&#7496;',
    'sup_h': '&#688;',
    'sup_n': '&#8319;',
    'sup_r': '&#691;',
    'sup_s': '&#738;',
    'sup_t': '&#7511;',
    'sub_0': '&#8320;',
    'sub_1': '&#8321;',
    'sub_2': '&#8322;',
    'sub_3': '&#8323;',
    'sub_4': '&#8324;',
    'sub_5': '&#8325;',
    'sub_6': '&#8326;',
    'sub_7': '&#8327;',
    'sub_8': '&#8328;',
    'sub_9': '&#8329;',
    'sub_+': '&#8330;',
    'sub_-': '&#8331;',
    'sub_=': '&#8332;',
    'sub_(': '&#8333;',
    'sub_)': '&#8334;',
    'sub_a': '&#8336;',
    'sub_e': '&#8337;',
    'sub_o': '&#8338;',
    'sub_x': '&#8339;',
    'sub_Ə': '&#8340;',
    'sub_h': '&#8341;',
    'sub_k': '&#8342;',
    'sub_l': '&#8343;',
    'sub_m': '&#8344;',
    'sub_n': '&#8345;',
    'sub_p': '&#8346;',
    'sub_s': '&#8347;',
    'sub_t': '&#8348;'
}


def is_already_sscript(content):
    for char in content:
        if ord(char) not in sscript_dcodes:
            return False

    return True


def is_convertible_to_dcode(content, script_type):
    for char in content:
        if f'{script_type}_{char}' not in sscript_to_dcode_table:
            return False

    return True


def convert_to_dcode(content, script_type):
    result = ''
    for char in content:
        ss_key = f'{script_type}_{char}'
        result += sscript_to_dcode_table.get(ss_key)

    return result
