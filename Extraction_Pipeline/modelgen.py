from transformers import T5Tokenizer, T5ForConditionalGeneration

base_model = "t5-small"  # or the exact model you fine-tuned
save_dir = r"D:\Downloads\LawDecodes\Summary\outputs\models\final_model"

# download tokenizer + save into your trained model folder
tokenizer = T5Tokenizer.from_pretrained(base_model)
tokenizer.save_pretrained(save_dir)
