import re
import PyPDF2
import pandas as pd
import streamlit as st
import io

# Streamlit UI
st.title("PDF Property Data Extractor")
st.write("Upload a PDF file to extract property data and download as Excel.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

patterns = {
    "Número de ROL de Avalúo": r"Número de ROL de Avalúo\s*:\s*([0-9\.\-]+)",
    "Dirección": r"Dirección\s*:\s*(.+)",
    "Comuna": r"Comuna\s*:\s*(.+)",
    "Destino": r"Destino del bien raíz\s*:\s*(.+)",
    "AVALÚO TOTAL": r"AVALÚO TOTAL\s*:\s*\$?\s*([0-9\.\,]+)",
    "AVALÚO EXENTO DE IMPUESTO": r"AVALÚO EXENTO DE IMPUESTO\s*:\s*\$?\s*([0-9\.\,]+)",
    "AVALÚO AFECTO A IMPUESTO": r"AVALÚO AFECTO A IMPUESTO\s*:\s*\$?\s*([0-9\.\,]+)"
}

if uploaded_file is not None:
    reader = PyPDF2.PdfReader(uploaded_file)
    data = []
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        row = {"Página": i + 1}
        if page_text:
            for key, pattern in patterns.items():
                match = re.search(pattern, page_text)
                if match:
                    value = match.group(1).strip()
                    if key in [
                        "AVALÚO TOTAL",
                        "AVALÚO EXENTO DE IMPUESTO",
                        "AVALÚO AFECTO A IMPUESTO"
                    ]:
                        value = value.replace('.', '')
                    row[key] = value
                else:
                    row[key] = ""
        else:
            for key in patterns:
                row[key] = ""
        data.append(row)
    df = pd.DataFrame(data)
    st.dataframe(df)
   
   # Write the DataFrame to a BytesIO buffer
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)  # Go to the start of the buffer

    # Download button for Excel
    st.download_button(
        label="Download Excel",
        data=output,
        file_name="extracted_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )