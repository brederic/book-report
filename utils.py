
def getTextBetween(text, start, end):
    if (end != '' and start != ''):
        return text.split(start)[1].split(end)[0]
    elif (end == ''):
        return text.split(start)[1]
    elif(start == ''):
        return text.split(end)[0]
