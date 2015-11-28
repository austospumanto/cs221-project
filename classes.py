import collections, itertools, Queue
import numpy, scipy, math, random
import os, sys
import tokenize, re, string






### Data Structures 
class Ingredient:
    def __init__(self):
        self.amount = ""
        self.units = ""
        self.ingredientName = ""
        self.entireLine = ""          # Contains amount, units, and ingredient name
        self.lineWithoutAmount = ""

        self.wordsInIngredient = []            # Vector of strings
        self.nonUnitWordsInIngredient = []     # Vector of strings
        self.endSeed = []                      # Vector of strings

class InstructionSentence:
    def __init__(self):
        self.isGoodSentence = True
        self.isServingSentence = True

        self.firstWord = ""
        self.sentence = ""
        self.sentenceSubbed = ""

        self.order1EndSeedsInside = []       # Vector of strings
        self.order2EndSeedsInside = []       # Vector of vector of strings
        self.nonUnitWordsInIngredient = []   # Vector of strings
        self.endSeed = []                    # Vector of strings
        self.tokensInSentence = []           # Vector of strings

class InstructionStep:
    def __init__(self):
        self.stepNumber = 0
        self.numSentences = 0
        self.allText = ""
        self.allTextEdited = ""
        self.instructionSentences = []    # Vector of InstructionSentence's
        self.sentenceStringVec = []       # Vector of strings










"""
Class: Recipe
 * ------------------------------------------------
 * Recipe contains the ingredients, name, serving size
 * and instructions for a recipe. It also implements
 * very useful functions for the whole program.

    string name
    string allRecipeText
    string allIngredientsText
    string allInstructionsText
    string allInstructionsTextEdited
    int numServings
    int numInstructions
    int numIngredients
    int indStartRecipe
    int recipeCharLength
    bool instructionsAreNumbered
    Vector<ingredient> ingredients
    Vector<instructionStep> instructionSteps
    Vector<Vector<string>> endSeeds
    Vector<instructionSentence> goodInstructionSentences
    Vector<instructionSentence> servingInstructionSentences
    Vector<string> finalIngredientWords
    Vector<string> instructions
    Vector<string> NORMAL_UNITS
    Vector<string> NORMAL_UNITS_PLURAL
    Vector<string> ABNORMAL_UNITS
    Vector<string> DESCRIPTORS
    Vector<string> STANDALONES
    Vector<string> INSTRUCTION_VERBS
    Vector<string> VALID_AFTER_WORDS
    Vector<string> VALID_BEFORE_WORDS
    Map<string,int> UNIT_TO_VOLUME    #Volume in milliliters (cc, cm^3)

 * ------------------------------------------------
"""
class Recipe:

    VALID_AFTER_WORDS = ["to", "in", "into", "on", "are", ".", ",", ";", "is"]
    VALID_BEFORE_WORDS = ["NUMBERS", "the", "and", "with"]
    NORMAL_UNITS = ["teaspoon", "tablespoon", "pound", "cup", "ounce", \
            "bunch", "strip", "clove", "stalk", "stick", "loaf", \
            "rind", "slice", "sprig", "head", "ear", "can", "pint", \
            "quart", "gallon", "sheet"]
    NORMAL_UNITS_PLURAL = ["teaspoons", "tablespoons", "pounds", "cups", "ounces", \
            "bunches", "strips", "cloves", "stalks", "sticks", "loaves", \
            "rinds", "slices", "sprigs", "heads", "ears", "cans", "pints", \
            "quarts", "gallons", "sheets"]
    ABNORMAL_UNITS = ["Pinch of", "Juice of", "Zest of"]
    DESCRIPTORS = ["large", "small", "whole", "thin", "coarse", "red", "green", \
            "rack", "hot", "medium", "baby", "fresh", "dried", "frozen", \
            "boneless", "skinless", "ripe", "pink", "coarsely chopped", "cold", \
            "minced", "grated", "finely grated", "ground", "hot", "freshly ground"]
    STANDALONES = ["Freshly ground pepper", "Coarse salt", \
            "Coarse salt and freshly ground pepper", \
            "Fresh tarragon and tarragon flowers", \
            "Creamy Tarragon Vinaigrette", \
            "Freshly ground black pepper", \
            "Canola oil", \
            "Coarse salt and freshly ground black pepper", \
            "Lime wedges", \
            "Cooking spray", \
            "Cold water" \
            "Crushed Ice"]
    INSTRUCTION_VERBS = ["Fill", "Mix", "Place", "Stir", "In", "Process", "Heat", "Whisk", \
            "Combine", "With", "Puree", "Squeeze", "Bring", "Put", "Using", "Toss", "Melt", \
            "Prepare", "Pour", "Preheat", "Soak", "Halve", "Line", "Cut", "Add", "Pulse", \
            "Mash", "Blend", "Sprinkle", "Beat", "Arrange", "Set", "Fit", "Scoop", "Cover"]
    UNIT_TO_VOLUME = {}
    UNIT_TO_VOLUME["cup"] = 237
    UNIT_TO_VOLUME["teaspoon"] = 5
    UNIT_TO_VOLUME["tablespoon"] = 15
    UNIT_TO_VOLUME["pint"] = 473
    UNIT_TO_VOLUME["quart"] = 950
    UNIT_TO_VOLUME["gallon"] = 3800
    UNIT_TO_VOLUME["can"] = 474

    def __init__(self):
        self.name = ""
        self.numServings = 0
        self.numIngredients = 0
        self.numInstructions = 0
        self.instructionsAreNumbered = False
        self.allRecipeText = ""
        # self.indStartRecipe = 0
        self.recipeCharLength = 0
        self.allIngredientsText = ""
        self.allInstructionsText = ""
        self.instructionSteps = []
        self.ingredients = []
        self.endSeeds = []
        self.finalIngredientWords = []
        self.goodInstructionSentences = []
        self.servingInstructionSentences = []

    ## Setters
    def setAllRecipeText(self, newAllRecipeText):
        self.allRecipeText = newAllRecipeText
    def setAllIngredientsText(self, newAllIngredientsText):
        self.allIngredientsText = newAllIngredientsText
    def setAllInstructionsText(self, newAllInstructionsText):
        self.allInstructionsText = newAllInstructionsText
    def setName(self, newName):
        self.name = newName
    def setNumServings(self, newNumServings):
        self.numServings = newNumServings
    def setNumInstructions(self, newNumInstructions):
        self.numInstructions = newNumInstructions
    def setNumIngredients(self, newNumIngredients):
        self.numIngredients = newNumIngredients
    # def setIndStartRecipe(self, newIndStartRecipe):
    #     self.indStartRecipe = newIndStartRecipe
    def setRecipeCharLength(self, newRecipeCharLength):
        self.recipeCharLength = newRecipeCharLength
    def setIngredients(self, newIngredients):
        self.ingredients = newIngredients
    def setInstructions(self, newInstructions):
        self.instructions = newInstructions
    def setEndSeeds(self, newEndSeeds):
        self.endSeeds = newEndSeeds
    def setInstructionSteps(self, newInstructionSteps):
        self.instructionSteps = newInstructionSteps

    # Getters 
    def getAllRecipeText(self):
        return self.allRecipeText
    def getAllIngredientsText(self):
        return self.allIngredientsText
    def getAllInstructionsText(self):
        return self.allInstructionsText
    def getName(self):
        return self.name
    def getNumServings(self):
        return self.numServings
    def getNumInstructions(self):
        return self.numInstructions
    def getNumIngredients(self):
        return self.numIngredients
    # def getIndStartRecipe(self):
    #     return self.indStartRecipe
    def getRecipeCharLength(self):
        return self.recipeCharLength
    def getIngredients(self):
        return self.ingredients
    def getInstructions(self):
        return self.instructions
    def getEndSeeds(self):
        return self.endSeeds
    def getInstructionSteps(self):
        return self.instructionSteps
    def getGoodInstructionSentences(self):
        return self.goodInstructionSentences
    def getServingInstructionSentences(self):
        return self.servingInstructionSentences

    # Other Function Implementations */
    def addInstructionStep(self, newInstructionStep):
        self.instructionSteps.append(newInstructionStep)
        return self.instructionSteps

    ##
    # Function: Recipe::fillInstructionSentenceTokens
    # -----------------------------------------------
    # Splits all "good" instruction sentences in the recipe into their
    # component tokens and stores those tokens in the .tokensInSentence member
    # variable of their corresponding good instruction sentence.
    ##
    def fillInstructionSentenceTokens(self):
        for i in xrange(0, len(self.goodInstructionSentences)):
            instSent = self.goodInstructionSentences[i]
            instSent.tokensInSentence = re.split("([^a-zA-Z0-9_\''])", instSent.sentence)
            self.goodInstructionSentences[i] = instSent

    ##
    # Function: Recipe::divideInstructionSentences
    # --------------------------------------------
    # Splits full recipe steps into their component sentences.
    ##
    def divideInstructionSentences(self):
        for i in xrange(0, len(self.instructionSteps)):
            myInstructionStep = self.instructionSteps[i]
            stepText = myInstructionStep.allText.replace(". ", ". @ ")
            sentenceVec = stepText.split("@")
            for sentence in sentenceVec:
                sentence = sentence.strip()
                if (sentence==""):
                    continue
                newInstructionSentence = InstructionSentence()
                newInstructionSentence.sentence = sentence
                newInstructionSentence.tokensInSentence = newInstructionSentence.sentence.split(" ")

                myInstructionStep.instructionSentences.append(newInstructionSentence)
                myInstructionStep.sentenceStringVec.append(sentence)
            self.instructionSteps[i] = myInstructionStep

    ##
    # Function: Recipe::findFinalIngredientWords
    # ------------------------------------------
    # Make a flattened list of all words used in end seeds.
    ##
    def findFinalIngredientWords(self):
        self.finalIngredientWords = list(itertools.chain(*self.endSeeds))

    def findSeedsInInstructionSentences(self):
        servingWords = ["Serve", "serve", "Served", "served"]
        for i in xrange(0, len(self.instructionSteps)):
            myInstructionStep = self.instructionSteps[i]
            for j in xrange(0, len(myInstructionStep.instructionSentences)):
                myInstructionSent = myInstructionStep.instructionSentences[j]
                sentence = myInstructionSent.sentence
                myInstructionSent.isServingSentence = False
                sentenceTokens = [t for t in re.split("([^a-zA-Z0-9_\''])", sentence) if t not in ['', ' ']]

                previousPreviousToken = ""
                previousToken = ""
                currentToken = ""
                for trigram in zip(sentenceTokens, sentenceTokens[1:], sentenceTokens[2:]):
                    previousPreviousToken, previousToken, currentToken = trigram
                    if (previousToken in self.finalIngredientWords and \
                            not (previousPreviousToken in self.VALID_BEFORE_WORDS and \
                              currentToken in self.VALID_AFTER_WORDS)):
                        myInstructionSent.isGoodSentence = False
                        break
                    elif (previousToken in self.finalIngredientWords):
                        myInstructionSent.order1EndSeedsInside += previousToken
                        myInstructionSent.isGoodSentence = True
                    else:
                        myInstructionSent.isGoodSentence = True
                    if (previousPreviousToken in servingWords or previousToken in servingWords or currentToken in servingWords):
                        myInstructionSent.isServingSentence = True
                myInstructionSent.sentence = myInstructionSent.sentence.replace("\n", "")
                if (myInstructionSent.isGoodSentence):
                    self.goodInstructionSentences.append(myInstructionSent)
                if (myInstructionSent.isServingSentence):
                    self.servingInstructionSentences.append(myInstructionSent)
                myInstructionStep.instructionSentences[j] = myInstructionSent
            self.instructionSteps[i] = myInstructionStep

    def separateInstructions(self):
        myInstructionSteps = []
        if self.instructionsAreNumbered:
            index = 1
            boundsOfSteps = []
            while (True):
                stepStart1 = ""
                stepStart2 = ""
                stepStart3 = ""
                stepStart4 = ""
                if (index == 1):
                    stepStart1 = "\n" + str(index) + ". "
                else:
                    stepStart1 = " \n" + str(index) + ". "
                    stepStart2 = " \n\n" + str(index) + ". "
                    stepStart3 = " \n\n\n" + str(index) + ". "
                    stepStart4 = " \n\n\n\n" + str(index) + ". "

                officialStepStart = ""
                indexOfStart = self.allInstructionsText.find(stepStart1)
                officialStepStart = stepStart1
                if (indexOfStart==-1):
                    indexOfStart = self.allInstructionsText.find(stepStart2)
                    officialStepStart = stepStart2
                if (indexOfStart==-1):
                    indexOfStart = self.allInstructionsText.find(stepStart3)
                    officialStepStart = stepStart3
                if (indexOfStart==-1):
                    indexOfStart = self.allInstructionsText.find(stepStart4)
                    officialStepStart = stepStart4

                if not len(boundsOfSteps) == 0:
                    boundsOfSteps[index-2].append(indexOfStart)
                if (indexOfStart != -1):
                    indexOfRealStart = indexOfStart + len(officialStepStart)
                    boundOfStep = []
                    boundOfStep.append(indexOfRealStart)
                    boundsOfSteps.append(boundOfStep)
                else:
                    boundsOfLastStep = boundsOfSteps[len(boundsOfSteps)-1]
                    boundsOfLastStep.append(len(self.allInstructionsText)-1)
                    break
                index += 1
            for i in xrange(0, len(boundsOfSteps)):
                boundsOfStep = boundsOfSteps[i]
                newInstructionStep = InstructionStep()
                newInstructionStep.stepNumber = i+1
                newInstructionStep.allText = self.allInstructionsText[boundsOfStep[0] : boundsOfStep[1]]
                newInstructionStep.allText = newInstructionStep.allText.strip()
                myInstructionSteps.append(newInstructionStep)
        else:
            newInstructionStep = InstructionStep()
            newInstructionStep.stepNumber = 0
            newInstructionStep.allText = self.allInstructionsText.strip()
            if newInstructionStep.allText.startswith("\n"):
                newInstructionStep.allText = newInstructionStep.allText[0]
            myInstructionSteps.append(newInstructionStep)
        self.instructionSteps = myInstructionSteps
        return myInstructionSteps

    ##
    # Function: Recipe::fillEndSeeds
    # ------------------------------
    # Get the end seeds (last few words) of each ingredient
    # in the Recipe.
    ##
    def fillEndSeeds(self, endSeedLength):
        for i in xrange(0, len(self.ingredients)):
            myIngredient = self.ingredients[i]
            words = myIngredient.wordsInIngredient
            if len(words) <= endSeedLength:
                myIngredient.endSeed = tuple([word for word in words if not isUnit(word)])
            else:
                myIngredient.endSeed = words[-endSeedLength:]

            self.ingredients[i] = myIngredient
            self.endSeeds.append(myIngredient.endSeed)

    def isUnit(self, word):
        return word in self.NORMAL_UNITS or word in NORMAL_UNITS_PLURAL

    def findIngredientAmounts(self):
        for i in xrange(0, len(self.ingredients)):
            myIngredient = self.ingredients[i]
            line = myIngredient.entireLine
            if line[0].isdigit():
                numString = ""
                for j in xrange(1, len(line)-3):
                    previousChar = line[j-1]
                    currentChar = line[j]
                    nextChar = line[j+1]
                    nextNextChar = line[j+2]
                    nextNextNextChar = line[j+3]
                    if (previousChar.isdigit() and not nextChar.isdigit() and \
                            currentChar==' ' and not (nextChar=='t' and nextNextChar=='o' and nextNextNextChar==' ')):
                        numString += previousChar
                        break
                    elif (previousChar.isdigit() and not nextChar.isdigit() and (currentChar=='-' or currentChar=='x')):
                        for k in reversed(xrange(0, len(numString))):
                            if (numString[k] == ' '):
                                numString = numString[:-1]   # Used .erase() before
                                break
                            else:
                                numString = numString[:-1]   # Used .erase() before
                        break
                    else:
                        numString += previousChar
                myIngredient.amount = numString
            else:
                myIngredient.amount = "NO_LEADING_NUMBER"
            ingredients[i] = myIngredient

    def findIngredientUnits(self):
        for i in xrange(0, len(self.ingredients)):
            myIngredient = ingredients[i]
            line = myIngredient.entireLine
            myVec = stringSplit(line, " ")
            theUnits = ""
            unitsFound = False
            for i in xrange(0, len(myVec)):
                if (isUnit(myVec[i])):
                    theUnits = myVec[i]
                    unitsFound = True
                    break
                if (unitsFound):
                    break
            myIngredient.units = theUnits
            ingredients[i] = myIngredient

    def fillIngredientWords(self):
        for i in xrange(0, len(self.ingredients)):
            myIngredient = ingredients[i]
            line = myIngredient.entireLine
            wordsInIngredient = stringSplit(line, " ")
            for i in xrange(0, len(wordsInIngredient)):
                word = wordsInIngredient[i]
                newWord = ""
                for ch in word:
                    if not ch.isalpha():
                        newWord += " "
                    else:
                        newWord += ch
                wordsInIngredient[i] = newWord

            ingredientWords = []
            validWord = True
            for i in xrange(0, len(wordsInIngredient)):
                currentWord = wordsInIngredient[i]
                for ch in currentWord:
                    if ch.isdigit():
                        validWord = False
                if validWord:
                    word = wordsInIngredient[i]
                    newWord = ""
                    for ch in word:
                        if (ch==','):
                            newWord += ""
                        elif (ch=='-'):
                            newWord += " "
                        elif not ch.isalpha():
                            newWord += " "
                        else:
                            newWord += ch
                    newWord = newWord.strip()
                    wordSplit = newWord.split(" ")
                    for newWord2 in wordSplit:
                        ingredientWords.append(newWord2)
                validWord = True

            nonUnitIngredientWords = []
            for word in ingredientWords:
                if not isUnit(word):
                    nonUnitIngredientWords += word
            myIngredient.wordsInIngredient = ingredientWords
            myIngredient.nonUnitWordsInIngredient = nonUnitIngredientWords
            ingredients[i] = myIngredient

    def separateIngredients(self, adjectives):
        ingredientsText = self.allIngredientsText
        myIngredients = []
        payAttention = False
        inParentheses = False
        pastComma = False
        ingredientsStarted = False
        wordsInIngredient = 0
        currentWord = ""

        for currentIndex in xrange(1, len(ingredientsText)-2):
            previousChar = ingredientsText[currentIndex-1]
            currentChar = ingredientsText[currentIndex]
            nextChar = ingredientsText[currentIndex+1]

            if (previousChar.isalpha()):
                currentWord += previousChar
            elif (currentWord != ""):
                wordsInIngredient += 1
                currentWord = ""

            if (previousChar == '\n' and currentChar.isdigit() and not inParentheses):
                wordsInIngredient = 0
                payAttention = True
                pastComma = False
                ingredientsStarted = True
                newIngredient = Ingredient()
                myIngredients.append(newIngredient)
            elif (currentIndex==1 and previousChar.isdigit()):
                wordsInIngredient = 0
                payAttention = True
                pastComma = False
                ingredientsStarted = True
                newIngredient = Ingredient()
                myIngredients.append(newIngredient)
            elif (previousChar == '\n' and currentChar.isupper() and ingredientsStarted and not inParentheses):
                wordsInIngredient = 0
                payAttention = True
                pastComma = False
                ingredientsStarted = True
                newIngredient = Ingredient()
                myIngredients.append(newIngredient)
            elif (ingredientsStarted):
                if (currentChar == ',' and not inParentheses and not (currentWord in adjectives and wordsInIngredient < 2)):
                    payAttention = False
                    pastComma = True

                elif (currentChar == '('):
                    payAttention = False
                    inParentheses = True
                elif (currentChar == ')'):
                    inParentheses = False
                    if not pastComma:
                        payAttention = True

            if (payAttention):
                currentIngredient = myIngredients[len(myIngredients)-1]
                currentLine = currentIngredient.entireLine
                if (currentChar == ')' or (currentChar == ' ' and currentLine[len(currentLine)-1] == ' ')):
                    continue
                if (currentIndex==1 and previousChar.isdigit()):
                    currentLine += previousChar
                if (currentChar != '\n'):
                    currentLine += currentChar
                if (currentIndex==len(ingredientsText)-2 and nextChar.isalpha()):
                    currentLine += nextChar
                currentIngredient.entireLine = currentLine
                myIngredients[len(myIngredients)-1] = currentIngredient
        ingredients = myIngredients

    ##
    # Function: Recipe::findAndSetNumServings
    # ---------------------------------
    # Find the number of servings this recipe makes.
    ##
    def findAndSetNumServings(self):
        numServings = None
        lineWordLists = [line.strip().split() for line in self.allRecipeText.split('\n')]
        for lineWords in lineWordLists:
            if lineWords != [] and lineWords[0] in ["MAKES", "SERVES"]:
                numbers = [s for s in line if s.isdigit()]
                if numbers != []:
                    numServings = numbers[0]

        # If the recipe does not mention how many servings it makes,
        # arbitrarily choose 10
        if numServings == None:
            numServings = 10

        self.numServings = numServings

    ##
    # Function: Recipe::findAndSetTitle
    # ---------------------------------
    # Find the title of this recipe in self.allRecipeText and set
    # self.name equal to that title.
    ##
    def findAndSetTitle(self):
        lines = self.allRecipeText.split('\n')
        title = ''
        for ind in xrange(0, len(lines)-1):
            line1 = lines[ind]
            line2 = lines[ind+1]
            if line1 != '' and line1[0].islower():
                title += line1
            elif line1 != '' and line2 == '' and title != '':
                self.name = title

                # Delete the title from self.allRecipeText
                self.allRecipeText = "\n".join(lines[ind:])
                break

    ##
    # Function: Recipe::splitIngredientsInstructionText
    # -------------------------------------------------
    # Divides a recipe's text into the 'ingredients' and 'instructions'
    # sections, setting the recipe's instruction text member variable
    # equal to all of the instruction text and returning all
    # of the ingredients text.
    ##
    def splitIngredientsInstructionText(self):
        allIngredientsText = "\n"
        recipeText = self.allRecipeText
        inMakeServeLine = False
        belowMakeServeLine = False
        haveSeenNumbers = False
        for currentIndex in xrange(0, len(recipeText)-3):
            char1 = recipeText[currentIndex]
            char2 = recipeText[currentIndex+1]
            char3 = recipeText[currentIndex+2]

            # See if we just entered in the make/serve line
            makesOrServes = self.getWord(currentIndex, recipeText)
            if makesOrServes == "MAKES" or makesOrServes == "SERVES":
                haveSeenNumbers = False
                inMakeServeLine = True
                belowMakeServeLine = False

            if inMakeServeLine and char1 == '\n':
                # make/serve line just ended
                inMakeServeLine = False
                belowMakeServeLine = True
            elif belowMakeServeLine:
                if char1.isdigit():
                    haveSeenNumbers = True
                if allIngredientsText == "" and char1 == '\n':
                    pass
                else:
                    atNewLine = (char1 == '\n')
                    nextWordIsInstructionVerb = (self.getWord(currentIndex+1, recipeText) in self.INSTRUCTION_VERBS)
                    nextLineIsNonNumberedInstruction = (atNewLine and haveSeenNumbers and nextWordIsInstructionVerb)
                    nextLineIsNumberedInstruction = (atNewLine and char2.isdigit() and char3 == '.')
                    nextLineIsInstruction = (nextLineIsNonNumberedInstruction or nextLineIsNumberedInstruction)
                    if nextLineIsInstruction:
                        self.allInstructionsText = recipeText[currentIndex:]
                        self.instructionsAreNumbered = nextLineIsNumberedInstruction
                        break
                    else:
                        allIngredientsText += char1
            else:
                # We're above the makeServe line
                pass
        self.allIngredientsText = allIngredientsText

    ##
    # Function: Recipe::getWord
    # -------------------------
    # Given a character index in the full recipe text, return the next
    # full word.
    ##
    def getWord(self, currentIndex, recipeText):
        returnWord = ""
        while True:
            if currentIndex >= len(recipeText):
                break
            currentChar = recipeText[currentIndex]
            if not currentChar.isalpha():
                break
            returnWord += currentChar
            currentIndex += 1
        return returnWord


    ##################################
    ### Printing-related functions ###
    ##################################

    def printGoodSentences(self):
        print self.name
        print "-----------------------------------------"
        for i in xrange(0, len(self.goodInstructionSentences)):
            myInstructionSent = self.goodInstructionSentences[i]
            if len(myInstructionSent.order1EndSeedsInside)==0:
                continue
            sentence = myInstructionSent.sentence
            sentence = sentence.replace("\n", "")
            print "   Sentence: ", sentence
            print "      Seeds: ", myInstructionSent.order1EndSeedsInside
        print "\n\n"

    def printAllInstructionText(self):
        print self.name
        print "------------------------"
        print "--- Instruction Text ---"
        print "------------------------"
        print self.allInstructionsText, "\n\n"

    def printAllIngredientsText(self):
        print self.name
        print "------------------------"
        print "--- Ingredients Text ---"
        print "------------------------"
        print self.allIngredientsText, "\n\n"

    def printAllInstructionSteps(self):
        print self.name
        print "------------------------------------------"
        i=1
        for iStep in self.instructionSteps:
            print "   Step ", i, ": ", iStep.allText
            i += 1
        print "\n\n"

    def printEndSeeds(self):
        print self.name
        print "---------------------------------"
        for endSeed in self.endSeeds:
            print "   ", endSeed

    def printIngredients(self):
        for i in xrange(0, len(self.ingredients)):
            print "   ", ingredients[i].entireLine
            print "        Amount: ", ingredients[i].amount
            print "        Units: ", ingredients[i].units
            print "        Words: ", ingredients[i].wordsInIngredient
            print "        Non-Unit Words: ", ingredients[i].nonUnitWordsInIngredient
            print "        End Seed: ", ingredients[i].endSeed
        print "   End Seeds:"
        for endSeed in self.endSeeds:
            print "   ", endSeed