from chatterbot.adapters.logic import LogicAdapter
from chatterbot.conversation import Statement

from chatterbot.utils.stop_words import StopWordsManager
from chatterbot.utils.pos_tagger import POSTagger

import subprocess


class DeveloperAssistant(LogicAdapter):
    """
    The DeveloperAssistant logic adapter provides a set of tools
    that can help a developer program. Currently, only the following
    features are supported:
    1) Running Python programs
    """

    def __init__(self, **kwargs):
        super(DeveloperAssistant, self).__init__(**kwargs)

        # Initializing variables
        self.program_path = ""
        self.program_name = ""

        self.stopwords = StopWordsManager()
        self.tagger = POSTagger()
        self.conversation = []

    def process(self, statement):
        """
        Assuming the user inputed statement is a
        request for the developer assistant, parse
        the request and determine the appropriate
        action to be used.
        """
        # Getting the confidence of this adapter's ability to respond
        # @TODO: This should not be as simple as a NaiveBayesClassifier
        #   but should instead use some way to determine how likely it
        #   is that the user is interacting with this logic adapter.
        confidence = self.classify(statement.text)

        # Getting the conversation
        try:
            self.conversation = self.context.conversation
        except:
            pass

        # Getting the stage of interaction with the user
        stage = self.determine_stage_of_interaction(statement)

        if stage == 1:
            return confidence, Statement("What is the absolute path to " + self.program_name + "?")
        elif stage == 3:
            # Run program
            self.context.io.process_response(Statement("Running " + self.program_name + "..."))
            subprocess.Popen("python " + self.program_path + self.program_name, shell=True)

            # Resetting global variables
            self.program_name = ""
            self.program_path = ""

            # Return a response
            return confidence, Statement("The program has finished running")

        return 0, Statement("")

    def classify(self, input_text):
        """
        Classifies the incoming test to determine whether this logic adapter
        should be used to respond to the user's input.
        """
        # @TODO: Restructure this to look in all conversation statements to
        #   determine whether the developer assistant is called before this
        for token in self.tagger.tokenize(input_text):
            if "run" in token.lower():
                return 1

        return 0

    def determine_stage_of_interaction(self, input_statement):
        """
        Determines at which point in the interaction with
        the user chatterbot is.
        """
        user_has_given_name = False
        user_has_given_path = False
        stage = 0

        # Parsing through the conversation with chatterbot looking for information
        for conversation_index in range(0, len(self.conversation)):
            if conversation_index == 0:
                user_input = input_statement.text
            else:
                user_input = self.conversation[len(self.conversation) - conversation_index][0]

            if self.extract_name(user_input) is not "" and user_has_given_name == False:
                user_has_given_name = True
                stage += 1
                self.program_name = self.extract_name(user_input)

            if self.extract_path(user_input) is not "" and user_has_given_path == False:
                user_has_given_path = True
                stage += 2
                self.program_path = self.extract_path(user_input)

        print("name: " + self.program_name)
        print("stage: " + str(stage))

        return stage

    def extract_name(self, user_input):
        """
        Return the program's name if it is included somewhere in the
        conversation.
        """
        name = ""

        # The following assumes that the user_input is simply: "run program_x"
        # @TODO: Change this to a more advanced parsing of the user_input. It
        #   requires additional functions within the chatterbot.utils module
        #   and some more thought on how to implement a better system
        has_asked_run = False
        for token in self.tagger.tokenize(user_input):
            if has_asked_run:
                name = token
                break

            if "run" in token:
                has_asked_run = True

        return name

    def extract_path(self, user_input):
        """
        Return the program's path if it is included somewhere in the
        conversation.
        """
        path = ""

        # Identifies the path if one is in user_input
        # @TODO: Rewrite to remove false positives (which can be created
        #   easily with the current implementation)
        for word in self.tagger.tokenize(user_input):
            if "/" in word:
                path = word
                break

        return path
