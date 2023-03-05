#2297

import argparse
import os
import re

counter = 0

def deobfuscateText(text):
    global counter
    lines = text.split('\n')

    # delete nop
    i = 0
    linesLength = len(lines)
    while i < linesLength:
        line = lines[i]
        if re.match('\s+nop', line):
            del lines[i]
            i -= 1
            linesLength = len(lines)

        i += 1

    # delete comments
    i = 0
    linesLength = len(lines)
    while i < linesLength:
        line = lines[i]
        if re.match('\s+\.line\s+\d+|\.source .*', line):
            del lines[i]
            i -= 1
            linesLength = len(lines)
        i += 1

    # delete blank lines
    i = 0
    linesLength = len(lines)
    while i < linesLength:
        line = lines[i]
        if re.match('^\s*$', line):
            del lines[i]
            i -= 1
            linesLength = len(lines)
        i += 1

    # Added variables
    suspectVar = ""
    localExpression = '\s+\.locals (\d+)'
    linesLength = len(lines)
    i = 0
    while i < linesLength:
        line = lines[i]
        if 'const-string v0, "NetworkMeteredCtrlr"' in line:
            x = 0
        result = re.match(localExpression, line)
        if bool(result):
            localVariables = int(result.group(1))
            while localVariables > 0:
                suspectVar = "v" + str(localVariables - 1)
                # scan ahead and see if the suspect variable is used
                suspectUsed = False
                endPos = -1
                for j in range(i+1, len(lines)):
                    skipLine = lines[j]
                    if re.match(localExpression, skipLine):
                        # Stop skipping forward
                        endPos = j
                        break

                    if re.search('\s+' + suspectVar, skipLine):
                        setCommands = ['const\/\d+', 
                                       'const-string', 
                                       'or-int\/2addr',
                                       'move',
                                       'and-int\/2addr',
                                       'shl-int\/2addr',
                                       'shr-int\/2addr']
                        
                        setCommandStatement = '(' + '|'.join(setCommands) + ') '
                        if not re.search(setCommandStatement + suspectVar, skipLine):
                                    suspectUsed = True

                if endPos < 0:
                        endPos = len(lines)

                if suspectUsed == False:
                    # Delete suspectVars
                    modifyLine = re.sub('\d+', "", line) + str(localVariables - 1)
                    lines[i] = modifyLine

                    start = i
                    end = endPos

                    for j in range(end -1, start, -1):
                        scanLine = lines[j]
                        if re.search('\s+' + suspectVar, scanLine):
                            del lines[j]
                    linesLength = len(lines)
                else:
                    break

                localVariables -= 1
        i += 1

    # reused variables
    i = 0
    while i < linesLength:
        line = lines[i]
        regexType = '(const-string|const-string\/jumbo|const\/\d+|const-wide|const-wide\/\d+|move-object|move-object\/from16|const-class|move|move\/from\d+|const-wide\/high\d+) '
        result = re.search( regexType + '(v\d+|p\d+)', line)
        if result:
            suspectVariable = result.group(2)

            # See if variable is used on next line
            j = i + 1
            nextLine = lines[j]

            if re.search(regexType + suspectVariable + "\D", nextLine):
                del lines[i]
                linesLength = len(lines)
                i -= 1

        i += 1

    # jumbo operations to non-jumbo
    i = 0
    linesLength = len(lines)
    while i < linesLength:
        line = lines[i]
        # goto/16 :goto_1
        #  const-string/jumbo v1, "state="
        # 
        jumboCommands = ['const-string/jumbo', 'goto/16']
        if re.search("const-string\/jumbo", line):
            lines[i] = re.sub('\/jumbo', "", line)
        elif re.search("goto/16", line):
            lines[i] = re.sub('\/16', "", line)
        elif re.search("goto/32", line):
            lines[i] = re.sub('\/32', "", line)
        i += 1

    return '\n'.join(lines)


def deobfuscateFile(inputFile, outputFile):
    global counter
    text = ""
    with open(inputFile, 'r') as f:
        text = f.read()
        
    restoredText = deobfuscateText(text)

    with open(outputFile, 'w') as f:
        f.write(restoredText)

    counter += 1

    if counter % 100 == 0:
        print("parsed: " + str(counter) + " number of files")


def folderSearch(inputFolder, outputFolder):
    os.makedirs(outputFolder, exist_ok=True)
    inputItems = os.listdir(inputFolder)

    for item in inputItems:
        if item == '.DS_Store':
            continue
        inputItemPath = inputFolder + "/" + item
        outputItemPath = outputFolder + "/" + item

        if os.path.isdir(inputItemPath):
            folderSearch(inputItemPath, outputItemPath)
        else:
            deobfuscateFile(inputItemPath, outputItemPath)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputFolder')
    parser.add_argument('outputFolder')

    args = parser.parse_args()

    inputFolder = args.inputFolder
    outputFolder = args.outputFolder

    folderSearch(inputFolder, outputFolder)
    print("done")


if __name__ == "__main__":
    main()