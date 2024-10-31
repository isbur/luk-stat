import cv2
import re, statistics
from Geometry import Rectangle
from TesseractRowList import TesseractRowList


def PSM6(img, d: dict[str, list[int|float]]):
   
    tesseract_rows = TesseractRowList(d)

    # Uncomment to draw all rectangles
    # for r in tesseract_rows:
    #     x,y,u,v = r.getRect()
    #     cv2.rectangle(img, (x,y), (u,v) , (0,255,255), 2)

    word_rows = [x for x in tesseract_rows if x.level == 5]

    # Содержимое страницы без колонтитулов
    # TODO: А всегда ли что-то распознаётся в строке с колонтитулами? Как обнаруживать, что чего-то недораспознали?
    word_rows_except_last_paragraph = TesseractRowList(r for r in word_rows if not(r.par_num == tesseract_rows.getBlockLength() and r.line_num == len(tesseract_rows.getLastPar().getChildren())))
    x2, y2, x3, y3 = word_rows_except_last_paragraph.envelope()
    cv2.rectangle(img, (x2,y2), (x3,y3) , (0,0,255), 2)



    line_rows = [x for x in tesseract_rows if x.level == 4]


    #### "Прохудим" на основании другого признака — удалённости от соседнего элемента больше, чем на удвоенный медианный "пробел"
    space_lengths = []
    for i, r in enumerate(line_rows):
        children = r.getChildren(word_rows)
        for j, child in enumerate(children):
            if j == len(children) - 1:
                continue
            space_length = children[j + 1].x - (child.x + child.w)
            space_lengths.append(space_length)
    median_space_length = statistics.median(space_lengths)

    #### Логика следующая:
    ####  - Разделить слова в строке (children) на 2 группы по нахождению необычно большого пробела
    #### (не сделано)  - Посчитать, сколько слов fuzzy-находятся в тезаурусе
    #### (не сделано)  - Отбраковать ту группу, в которой найдено меньше слов в тезаурусе
    ####  - Сделано проще - за настоящие слова считаем строки, отвечающие определённому регэкспу (см. реализацию метода countWords)
    ####  - И в дополнение к разрывам отсеиваем бессмысленные строки из небукв
    ####  - при отрисовке просто использовать envelope оставшихся children
    for i, r in enumerate(line_rows):
        children = r.getChildren(word_rows)
        if i in (38, 39):
            print(i, children)
        lbound, rbound = 0, len(children)
        for j, child in enumerate(children):
            if j == len(children) - 1:
                continue
            space_length = children[j + 1].x - child.x - child.w
            re_str = r'(?:^[^а-яА-Я0-9]+$)' # r'(?:^[^а-яА-Я]+$)' отбраковывает так же номера задач
            if space_length > 2*median_space_length or re.match(re_str, child.text):
                lcounter, rcounter = children[:j+1].countWords(), children[j+1:].countWords()
                cv2.putText(img, "*", (children[j + 1].x - space_length, child.y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                if lcounter < rcounter:
                    lbound = j + 1
                else:
                    rbound = j + 1
                    break
        newRect = Rectangle(*(children[lbound:rbound].envelope()))
        line_rows[i].setRect(newRect)
        
    
    #### Выделение plaintext-блока на основании медианной высоты строки
    #### TODO: мб вынести в общий блок PSM6+3
    median_line_height = statistics.median(r.h for r in line_rows)

    colors = [
        (0,255,0),
        (255,0,0)
    ]
    block_counter: int = 0
    sub_counters: list[list[int]] = [[]]
    for i, r in enumerate(line_rows):
        if i != 0 and r.y - line_rows[i-1].y - median_line_height > median_line_height:
            block_counter += 1
            sub_counters.append([])
        sub_counters[block_counter].append(i)
        color = colors[block_counter % 2]
        cv2.rectangle(img, (r.x, r.y), (r.x+r.w, r.y+r.h), color, 2)
        cv2.putText(img, str(i), (r.x, r.y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    text_block_line_indices = [x for x in sub_counters if 
                                    len(x) == max(len(x) for x in sub_counters)
                                ][0]
    text_block_rows = TesseractRowList(line_rows[i] for i in text_block_line_indices)
    x1, y1, x2, y2 = text_block_rows.envelope()
    cv2.rectangle(img, (x1, y1), (x2, y2), (255,0,255), 2)
    ####

