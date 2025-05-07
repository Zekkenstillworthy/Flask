from .models import db, Question

class DataUtility:
    @staticmethod
    def import_default_questions():
        """Import default questions if the database is empty"""
        if Question.query.count() == 0:
            try:
                default_questions = [
                    {
                        "numb": 1,
                        "question": "What is an Autonomous System (AS)?",
                        "answer": "b. A collection of networks under one administration",
                        "options": [
                            "a. A group of devices sharing a MAC address",
                            "b. A collection of networks under one administration",
                            "c. A backup route in OSPF",
                            "d. A network type for stub areas"
                        ],
                        "explanation": ""
                    },
                    {
                        "numb": 2,
                        "question": "What does RIP stand for?",
                        "answer": "b. Routing Information Protocol",
                        "options": [
                            "a. Routing Internet Protocol",
                            "b. Routing Information Protocol",
                            "c. Remote Information Path",
                            "d. Router Internal Path"
                        ],
                        "explanation": ""
                    },
                    {
                        "numb": 3,
                        "question": "What metric does RIP use to determine the best route?",
                        "answer": "c. Hop Count",
                        "options": [
                            "a. Bandwidth",
                            "b. Latency",
                            "c. Hop Count",
                            "d. Cost"
                        ],
                        "explanation": ""
                    },
                    {
                        "numb": 4,
                        "question": "What is the maximum hop count RIP can handle?",
                        "answer": "b. 15",
                        "options": [
                            "a. 10",
                            "b. 15",
                            "c. 20",
                            "d. 25"
                        ],
                        "explanation": ""
                    },
                    {
                        "numb": 5,
                        "question": "Which command configures OSPF on an interface?",
                        "answer": "b. ip ospf 1 area 0",
                        "options": [
                            "a. ip ospf network",
                            "b. ip ospf 1 area 0",
                            "c. configure ospf area 0",
                            "d. network ospf-enable"
                        ],
                        "explanation": ""
                    }
                ]
                
                for q_data in default_questions:
                    question = Question(
                        numb=q_data["numb"],
                        question=q_data["question"],
                        answer=q_data["answer"],
                        options=q_data["options"],
                        explanation=q_data.get("explanation", ""),
                        category="riddle"
                    )
                    db.session.add(question)
                    
                db.session.commit()
                print("Imported default questions successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Error importing default questions: {e}")
