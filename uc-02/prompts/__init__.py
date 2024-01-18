# Prompts

# prompt for getSummary
with open('prompts/summary.txt', 'r') as file:
    SUMMARY_PROMPT = file.read().strip()

# # prompt for getArticles 
# with open('prompts/articles.txt', 'r') as file:
#     ARTICLES_PROMPT = file.read().strip()

# testing prompt for getArticles 
# few-shots prompt
# with open('prompts/testing_articles.txt', 'r') as file:
#     ARTICLES_PROMPT = file.read().strip()
with open('prompts/testing_articles_2.txt', 'r') as file:
    ARTICLES_PROMPT = file.read().strip()
