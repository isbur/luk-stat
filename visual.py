import cv2 
from cv2.typing import MatLike
import json
import statistics
from typing import Callable
from luk import Problem, LukProblems
from luk.mytesseract import TesseractRowList, TesseractRow


def PSM3(img: MatLike, d: dict[str, list[int|float|str]]) -> LukProblems:

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
        for c in r.children:
            text_word_rows.append(c)

    for r in text_line_rows:
        for c in r.children:
            if [c.isNear(wr, epsilon=2*median_line_height) for wr in text_word_rows if c != wr].count(True) <= 1:
                c.marked_as_detached = True
                c.show(img, (0,0,255))
    text_line_rows = trl(r for r in text_line_rows if not all(c.marked_as_detached for c in r.children))
    
    #### Отфильтруем также линии состоящие из слов шириной в ~1 пиксель
    for r in text_line_rows:
        for c in r.children:
            if c.w <= median_line_height // 3:
                c.marked_as_detached = True
    text_line_rows = trl(r for r in text_line_rows if not all(c.marked_as_detached for c in r.children))

    #### "Прохудим" строки
    #### Логика следующая:
    ####  - Разделить слова в строке (children) на 2 группы по нахождению необычно большого пробела
    ####  - За настоящие слова считаем строки, отвечающие определённому регэкспу (см. реализацию метода countWords)
    ####  - (пока отключено) И в дополнение к разрывам отсеиваем бессмысленные строки из небукв
    ####  - при отрисовке просто использовать envelope оставшихся children
    for r in text_line_rows:
        children = r.children
        if children is None:
            raise Exception("Row children are not initialized")
        if len(children) == 1:
            continue
        median_space_length = children.getMedianSpaceLength()
        lbound, rbound = 0, len(children)
        for j, child in children.enumerate():
            if j in (0, len(children) - 1): # игнорируем правило для первого слова - скорее всего, это номер задачи (atan7)
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
        r.children = children[lbound:rbound]
        r.setRect(r.children.envelope())

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
    # for i, t in enumerate(text_line_blocks):
    #     for j, r in t.enumerate():
    #         r.show(img, colors[i % 2])
    
    #### Извлекаем задачи
    def extractProblems(problemConstructorCall: Callable[[TesseractRow, TesseractRowList],Problem]) -> tuple[LukProblems, list[int]]:

        # Внешние переменные:
        # tesseract_rows
        # text_line_blocks

        problems = LukProblems([], tesseract_rows)
        indents: list[int] = []
        counter = 0
        accumulator = trl()
        for i, b in enumerate(text_line_blocks):
            for j, r in b.enumerate():

                # cv2.putText(img, str(counter), (r.x, r.y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                #### Извлекаем номер задачи
                problem = problemConstructorCall(r, accumulator)
                
                
                #### Сопоставляем TesseractRows задачам
                #### TODO научиться различать блоки-заголовки
                if problem.number != -1:
                    if len(problems) > 0:
                        problems[-1].rows = trl(r for r in accumulator)
                        if len(accumulator) > 1:
                            indents.append(accumulator[0].Rect.x - accumulator[1].Rect.x)
                        accumulator = trl()
                    else:
                        pass
                        #### TODO научиться присовокуплять accumulator к последней problem с предыдущей страницы
                    
                if problem.number != -1:
                    problems.append(problem)

                accumulator.append(r)

                # if counter in range(30, 40):
                #     print(counter, i, accumulator)

                counter += 1
        #### Добавить содержимое аккумулятора при окончании всех блоков
        problems[-1].rows = trl(r for r in accumulator)
        accumulator = trl()

        return problems, indents

    problemConstructorCall: Callable[[TesseractRow, TesseractRowList], Problem] = lambda r, _: Problem(r)
    problems, _ = extractProblems(problemConstructorCall)

        
    # if not problems.check_sequence():
    #     print("Couldn't validate problem sequence:", problems)
    
    # Заполним "дырки" пустыми задачами с соответствующими номерами
    # if not problems.check_sequence():
    #     full_number_sequence = list(range(problems[0].number, problems[-1].number + 1))
    #     for i, n in enumerate(full_number_sequence):
    #         if all(n != p.number for p in problems):
    #             problems.problems.insert(i, Problem(n))

    
    for p in problems:
        if len(p.rows) > 0:
            p.Rect = p.rows.envelope()
            # p.Rect.show(img, (255,0,255))
        else:
            print(p.number)
    
    return problems


def show(img: MatLike):
    #### Fullscreen by default
    cv2.namedWindow('img', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("img", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    ####
    cv2.imshow('img',img)
    cv2.waitKey(0)

    
def main() -> None:

    fileNumber = 10

    img: MatLike = cv2.imread(f"./PNGs/input-{str(fileNumber).zfill(2)}.png")

    with open(f"./JSONs-PSM3/{str(fileNumber).zfill(2)}.json", "r") as f:
        d: dict[str, list[int|float|str]] = json.load(f)
    PSM3(img, d)

    show(img)


if __name__ == "__main__":
    main()