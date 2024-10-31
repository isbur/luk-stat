# import jsonpickle

#### JSONify
# with open(f"./{str(fileNumber).zfill(2)}.json", "w", encoding='utf-8') as outfile:
#     jsonpickle.set_preferred_backend('json')
#     jsonpickle.set_encoder_options('json', ensure_ascii=False, indent=4)
#     A_json = jsonpickle.encode(A, unpicklable=False)
#     outfile.write(A_json)


# matchProblemNumber = re.match(r'\d{1,3}', text) — более общий случай
# matchProblemNumber = re.match(r'\d{3}', r.text) # только для трёхзначных номеров задач
# matchExtraProblemNumber = re.match(r'Д\.{0,1}$', r.text)

# r'(?:Рис\.?)'

#### Выделяем подписи "Рис. ###" через регэксп
# for r in text_line_rows:
#     children = r.getChildren()
#     if any(re.search(r'\bРис\.?\b', c.text) for c in children):
#         r.show(img, (0,0,255))
#         [print(c.text, end = "|") for c in children]
#     print()


# Добавление надписей на картинку
# cv2.putText(img, str(i), (r.x, r.y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)


# Если снова придётся рисовать окантовки
#
# c.show(img, (0,255,255))
# x,y,u,v = c.getRect()
# epsilon = median_line_height
# cv2.rectangle(img, (x-epsilon,y-epsilon), (u+epsilon,v+epsilon), (0,255,255), 2)
# cv2.putText(img, str(j), (c.x, c.y), cv2.FONT_HERSHEY_SIMPLEX, 1, colors[i % 2], 2)


# Если снова захочется взглянуть на блоки
#
# block_rows = [r for r in tesseract_rows if r.isblock()]
# for i, r in enumerate(block_rows):
#     r.show(img, (255,0,255))
#     cv2.putText(img, str(i), (r.x, r.y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2)