import math
from tabulate import tabulate
from colorama import init, Fore, Style


def FreqsDict(freqs: str):
    """
    Создает словарь частот
    :param freqs: строка вида A:2 B:6, где A, B - символы алфавита, а 2, 6 - частоты встречаемости в тексте (в сумме дают степень двойки)
    :return: словарь, где ключи - буквы, а значения - частоты
    """
    freqs = freqs.split(" ")
    d = {}
    for i in freqs:
        i_spl = i.split(":")
        d[i_spl[0]] = i_spl[1]
    return d


def CreateZeroMatrix(n, m):
    """
    Создает нулевую матрицу
    :param n: количество строк
    :param m: количество столбцов
    :return: нулевая матрица n * m
    """
    matrix = []
    for i in range(n):
        row = []
        for j in range(m):
            row.append(0)
        matrix.append(row)
    return matrix


def InputIsCorrect(alph_cnt: int, freqs: str, text: str, final: int, compression: bool):
    """
    Функция, проверяющая, являются ли введенные данные корректными для FSE сжатия / разжатия
    :param compression: True / False
    :param final: финальное состояния
    :param alph_cnt: целое число - кол-во символов в алфавите
    :param freqs: строка вида A:2 B:6, где A, B - символы алфавита, а 2, 6 - частоты встречаемости в тексте (в сумме дают степень двойки)
    :param text: строка - текст для сжатия
    :return: True / False
    """
    try:
        dfreqs = dict(FreqsDict(freqs))
        if not math.log2(sum([int(x) for x in dfreqs.values()])).is_integer():
            return False
        if len(dfreqs) != alph_cnt:
            return False
        if compression:
            text = set(list(text))
            if alph_cnt != len(text):
                return False
            return True
        else:
            return True  # TODO
    except:
        return False


def split_power_of_two_old(N, k):
    # Проверяем, что N и k являются целыми числами и что N является степенью двойки
    if not isinstance(N, int) or not isinstance(k, int) or (N & (N - 1) != 0):
        return None  # Возвращаем None в случае неверных входных данных
    # Вычисляем maxbit - наибольшую степень двойки, такую что 2^maxbit >= N / k
    maxbit = N.bit_length() - k.bit_length()
    # Вычисляем количество больших интервалов - это N / 2^maxbit
    big_count = N >> maxbit
    # Вычисляем количество малых интервалов - это (k - big_count) * 2
    small_count = (k - big_count) << 1
    # Создаем пустой список для хранения слагаемых
    result = []
    # Добавляем малые интервалы в список - это 2^(maxbit-1)
    result.extend([1 << (maxbit - 1)] * small_count)
    # Добавляем большие интервалы в список - это 2^maxbit
    result.extend([1 << maxbit] * big_count)
    # Проверяем, что сумма слагаемых равна N
    if sum(result) != N:
        # Если нет, то уменьшаем количество больших интервалов на 1 и увеличиваем количество малых интервалов на 2
        result.pop()
        result.extend([1 << (maxbit - 1)] * 2)
    # Возвращаем список слагаемых
    return result[:k]  # Берем только первые k элементов списка


def IsPowOfTwo(n):
    return round(math.ceil(math.log2(n))) == round(math.floor(math.log2(n)))


def SplitPowerOfTwo(total: int, count: int):
    """
    Создает массив из чисел, каждое число - количество позиций в таблице состояний, которое занимает одно состояние из всех
    пример: символ А встречается с вероятностью 6 из 16, для 'A' определено 6 состояний от 1 до 6
    состояние 1 в таблице состояний занимает 2 позиции, то же самое для состояний 2, 3 и 4
    а состояния 5 и 6 занимают по 4 позиции (итого 6 состояний занимают все 16 возможных позиций)
    массив [2, 2, 2, 2, 4, 4] и будет результатом функции
    """
    res = [0 for i in range(count)]
    if count == total:
        for i in range(count):
            res[i] = 1
    elif count > total / 2:
        res = SplitPowerOfTwo(total // 2, total // 2) + SplitPowerOfTwo(total // 2, count - total // 2)
    elif (total % count == 0) and (IsPowOfTwo(total // count)):
        amount = total // count
        for i in range(count):
            res[i] = amount
    else:
        amount = int(math.pow(2, math.floor(math.log2(total / count))))
        for j in range(count):
            res[j] = amount
        last = total - count * amount
        i = count - 1
        while i > 0:
            if IsPowOfTwo(amount + last // (count - i)):
                for j in range(count - 1, i-1, -1):
                    res[j] += last // (count - i)
            i -= 1
    return res


def StateIndices(dfreqs: dict):
    let_ind = {}
    if len(dfreqs) == 1:
        let_ind[list(dfreqs.keys())[0]] = [int(list(dfreqs.values())[0])]
        return let_ind
    sumfreqs = sum([int(x) for x in dfreqs.values()])
    alph_cnt = len(dfreqs)
    for let in dfreqs.keys():
        let_ind[let] = SplitPowerOfTwo(int(sumfreqs), int(dfreqs[let]))
    return let_ind


def TableStateFiller(state_lengths, sumfreqs, current_state):
    b = [0] * sumfreqs
    k = current_state
    i = 0
    for n in state_lengths:
        b[i:i + n] = [k] * n
        k += 1
        i += n
    return b, k


def CreateTable(freqs: str):
    dfreqs = FreqsDict(freqs)
    if len(dfreqs) == 1:
        dfreqs[list(dfreqs.keys())[0]] = 1
    alph_cnt = len(dfreqs)
    table = CreateZeroMatrix(alph_cnt + 1, sum([int(x) for x in dfreqs.values()]) + 1)
    table[0][0] = "#"
    for i in range(1, alph_cnt + 1):
        table[i][0] = list(dfreqs.keys())[i - 1]
    letter_counter = 1
    for j in range(1, sum([int(x) for x in dfreqs.values()]) + 1):
        table[0][j] = list(dfreqs.keys())[letter_counter - 1]
        letter_counter += 0 \
            if j < sum([int(x) for x in list(dfreqs.values())[:letter_counter]]) \
            else 1
    current_state = 1
    for i in range(1, alph_cnt + 1):
        rowletter = table[i][0]
        state_magic = TableStateFiller(StateIndices(dfreqs)[rowletter],
                                        sum([int(x) for x in dfreqs.values()]),
                                        current_state)
        table[i][1:] = state_magic[0]
        states_in_row = set()
        k_curr = 0
        for j in range(1, len(table[i])):
            curr = table[i][j]
            if curr in states_in_row:
                k_curr += 1
            else:
                k_curr = 0
                states_in_row.add(curr)
            table[i][j] = [curr, "0" * (- len(bin(k_curr)[2:]) + round(math.log2(state_magic[0].count(curr)))) + bin(k_curr)[2:]]
        current_state = state_magic[1]
    return table


def Compress(alph_cnt: int, freqs: str, text: str):
    if not InputIsCorrect(alph_cnt, freqs, text, 0, True):
        return ["", "", "Некорректные данные, повторите ввод"]
    dfreqs = FreqsDict(freqs)
    table = CreateTable(freqs)
    letter = text[0]
    state = table[0].index(letter)
    bits = ""
    fs = [state, text, bits]
    # print(fs)
    while len(text) != 0:
        letter = text[0]
        text = text[1:]
        vertical_index = list(dfreqs.keys()).index(letter) + 1
        cell = table[vertical_index][state]
        state = cell[0]
        bits += cell[1]
        fs = [state, text, bits]
        # print(fs)
    return fs




def StateCodesLengths(freqs: str):
    """
    По списку частот формирует словарь вида {внутреннее состояние: длина кодов состояния, ...}\n
    {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 3} для "A:3 T:2 G:2 C:1"
    """
    alph_cnt = len(FreqsDict(freqs))
    table = CreateTable(freqs)
    res = {}
    for i in range(1, alph_cnt + 1):
        for j in range(1, len(table[0])):
            res[table[i][j][0]] = len(table[i][j][1])
    return res


def FindIndicesOfState(freqs: str, state: int):
    alph_cnt = len(FreqsDict(freqs))
    table = CreateTable(freqs)
    ind = []
    for i in range(1, alph_cnt + 1):
        for j in range(1, len(table[i])):
            if table[i][j][0] == state:
                ind.append([i, j])
    return {"row": ind[0][0], "start": ind[0][1], "end": ind[-1][1]}


def FindLetterAndPrevState(freqs: str, state: int, bits: str):
    """
    На вход подается состояние и битовая строка. Действия:\n
    1. Считаем длину кодов (одного из) состояния [lencode]
    2. Отрезаем с конца битовой строки lencode символов [bit]
    3. Ищем букву (сверху таблицы), проходясь по всем кодам [code] этого состояния
    4. Если код и бит совпали [code == bit], то возвращаем в виде кортежа:
        (соответствующее code'у и внутреннему состоянию верхнее состояние [up_state];\n
        буква, соответствующая верхнему состоянию [letter];\n
        битовая строка без последнего bit [bits])
    5. Если не совпали, продолжаем искать
    """
    try:
        dfreqs = FreqsDict(freqs)
        sumfreqs = sum([int(x) for x in dfreqs.values()])
        alph_cnt = len(dfreqs)
        table = CreateTable(freqs)

        # Длина кодов состояния
        lencode = StateCodesLengths(freqs)[state]
        # print(lencode)

        # Бит для проверки мэтча
        bit = bits[-lencode:]
        bits = bits[:-lencode]

        # Границы состояния в таблице
        state_ind = FindIndicesOfState(freqs, state)
        row = state_ind["row"]
        start = state_ind["start"]
        end = state_ind["end"]

        letter = "666"
        up_state = 666

        FOUND = False
        for j in range(start, end + 1):
            code = table[row][j][1]
            if code == bit:
                letter = table[row][0]
                up_state = j
                FOUND = True
                break

        if not FOUND:
            # print("!!!", state)
            return "STOPSIGNAL"

        return up_state, letter, bits
    except Exception:
        return "STOPSIGNAL"


def Decompress(alph_cnt: int, freqs: str, bits: str, final: int):
    if not InputIsCorrect(alph_cnt, freqs, bits, final, False):
        return ["", "Некорректные данные, повторите ввод", ""]
    fs = [final, "", bits]
    try:
        # print(fs, end=" <-- ")
        while len(bits) != 0 and fs[0] != 0:
            engine = FindLetterAndPrevState(freqs, fs[0], fs[2])
            if engine == "STOPSIGNAL" and len(fs[2]) != 0:
                fs[1] = f"Что-то пошло не так. Проверьте корректность введенных данных... {fs[1]}"
                break
            if engine == "STOPSIGNAL":
                break
            fs[0] = engine[0]
            fs[1] = engine[1] + fs[1]
            fs[2] = engine[2]
            if len(bits) == 0:
                break
            # print(fs, end=" <-- ")
    except Exception:
        fs[1] = f"Что-то пошло не так. Проверьте корректность введенных данных {fs[1]}"
    return fs


print(Fore.GREEN + Style.BRIGHT + ">>> FINITE STATE ENTROPY <<<" + Style.RESET_ALL)
while True:
    try:
        s = input("d / c: ")
        if s == "d":
            print("ДЕКОДИРОВАНИЕ")
            alph_cnt = int(input("Количество символов в алфавите: "))
            freqs = input("Частоты в формате A:1 B:2 C:1 (сумма частот - степень 2): ")
            bits = input("Битовая строка: ")
            final = int(input("Финальное состояние при кодировании: "))
            res = Decompress(alph_cnt, freqs, bits, final)
            print(f"Финальная запись автомата: {res}"
                  f"\nФинальное (начальное) состояние: {Fore.MAGENTA + str(res[0]) + Style.RESET_ALL}"
                  f"\nРазжатая строка: {Fore.MAGENTA + str(res[1]) + Style.RESET_ALL}"
                  f"\nИнформация о кодировке:"
                  f"\n{tabulate(CreateTable(freqs), tablefmt='pipe')}")
        elif s == "c":
            print("КОДИРОВАНИЕ")
            alph_cnt = int(input("Количество символов в алфавите: "))
            freqs = input("Частоты в формате A:1 B:2 C:1 (сумма частот - степень 2): ")
            text = input("Текст (согласно предыдущим двум вводам): ")
            res = Compress(alph_cnt, freqs, text)
            print(f"Финальная запись автомата: {res}"
                  f"\nФинальное состояние: {Fore.MAGENTA + str(res[0]) + Style.RESET_ALL}"
                  f"\nCжатая строка: {Fore.MAGENTA + str(res[2]) + Style.RESET_ALL}"
                  f"\nИнформация о кодировке:"
                  f"\n{tabulate(CreateTable(freqs), tablefmt='pipe')}")
        else:
            print("Я тут вам не ChatGPT :) У меня есть только команды: c и d")
        print()
    except Exception:
        print(Fore.RED + Style.BRIGHT + "Произошла какая-то неизвестная ошибка. Проверьте ввод." + Style.RESET_ALL)
        print()