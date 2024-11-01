import re
import cv2
from cv2.typing import MatLike
import json
import statistics
from typing import Iterable
from mytesseract import TesseractRowList, Problem


def PSM3(img: MatLike, d: dict[str, list[int|float|str]]):

    def trl(src = None) -> TesseractRowList:
        return TesseractRowList(src)

    tesseract_rows = trl(d)

    line_rows = trl(r for r in tesseract_rows if r.isline())
    
    median_line_height = line_rows.getMedianLineHeight()

    # Не все рисунки определяются, как строки с .h >= 2*median_line_height, 
    # ибо в принципе нестабильно определяются тессерактом, придётся хитрить. 
    # нижняя граница — чтобы избавиться от странных однопиксельных артефактов
    text_line_rows = trl(r for r in line_rows if median_line_height // 3 < r.h < 2*median_line_height)

    #### Отфильтруем физически удалённые от основного текста слова (и соответствующие им строки)
    text_word_rows = TesseractRowList()
    for r in text_line_rows:
        for c in r.getChildren():
            text_word_rows.append(c)

    for r in text_line_rows:
        for c in r.getChildren():
            if [c.isNear(wr) for wr in text_word_rows if c != wr].count(True) <= 1:
                c.marked_as_detached = True
                c.show(img, (0,0,255))
    text_line_rows = trl(r for r in text_line_rows if not all(c.marked_as_detached for c in r.getChildren()))
    
    #### Отфильтруем также линии состоящие из слов шириной в ~1 пиксель
    for r in text_line_rows:
        for c in r.getChildren():
            if c.w <= median_line_height // 3:
                c.marked_as_detached = True
    text_line_rows = trl(r for r in text_line_rows if not all(c.marked_as_detached for c in r.getChildren()))

    #### "Прохудим" строки
    #### Логика следующая:
    ####  - Разделить слова в строке (children) на 2 группы по нахождению необычно большого пробела
    ####  - За настоящие слова считаем строки, отвечающие определённому регэкспу (см. реализацию метода countWords)
    ####  - (пока отключено) И в дополнение к разрывам отсеиваем бессмысленные строки из небукв
    ####  - при отрисовке просто использовать envelope оставшихся children
    for r in text_line_rows:
        children = r.getChildren()
        if len(children) == 1:
            continue
        median_space_length = children.getMedianSpaceLength()
        lbound, rbound = 0, len(children)
        for j, child in children.enumerate():
            if j == len(children) - 1:
                continue
            next = children[j + 1] 
            space_length = next.x - child.getRect().u
            # re_str = r'(?:^[^а-яА-Я0-9]+$)' # r'(?:^[^а-яА-Я]+$)' отбраковывает так же номера задач
            # if space_length > 1.2*median_space_length or re.match(re_str, child.text):
            if space_length > 2*median_space_length:
                lcounter, rcounter = children[:j+1].countWords(), children[j+1:].countWords()
                if lcounter < rcounter:
                    lbound = j + 1
                else:
                    rbound = j + 1
                    break
        r.setRect(children[lbound:rbound].envelope())

    #### Отсортируем строки в порядке их нахождения на странице, сверху-вниз
    text_line_rows.sort(key = lambda r: r.y)

    #### Выделяем непрерывные блоки текста
    text_line_blocks = [TesseractRowList([text_line_rows[0]])]
    for i, r in text_line_rows.enumerate():
        if i == len(text_line_rows) - 1:
            continue
        next = text_line_rows[i + 1]
        if next.y - r.y < 1.5 * median_line_height:
            text_line_blocks[-1].append(next)
        else:
            text_line_blocks.append(TesseractRowList([next]))

    #### Визуализируем непрерывные блоки текста
    colors = [
        (0,255,0),
        (255,0,0)
    ]
    for i, t in enumerate(text_line_blocks):
        for j, r in t.enumerate():
            r.show(img, colors[i % 2])
    
    #### Извлекаем задачи
    problems: list[Problem] = []
    counter = 0
    accumulator = trl()
    for i, b in enumerate(text_line_blocks):
        for j, r in b.enumerate():

            cv2.putText(img, str(counter), (r.x, r.y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            #### Извлекаем номер задачи
            problem = Problem(r)
            
            #### Сопоставляем TesseractRows задачам
            #### TODO научиться различать блоки-заголовки
            if problem.number != -1:
                if len(problems) > 0:
                    problems[-1].rows = trl(r for r in accumulator)
                    accumulator = trl()
                else:
                    pass
                    #### TODO научиться присовокуплять accumulator к последней problem с предыдущей страницы
                
            if problem.number != -1:
                problems.append(problem)

            accumulator.append(r)

            if counter in range(30, 40):
                print(counter, i, accumulator)

            counter += 1

        #### Добавить содержимое аккумулятора при каждом окончании блока
        # print("End of block")
        # print(i, accumulator)
        # print(problems)
    #### Добавить содержимое аккумулятора при каждом окончании всех блоков
    problems[-1].rows = trl(r for r in accumulator)
    accumulator = trl()

    print(problems)

    for i, p in enumerate(problems):
        if len(p.rows) > 0:
            p.Rect = p.rows.envelope()
            p.Rect.show(img, (255,0,255))
        else:
            print(p.number)

    def check_sequence(A: Iterable[int]) -> bool:
        A = list(A)
        A.sort()
        answer = True
        for i, n in enumerate(A):
            if i == len(A) - 1:
                continue
            n = int(n)
            if (int(A[i + 1]) - n) != 1:
                answer = False
                break
        return answer
    #TODO а что если у нас перемена с двухзначных на трёхзначные? Ну или с однозначных на двузначные...
    main_problems = [p for p in problems if not p.extra]
    if not check_sequence(p.number for p in main_problems):
        median_str_len = int(statistics.median(len(str(p.number)) for p in main_problems))
        for p in main_problems:
            p.number = int(str(p.number)[:median_str_len])
    extra_problems = [p for p in problems if p.extra]
    if not check_sequence(p.number for p in main_problems) or not check_sequence(p.number for p in extra_problems):
        raise Exception("Couldn't validate problem numbers")

    
def main() -> None:

    fileNumber = 5

    img: MatLike = cv2.imread(f"./PNGs/{str(fileNumber).zfill(2)}.png")

    with open(f"./JSONs-PSM3/{str(fileNumber).zfill(2)}.json", "r") as f:
        d: dict[str, list[int|float|str]] = json.load(f)
    PSM3(img, d)

    #### Fullscreen by default
    cv2.namedWindow('img', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("img", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    ####
    cv2.imshow('img',img)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()