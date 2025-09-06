from sklearn.metrics import accuracy_score, recall_score

def extract_metrics(filename: str):
    with open(filename, "r") as f:
        score = {}
        index = 0
        for raw in f:
            line = raw.strip() # remove leading/trailing whitespace
            if not line:
                continue
            if line.startswith("Result:"):
                result = line.split("Result:", 1)[1].strip()
                
                parts = [part.strip() for part in result.split(",", 1)]
                if len(parts) == 2:
                    classification, confidence = parts
                    score[index]["classification"] = classification
                    try:
                        score[index]["confidence"] = float(confidence)
                    except ValueError:
                        score[index]["confidence"] = None
                    index += 1
                else:
                    print(f"Unexpected format in line: {line}")
                    index += 1
            else:
                label = line.rstrip(",").strip()
                score[index] = {"label": label}

    return score

def calculate_metrics(scores: dict):
    y_true = []
    y_pred = []
    acc = 0.0
    recall = 0.0
    mapping = {"legit": "benign", "phish": "phishing", "suspicious": "phishing"}

    for _, entry in scores.items():
        y_true.append(entry["label"])
        pred = mapping.get(entry["classification"], entry["classification"])
        y_pred.append(pred)

    acc = accuracy_score(y_true, y_pred) #overall performance
    recall = recall_score(y_true, y_pred, labels=["benign", "phishing"], pos_label="phishing") #from phishing how many we  predicted correctly
    print(f"Accuracy: {acc:.2%}\n")
    print(f"Recall: {recall:.2%}\n")
    return acc, recall


    y_true = []
    y_pred = []
    recall = 0.0
    
    

if __name__ == "__main__":
    scores = extract_metrics("score_qwen2.5.txt")
    print("For qwen2.5:  ")
    accuracy = calculate_metrics(scores)
    
    scores = extract_metrics("score_gemma3.txt")
    print("For gemma3:  ")
    accuracy = calculate_metrics(scores)

    scores = extract_metrics("score_openai.txt")
    print("For gpt-4o-mini:  ")
    accuracy = calculate_metrics(scores)