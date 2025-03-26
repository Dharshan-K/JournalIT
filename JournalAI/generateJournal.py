from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

def model_fn(model_dir):
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    return {"model": model, "tokenizer": tokenizer}

def predict_fn(data, model_dict):
    combined_input = f"""
    Generate a detailed developer journal entry with explanations for each task.
    User Activities: {data['events']}
    
    Journal Entry:
    """
    
    generator = pipeline(
        "text-generation",
        model=model_dict["model"],
        tokenizer=model_dict["tokenizer"]
    )
    
    return generator(
        combined_input,
        max_length=500,
        num_return_sequences=1,
        temperature=0.7
    )[0]["generated_text"]