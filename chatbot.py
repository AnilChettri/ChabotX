import json
import random
import spacy
from spacy.matcher import PhraseMatcher


class Chatbot:
    def __init__(self, intents_file='intents.json', model_name='en_core_web_sm'):
        """
        Initialize the chatbot:
         - Load the spaCy model
         - Prepare the phrase matchers for each intent pattern
         - Load the intents from a JSON file
        """
        self.nlp = spacy.load(model_name)
        with open(intents_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.intents = data['intents']

        # Initialize the phrase matcher
        self.matcher = PhraseMatcher(self.nlp.vocab, attr='LOWER')
        self._build_matchers()

    def _build_matchers(self):
        """
        For each intent, create phrase patterns to match them using spaCy's PhraseMatcher.
        """
        for intent in self.intents:
            tag = intent['tag']
            if "patterns" in intent:
                phrase_patterns = [self.nlp.make_doc(pattern) for pattern in intent['patterns']]
                self.matcher.add(tag, phrase_patterns)

    def classify_intent(self, user_text):
        """
        Use spaCy's PhraseMatcher to find which intent best matches the user's text.
        Returns the best matching 'tag' or 'fallback' if none matched.
        """
        doc = self.nlp(user_text)
        matches = self.matcher(doc)

        # Debugging: Log matched patterns
        print(f"[Debug] User Input: {user_text}")
        print(f"[Debug] Matches: {[(self.nlp.vocab.strings[m_id], start, end) for m_id, start, end in matches]}")

        # Tally matches by intent
        intent_counts = {}
        for match_id, start, end in matches:
            intent_tag = self.nlp.vocab.strings[match_id]  # Get string representation
            intent_counts[intent_tag] = intent_counts.get(intent_tag, 0) + 1

        if not intent_counts:
            return "fallback"

        # Return the intent with the highest match count
        return max(intent_counts, key=intent_counts.get)

    def get_response(self, intent_tag):
        """
        Return a random response from the matched intent, or fallback if not found.
        """
        for intent in self.intents:
            if intent['tag'] == intent_tag:
                return random.choice(intent['responses'])

        # Fallback if no direct match (shouldn't happen if we have a fallback in the JSON)
        for intent in self.intents:
            if intent['tag'] == "fallback":
                return random.choice(intent['responses'])

        # In case fallback is missing from JSON
        return "I'm not sure how to respond to that."

    def chat(self, user_text):
        """
        Main method to handle user input:
         1) Classify intent
         2) Generate a suitable response
        """
        # Classify the user's intent
        intent_tag = self.classify_intent(user_text)

        # Get the response for the detected intent
        response = self.get_response(intent_tag)

        # Debugging: Ensure fallback is not added unnecessarily
        print(f"[Debug] Intent Tag: {intent_tag}")
        print(f"[Debug] Response: {response}")

        return response


# Quick test when run directly
if __name__ == "__main__":
    bot = Chatbot()
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Goodbye!")
            break
        bot_response = bot.chat(user_input)
        print("Bot:", bot_response)
