import os
import sys
from model.model_prediction import run_model_prediction

def test_model_download():
    print("Testing model download from GCS...")
    
    # Test input text
    test_text = "This is a test article about politics and policies."
    
    # Force download by setting use_local_model to False
    try:
        result = run_model_prediction(test_text, use_local_model=False)
        print(f"Success! Model gave prediction: {result}")
        return True
    except Exception as e:
        print(f"Error testing model download: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_download()
    sys.exit(0 if success else 1)