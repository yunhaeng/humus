# Streamlit Chatbot

This project is a Streamlit-based chatbot that utilizes the OpenAI API to provide answers based on the content of PDF files. It employs a Retrieval-Augmented Generation (RAG) approach to enhance the chatbot's responses by retrieving relevant information from the provided documents.

## Project Structure

```
streamlit-chatbot
├── data
│   └── sample.pdf
├── src
│   ├── app.py
│   ├── chatbot.py
│   ├── openai_api.py
│   └── utils.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd streamlit-chatbot
   ```

2. **Install the required packages**:
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API Key**:
   Ensure you have your OpenAI API key. You can set it as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

## Usage

To run the Streamlit application, execute the following command in your terminal:
```bash
streamlit run src/app.py
```

Once the application is running, you can interact with the chatbot through the web interface. Type your questions, and the chatbot will respond based on the content extracted from the PDF files in the `data` folder.

## Functionality Overview

- **PDF Processing**: The chatbot loads and processes PDF files to extract relevant text.
- **Retrieval-Augmented Generation**: It retrieves information from the processed documents to generate accurate and context-aware responses.
- **OpenAI Integration**: The chatbot utilizes the OpenAI API to formulate responses based on user queries and the retrieved information.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.