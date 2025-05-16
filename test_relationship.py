"""
Test script to verify that the relationship between models works correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from admin.models import AdminUser, AdminScore
from user.models import User, Score
from __init__ import db

def print_separator():
    print("\n" + "-" * 50 + "\n")

# Test getting a user and their scores using the admin models
def test_admin_user_scores():
    print("Testing Admin User -> Scores relationship:")
    try:
        # Get the first user
        user = AdminUser.query.first()
        if user:
            print(f"Found user: {user.username} (ID: {user.id})")
            # Get scores for this user using our custom method
            scores = user.get_scores()
            print(f"User has {len(scores)} scores:")
            for score in scores[:3]:  # Limit to 3 scores for cleaner output
                print(f"- Score: {score.score}, Category: {score.category}, Date: {score.date_attempted}")
        else:
            print("No users found")
    except Exception as e:
        print(f"Error testing admin user scores: {str(e)}")

# Test getting a score and its user using the admin models
def test_admin_score_user():
    print("Testing Admin Score -> User relationship:")
    try:
        # Get the first score
        score = AdminScore.query.first()
        if score:
            print(f"Found score: {score.score} (ID: {score.id})")
            # Get user for this score using our custom method
            user = score.get_user()
            if user:
                print(f"Score belongs to user: {user.username} (ID: {user.id})")
            else:
                print("No user found for this score")
        else:
            print("No scores found")
    except Exception as e:
        print(f"Error testing admin score user: {str(e)}")

# Test getting a user and their scores using the user models
def test_user_scores():
    print("Testing User -> Scores relationship:")
    try:
        # Get the first user
        user = User.query.first()
        if user:
            print(f"Found user: {user.username} (ID: {user.id})")
            # Get scores for this user using the standard relationship
            scores = user.scores
            print(f"User has {len(scores)} scores:")
            for score in scores[:3]:  # Limit to 3 scores for cleaner output
                print(f"- Score: {score.score}, Category: {score.category}, Date: {score.date_attempted}")
        else:
            print("No users found")
    except Exception as e:
        print(f"Error testing user scores: {str(e)}")

# Test getting a score and its user using the user models
def test_score_user():
    print("Testing Score -> User relationship:")
    try:
        # Get the first score
        score = Score.query.first()
        if score:
            print(f"Found score: {score.score} (ID: {score.id})")
            # Get user for this score using the standard relationship
            user = score.user
            if user:
                print(f"Score belongs to user: {user.username} (ID: {user.id})")
            else:
                print("No user found for this score")
        else:
            print("No scores found")
    except Exception as e:
        print(f"Error testing score user: {str(e)}")

if __name__ == "__main__":
    print("Running relationship tests...")
    
    # Test admin models
    test_admin_user_scores()
    print_separator()
    test_admin_score_user()
    print_separator()
    
    # Test user models
    test_user_scores()
    print_separator()
    test_score_user()
    
    print("\nTests completed!")
