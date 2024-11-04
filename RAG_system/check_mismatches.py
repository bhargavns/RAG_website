import re

def extract_glosses(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    gloss_match = re.search(r'"gloss":\s*"(.*?)"', text)
    gloss = gloss_match.group(1) if gloss_match else None

    # Extract the Expected gloss
    expected_gloss_match = re.search(r'Expected Gloss:(.*)', text)
    expected_gloss = expected_gloss_match.group(1).strip() if expected_gloss_match else None

    return gloss, expected_gloss

if __name__ == "__main__":
    glosses, expected_glosses = extract_glosses('./outputs/model_out.txt')
    print("Extracted glosses:")
    for gloss in glosses:
        print(gloss)
    
    print("\nExtracted expected glosses:")
    for expected_gloss in expected_glosses:
        print(expected_gloss)