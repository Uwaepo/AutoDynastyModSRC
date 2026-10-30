import re

def is_valid_roman(s: str) -> bool:
    pattern = r"^(C|XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
    return bool(re.fullmatch(pattern, s)) and bool(s)


def int_to_roman(n: int) -> str:
    roman = {
        100: "C",
        90: "XC",
        50: "L",
        40: "XL",
        10: "X",
        9: "IX",
        5: "V",
        4: "IV",
        1: "I"
    }

    if not 1 <= n <= 100:
        return None

    if n == 100:
        return "C"

    result = ""

    for value, symbol in roman.items():
        while n >= value:
            result += symbol
            n -= value

    return result


def roman_to_int(s: str) -> int:
    values = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100
    }

    if is_valid_roman(s) == False:
        return

    if s == "C":
        return 100

    total = 0

    for i in range(len(s)):
        current = values[s[i]]

        if i + 1 < len(s) and current < values[s[i + 1]]:
            total -= current
        else:
            total += current

    return total


def extract_roman_number(s: str) -> str:
    match = re.search(r"[IVXLC]+$", s)

    if match:
        number = match.group()

        if is_valid_roman(number):
            return number

    return None


def is_chinese_number(s: str) -> bool:
    pattern = r"(一百|[二三四五六七八九]?十[一二三四五六七八九]?|[一二三四五六七八九])"
    return bool(re.fullmatch(pattern, s))


def int_to_chinese(n: int) -> str:
    digits = "一二三四五六七八九"

    if not 1 <= n <= 100:
        return None

    if n == 100:
        return "一百"

    if n < 10:
        return digits[n - 1]

    tens, ones = divmod(n, 10)

    result = (digits[tens - 1] if tens > 1 else "") + "十"

    if ones:
        result += digits[ones - 1]

    return result


def chinese_to_int(s: str) -> int:
    digits = "一二三四五六七八九"

    if not is_chinese_number(s):
        return None

    if s == "一百":
        return 100

    if "十" in s:
        tens, ones = s.split("十")

        tens = digits.index(tens) + 1 if tens else 1
        ones = digits.index(ones) + 1 if ones else 0

        return tens * 10 + ones

    return digits.index(s) + 1


def extract_chinese_number(s: str) -> str:
    match = re.search(r"[一二三四五六七八九十百]+$", s)
    if match and is_chinese_number(match.group()):
        return match.group()
    return None