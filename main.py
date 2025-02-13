import os
import streamlit as st
import requests
import json
from groq import Groq


def perform_search(query: str, api_key: str) -> dict:
    """Call the Serper API to perform a search."""
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Search API error: {response.text}")
        return {}


def generate_article(prompt_text: str) -> str:
    """Use the Groq API to generate an article based on a prompt."""
    client = Groq()
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )
    return chat_completion.choices[0].message.content


def main():
    st.title("AI Article Generator with Serper & Groq")
    st.write("Enter a search query to retrieve data from Serper and generate an article using Groq.")

    # Input for Serper API key and search query

    query = st.text_input("Search Query:", value="apple inc")

    if st.button("Generate Article"):
        if not query:
            st.error("Please enter a search query.")
            return

        st.info("Performing search...")
        search_results = perform_search(query, os.getenv("SERPER_API_KEY"))

        # Extract and compile a summary of organic search results.
        organic_results = search_results.get("organic", [])
        if not organic_results:
            st.warning("No organic search results found.")
            return

        search_info = ""
        for result in organic_results:
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No snippet")
            link = result.get("link", "No link")
            search_info += f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n\n"

        st.subheader("Search Results")
        st.text_area("Results", search_info, height=300)

        # Build a prompt that includes the search results
        prompt = f"Using the following search results, write a detailed and well-organized article about '{query}':\n\n{search_info}"

        st.info("Generating article with Groq...")
        article = generate_article(prompt)
        st.subheader("Generated Article")
        st.write(article)


if __name__ == "__main__":
    main()
