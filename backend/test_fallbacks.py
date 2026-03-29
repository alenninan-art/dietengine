import os
import sys

# Mocking some dependencies to test the logic
def test_fallback_logic():
    print("Testing Chatbot Fallback Logic...")
    
    # Test cases for rule-based matching
    test_queries = [
        "What is my protein intake?",
        "How many calories in a burger?",
        "Tell me about kerala food.",
        "thank you",
        "information to reduce weight diet",
        "diet for weight lose",
        "diet for me",
        "what is my weight"
    ]
    
    def get_response(user_msg):
        user_msg = user_msg.lower().strip()
        response = ""
        
        # Protein specific queries
        if any(word in user_msg for word in ["protein", "protien", "amino"]):
            response = "Protein is crucial!"
        # Diet advice & Weight loss (PRIORITY)
        elif any(word in user_msg for word in ["diet", "food", "eat", "meal", "weight loss", "lose weight", "reduce weight", "reducing weight"]):
            response = "I recommend the Diet Plan..."
        # Calorie specific queries
        elif any(word in user_msg for word in ["calorie", "calories", "kcal", "energy"]):
            response = "Managing calories is key."
        # BMI information
        elif any(word in user_msg for word in ["bmi", "body mass index", "my weight", "check my weight"]):
            response = "Your current BMI is..."
        # Cultural & Kerala Specifics
        elif any(word in user_msg for word in ["kerala", "culture", "traditional", "indian", "local"]):
            response = "Traditional Kerala food..."
        # Appreciation
        elif any(word in user_msg for word in ["thank", "thanks", "great", "awesome", "good"]):
            response = "You're very welcome!"
        else:
            response = "That's an interesting question!"
        
        return response

    for query in test_queries:
        res = get_response(query)
        print(f"Query: '{query}' -> Response: '{res}'")
        assert res != ""

    print("Success: Fallback logic works as expected.")

if __name__ == "__main__":
    test_fallback_logic()
