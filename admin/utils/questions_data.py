from typing import List, Dict, Any

def get_networking_questions() -> List[Dict[str, Any]]:
    """
    Returns a list of default networking questions for the application.
    
    Each question has the following structure:
    - numb: Question number
    - question: The actual question text
    - answer: The correct answer option
    - options: List of possible answer options
    - explanation: Optional explanation of the correct answer
    
    Returns:
        List[Dict[str, Any]]: A list of question dictionaries
    """
    return [
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
            "explanation": "An Autonomous System is a collection of networks under a single administrative domain."
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
            "explanation": "RIP (Routing Information Protocol) is one of the oldest distance-vector routing protocols."
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
            "explanation": "RIP uses hop count as its routing metric, with a maximum of 15 hops."
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
            "explanation": "RIP has a maximum hop count of 15. Destinations requiring 16 or more hops are considered unreachable."
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
            "explanation": "The command 'ip ospf 1 area 0' enables OSPF process 1 on the interface and assigns it to area 0."
        }
    ]
