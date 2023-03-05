import argparse
import os
import re

outputDir = "./diff"
counter = 0
emptyCounter = 0

def fileDiff(file1, file2, outputFile):
    global counter
    global outputDir
    global emptyCounter
    outputFolder = os.path.dirname(outputFile)
    os.makedirs(outputFolder, exist_ok=True)

    os.system("diff -B '" + file1 + "' '" + file2 + "' > '" + outputFile + "'")

    if os.stat(outputFile).st_size == 0:
        os.remove(outputFile)
        emptyCounter = emptyCounter + 1
        if emptyCounter % 100 == 0:
            print("D: " + str(counter) + " S: " + str(emptyCounter))
    else:
        counter = counter + 1

def folderDiff(folder1, folder2, outputFolder):
    items1 = os.listdir(folder1)
    items2 = os.listdir(folder2)

    for item in items1:
        if not item in items2:
            if item != ".DS_Store":
                print(item + " is missing")
                break

        item1 = folder1 + "/" + item
        item2 = folder2 + "/" + item
        outputFile = outputFolder + "/" + item
        if os.path.isdir(folder1 + "/" + item):
            folderDiff(item1, item2, outputFile)
        else:
            fileDiff(item1, item2, outputFile)


    for item in items2:
        if not item in items1:
            if item != ".DS_Store":
                print(folder2 + "/" + item + " is missing from " + folder1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('folder1')
    parser.add_argument('folder2')
    parser.add_argument('outputFolder')

    args = parser.parse_args()

    folder1 = args.folder1
    folder2 = args.folder2
    outputFolder = args.outputFolder

    folderDiff(folder1, folder2, outputFolder)

    print(str(counter) + " files that are different and: " + str(emptyCounter) + " are the same" )
    print("reduce files by: " + str(emptyCounter/(emptyCounter + counter)))



if __name__ == "__main__":
    main()