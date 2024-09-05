import streamlit as st
import re
import requests
import spacy

# Charger le modèle spaCy pour la simplification syntaxique
nlp = spacy.load('fr_core_news_sm')

# Fonction pour récupérer des synonymes simples via l'API Datamuse
def get_falc_synonym(word):
    response = requests.get(f'https://api.datamuse.com/words?ml={word}&max=3')
    if response.status_code == 200:
        data = response.json()
        # Filtrage des résultats pour ne garder que les mots simples (on peut ajuster ce critère)
        for entry in data:
            synonym = entry['word']
            if len(synonym) <= 8:  # Exemple : ne garder que des mots courts
                return synonym
    return word  # Si aucun synonyme adapté trouvé, retourner le mot original

# Fonction pour remplacer les mots complexes par des synonymes FALC
def replace_complex_words(text):
    words = text.split()
    simplified_text = [get_falc_synonym(word) for word in words]
    return ' '.join(simplified_text)

# Fonction pour diviser les phrases trop longues
def split_long_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    short_sentences = []
    for sentence in sentences:
        if len(sentence) > 100:  # Si la phrase dépasse 100 caractères
            parts = re.split(r',|;', sentence)  # On la coupe par des virgules ou des points-virgules
            short_sentences.extend(parts)
        else:
            short_sentences.append(sentence)
    return ' '.join(short_sentences)

# Fonction pour simplifier les chiffres et pourcentages
def simplify_numbers(text):
    text = re.sub(r'\b\d+%\b', 'beaucoup', text)  # Remplacer les pourcentages par "beaucoup"
    text = re.sub(r'\b\d{4}\b', 'une année', text)  # Remplacer les dates avec 4 chiffres
    text = re.sub(r'\b\d+\b', 'un nombre', text)  # Remplacer les autres chiffres par "un nombre"
    return text

# Fonction pour appliquer des règles supplémentaires (basé sur les recommandations FALC)
def apply_falc_rules(text):
    text = text.replace('\n', '\n\n')  # Ajouter des espaces entre les paragraphes
    text = re.sub(r'\bUE\b', 'Union Européenne (UE)', text)  # Exemple pour éviter les acronymes non expliqués
    return text

# Fonction principale pour simplifier le texte
def simplify_text(text):
    text = replace_complex_words(text)
    text = split_long_sentences(text)
    text = simplify_numbers(text)
    text = apply_falc_rules(text)
    return text

# Fonction pour valider le texte FALC
def validate_falc(text):
    issues = []
    
    # Validation des phrases longues
    for sentence in re.split(r'(?<=[.!?]) +', text):
        if len(sentence) > 100:
            issues.append((sentence, "Phrase trop longue"))
    
    # Validation des mots complexes
    words = text.split()
    for word in words:
        synonym = get_falc_synonym(word)
        if synonym == word:
            issues.append((word, "Mot complexe non simplifié"))
    
    return issues

# Interface Streamlit
st.title("Transformateur de texte FALC avec validation")

# Champ de texte pour entrer un texte à simplifier
user_input = st.text_area("Entrez un texte :", height=300)

# Bouton pour déclencher la simplification et validation
if st.button("Simplifier et Valider"):
    if user_input:
        # Simplification du texte
        simplified_text = simplify_text(user_input)
        
        # Validation du texte FALC
        issues = validate_falc(simplified_text)
        
        st.subheader("Texte simplifié :")
        st.write(simplified_text)
        
        # Affichage de la validation FALC
        st.subheader("Validation FALC :")
        if issues:
            for item, reason in issues:
                st.markdown(f"<span style='color: red;'>{item}</span>: {reason}", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: green;'>Le texte respecte les règles FALC</span>", unsafe_allow_html=True)
    else:
        st.write("Veuillez entrer un texte à simplifier.")
