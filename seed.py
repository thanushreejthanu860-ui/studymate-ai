import json
from datetime import date
from app import app, db
from models import User, Lecture, Question
from werkzeug.security import generate_password_hash

LECTURES = [
    {
        "title": "Introduction to AI",
        "video_url": "https://www.youtube.com/watch?v=ad79nYk2keg",
        "notes": (
            "Artificial Intelligence (AI) is the simulation of human intelligence by machines. "
            "AI systems can perform tasks like reasoning, learning, problem-solving, perception, and language understanding. "
            "AI is broadly divided into Narrow AI (designed for a specific task, like a chess engine) and General AI (hypothetical human-level intelligence). "
            "Key branches include Machine Learning, Natural Language Processing, Computer Vision, and Robotics. "
            "The Turing Test, proposed by Alan Turing in 1950, is a measure of machine intelligence. "
            "AI applications include virtual assistants, recommendation systems, fraud detection, and self-driving cars."
        ),
        "questions": [
            {
                "text": "What does AI stand for?",
                "option_a": "Automated Integration",
                "option_b": "Artificial Intelligence",
                "option_c": "Automated Intelligence",
                "option_d": "Artificial Integration",
                "correct_option": "B",
                "explanation": "AI stands for Artificial Intelligence — the simulation of human intelligence by machines.",
                "wrong_reasons": json.dumps({
                    "A": "Automated Integration is a software engineering term unrelated to AI.",
                    "C": "Automated Intelligence is not a recognised term in computer science.",
                    "D": "Artificial Integration has no meaning in the context of AI."
                })
            },
            {
                "text": "Which of the following is an example of Narrow AI?",
                "option_a": "A robot that can do any human job",
                "option_b": "A chess-playing program",
                "option_c": "A system with human-level general reasoning",
                "option_d": "A biological brain",
                "correct_option": "B",
                "explanation": "A chess-playing program is Narrow AI because it is designed for one specific task.",
                "wrong_reasons": json.dumps({
                    "A": "A robot that can do any human job describes General AI, which does not yet exist.",
                    "C": "Human-level general reasoning is the definition of General AI, not Narrow AI.",
                    "D": "A biological brain is not an AI system."
                })
            },
            {
                "text": "Who proposed the Turing Test?",
                "option_a": "John McCarthy",
                "option_b": "Marvin Minsky",
                "option_c": "Alan Turing",
                "option_d": "Geoffrey Hinton",
                "correct_option": "C",
                "explanation": "Alan Turing proposed the Turing Test in 1950 as a measure of machine intelligence.",
                "wrong_reasons": json.dumps({
                    "A": "John McCarthy coined the term 'Artificial Intelligence' but did not propose the Turing Test.",
                    "B": "Marvin Minsky was a pioneer in AI but is not associated with the Turing Test.",
                    "D": "Geoffrey Hinton is known for deep learning, not the Turing Test."
                })
            },
        ]
    },
    {
        "title": "Machine Learning",
        "video_url": "https://www.youtube.com/watch?v=ukzFI9rgwfU",
        "notes": (
            "Machine Learning (ML) is a subset of AI that enables systems to learn from data without being explicitly programmed. "
            "The three main types are: Supervised Learning (labelled data, e.g. spam detection), "
            "Unsupervised Learning (unlabelled data, e.g. customer clustering), and "
            "Reinforcement Learning (learning by reward and penalty, e.g. game-playing agents). "
            "Key concepts include features (input variables), labels (output variables), training set, test set, and model evaluation. "
            "Overfitting occurs when a model learns the training data too well and performs poorly on new data. "
            "Common algorithms include Linear Regression, Decision Trees, k-Nearest Neighbours, and Support Vector Machines."
        ),
        "questions": [
            {
                "text": "Which type of ML uses labelled training data?",
                "option_a": "Unsupervised Learning",
                "option_b": "Reinforcement Learning",
                "option_c": "Supervised Learning",
                "option_d": "Transfer Learning",
                "correct_option": "C",
                "explanation": "Supervised Learning trains on labelled data where the correct output is already known.",
                "wrong_reasons": json.dumps({
                    "A": "Unsupervised Learning works with unlabelled data — there are no predefined correct outputs.",
                    "B": "Reinforcement Learning learns through rewards and penalties, not labelled datasets.",
                    "D": "Transfer Learning reuses a pre-trained model; it is not defined by labelled data alone."
                })
            },
            {
                "text": "What is overfitting in machine learning?",
                "option_a": "When a model is too simple to learn patterns",
                "option_b": "When a model learns training data too well and fails on new data",
                "option_c": "When a model is trained on too little data",
                "option_d": "When a model uses too many features",
                "correct_option": "B",
                "explanation": "Overfitting means the model memorises the training data and cannot generalise to unseen examples.",
                "wrong_reasons": json.dumps({
                    "A": "A model that is too simple suffers from underfitting, not overfitting.",
                    "C": "Training on too little data can cause overfitting but is not the definition of it.",
                    "D": "Using many features can contribute to overfitting but is not the definition."
                })
            },
            {
                "text": "Which algorithm is commonly used for classification and regression tasks?",
                "option_a": "k-Means Clustering",
                "option_b": "Principal Component Analysis",
                "option_c": "Decision Tree",
                "option_d": "DBSCAN",
                "correct_option": "C",
                "explanation": "Decision Trees can handle both classification and regression problems.",
                "wrong_reasons": json.dumps({
                    "A": "k-Means is an unsupervised clustering algorithm, not used for labelled classification.",
                    "B": "PCA is a dimensionality reduction technique, not a classification or regression algorithm.",
                    "D": "DBSCAN is a density-based clustering algorithm used in unsupervised learning."
                })
            },
        ]
    },
    {
        "title": "Deep Learning",
        "video_url": "https://www.youtube.com/watch?v=6M5VXKLf4D4",
        "notes": (
            "Deep Learning is a subset of Machine Learning that uses multi-layered neural networks to learn representations from data. "
            "The word 'deep' refers to the many hidden layers in the network. "
            "Deep Learning excels at tasks like image recognition, speech recognition, and natural language processing. "
            "Key architectures include Convolutional Neural Networks (CNNs) for images, "
            "Recurrent Neural Networks (RNNs) for sequences, and Transformers for language. "
            "Training requires large datasets and significant computing power (GPUs). "
            "Backpropagation and gradient descent are used to update the network weights during training. "
            "Common activation functions are ReLU, Sigmoid, and Softmax."
        ),
        "questions": [
            {
                "text": "What does 'deep' refer to in Deep Learning?",
                "option_a": "The complexity of the data",
                "option_b": "The number of hidden layers in the network",
                "option_c": "The depth of the training dataset",
                "option_d": "The difficulty of the problem being solved",
                "correct_option": "B",
                "explanation": "'Deep' refers to the many hidden layers stacked in a neural network.",
                "wrong_reasons": json.dumps({
                    "A": "Data complexity is not what 'deep' describes in this context.",
                    "C": "Dataset depth is not a standard term; 'deep' refers to network architecture.",
                    "D": "Problem difficulty does not determine whether a model is called 'deep'."
                })
            },
            {
                "text": "Which architecture is best suited for image recognition?",
                "option_a": "Recurrent Neural Network (RNN)",
                "option_b": "Transformer",
                "option_c": "Convolutional Neural Network (CNN)",
                "option_d": "Autoencoder",
                "correct_option": "C",
                "explanation": "CNNs use convolutional filters to detect spatial patterns, making them ideal for images.",
                "wrong_reasons": json.dumps({
                    "A": "RNNs are designed for sequential data like text or time series, not images.",
                    "B": "Transformers are primarily used for language tasks, though vision transformers exist.",
                    "D": "Autoencoders are used for compression and anomaly detection, not primarily image classification."
                })
            },
            {
                "text": "Which algorithm is used to update weights during deep learning training?",
                "option_a": "k-Means",
                "option_b": "Backpropagation with gradient descent",
                "option_c": "Random Forest",
                "option_d": "Naive Bayes",
                "correct_option": "B",
                "explanation": "Backpropagation computes gradients and gradient descent uses them to update network weights.",
                "wrong_reasons": json.dumps({
                    "A": "k-Means is a clustering algorithm unrelated to neural network training.",
                    "C": "Random Forest is an ensemble ML method, not a neural network training algorithm.",
                    "D": "Naive Bayes is a probabilistic classifier, not a weight-update method."
                })
            },
        ]
    },
    {
        "title": "Neural Networks",
        "video_url": "https://www.youtube.com/watch?v=aircAruvnKk",
        "notes": (
            "A Neural Network is a computational model inspired by the human brain. "
            "It consists of layers of interconnected nodes called neurons. "
            "The three main layer types are: Input Layer (receives raw data), "
            "Hidden Layers (learn intermediate representations), and Output Layer (produces the final prediction). "
            "Each connection has a weight that is adjusted during training. "
            "An activation function decides whether a neuron should fire. "
            "Common activation functions: Sigmoid (outputs 0-1), ReLU (outputs 0 or the input if positive), Softmax (outputs probabilities summing to 1). "
            "A perceptron is the simplest neural network with a single layer. "
            "Bias is an extra parameter added to each neuron to shift the activation function."
        ),
        "questions": [
            {
                "text": "What is the role of the hidden layer in a neural network?",
                "option_a": "To receive raw input data",
                "option_b": "To produce the final output",
                "option_c": "To learn intermediate representations of the data",
                "option_d": "To store the training dataset",
                "correct_option": "C",
                "explanation": "Hidden layers transform the input through learned weights to extract useful features.",
                "wrong_reasons": json.dumps({
                    "A": "Receiving raw input is the role of the Input Layer, not the hidden layer.",
                    "B": "Producing the final output is the role of the Output Layer.",
                    "D": "Neural networks do not store the training dataset inside their layers."
                })
            },
            {
                "text": "Which activation function outputs values between 0 and 1?",
                "option_a": "ReLU",
                "option_b": "Softmax",
                "option_c": "Sigmoid",
                "option_d": "Tanh",
                "correct_option": "C",
                "explanation": "The Sigmoid function maps any input to a value between 0 and 1, useful for binary classification.",
                "wrong_reasons": json.dumps({
                    "A": "ReLU outputs 0 for negative inputs and the raw value for positive inputs, not bounded to 1.",
                    "B": "Softmax outputs a probability distribution across multiple classes, not a single 0-1 value.",
                    "D": "Tanh outputs values between -1 and 1, not 0 and 1."
                })
            },
            {
                "text": "What is a perceptron?",
                "option_a": "A multi-layer deep neural network",
                "option_b": "The simplest neural network with a single layer",
                "option_c": "A type of activation function",
                "option_d": "A method for reducing overfitting",
                "correct_option": "B",
                "explanation": "A perceptron is the simplest neural network, consisting of a single layer of weights.",
                "wrong_reasons": json.dumps({
                    "A": "A multi-layer network is called a Multi-Layer Perceptron (MLP), not a perceptron.",
                    "C": "A perceptron is a network architecture, not an activation function.",
                    "D": "Techniques like dropout or regularisation reduce overfitting; a perceptron does not."
                })
            },
        ]
    },
]


def seed():
    with app.app_context():
        db.create_all()

        # Clear existing data
        from models import AttemptAnswer, Attempt, Watched, Explainer
        AttemptAnswer.query.delete()
        Attempt.query.delete()
        Watched.query.delete()
        Explainer.query.delete()
        Question.query.delete()
        Lecture.query.delete()
        User.query.delete()
        db.session.commit()

        # Demo student
        student = User(
            name="Alex Johnson",
            email="student@college.edu",
            password_hash=generate_password_hash("student123"),
            role="student",
            student_id="STU-2024-001",
            phone="+1-555-0101",
            course="BSc Computer Science",
            semester="3",
            department="Computer Science",
            college="Faculty of Engineering",
            joined=date(2024, 9, 1)
        )

        # Demo lecturer
        lecturer = User(
            name="Dr. Sarah Williams",
            email="lecturer@college.edu",
            password_hash=generate_password_hash("lecturer123"),
            role="lecturer",
            joined=date(2023, 1, 15)
        )

        db.session.add_all([student, lecturer])
        db.session.flush()

        for lec_data in LECTURES:
            lecture = Lecture(
                title=lec_data["title"],
                notes=lec_data["notes"],
                video_url=lec_data["video_url"],
                lecturer_id=lecturer.id
            )
            db.session.add(lecture)
            db.session.flush()

            for q in lec_data["questions"]:
                question = Question(
                    lecture_id=lecture.id,
                    text=q["text"],
                    option_a=q["option_a"],
                    option_b=q["option_b"],
                    option_c=q["option_c"],
                    option_d=q["option_d"],
                    correct_option=q["correct_option"],
                    explanation=q["explanation"],
                    wrong_reasons=q["wrong_reasons"]
                )
                db.session.add(question)

        db.session.commit()
        print("Database seeded successfully.")
        print("  Student:  student@college.edu / student123")
        print("  Lecturer: lecturer@college.edu / lecturer123")


if __name__ == "__main__":
    seed()
