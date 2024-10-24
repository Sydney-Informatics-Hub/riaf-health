# Export functions Llama-index Document files

from llama_index.core import Document
from docx import Document as DocxDocument
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import json

def export_documents_to_json(documents, output_file):
    """
    Export documents to a JSON file with readable format
    """
    docs_export = []
    
    for doc in documents:
        doc_dict = {
            'text': doc.text,
            'metadata': doc.metadata,
            'doc_id': doc.doc_id,
            'embedding': doc.embedding.tolist() if doc.embedding is not None else None,
            'excluded_embed_metadata_keys': doc.excluded_embed_metadata_keys,
            'excluded_llm_metadata_keys': doc.excluded_llm_metadata_keys,
            'relationships': doc.relationships,
        }
        docs_export.append(doc_dict)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(docs_export, f, indent=2, ensure_ascii=False)


def export_documents_to_txt(documents, output_file):
    """
    Export documents to a text file with clear sections
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, doc in enumerate(documents, 1):
            f.write(f"=== Document {i} ===\n")
            f.write(f"Doc ID: {doc.doc_id}\n")
            f.write("\n=== Text ===\n")
            f.write(doc.text)
            f.write("\n\n=== Metadata ===\n")
            for key, value in doc.metadata.items():
                f.write(f"{key}: {value}\n")
            f.write("\n" + "="*50 + "\n\n")



def export_documents_to_docx_formatted(documents, output_file):
    """
    Export documents to a nicely formatted Word document
    """
    doc = DocxDocument()
    
    # Document title
    title = doc.add_heading('Document Export', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add summary
    doc.add_paragraph(f'Total Documents: {len(documents)}')
    doc.add_paragraph(f'Export Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    doc.add_page_break()
    
    for i, document in enumerate(documents, 1):
        # Document header
        heading = doc.add_heading(f'Document {i}', level=1)
        heading.style.font.color.rgb = RGBColor(0, 0, 139)  # Dark blue
        
        # Document ID
        id_para = doc.add_paragraph()
        id_run = id_para.add_run(f'Document ID: {document.doc_id}')
        id_run.bold = True
        
        # Metadata section
        doc.add_heading('Metadata', level=2)
        metadata_table = doc.add_table(rows=1, cols=2)
        metadata_table.style = 'Table Grid'
        metadata_table.allow_autofit = True
        
        # Style the header row
        header_cells = metadata_table.rows[0].cells
        for cell in header_cells:
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(11)
        header_cells[0].text = 'Key'
        header_cells[1].text = 'Value'
        
        # Add metadata rows
        for key, value in document.metadata.items():
            row_cells = metadata_table.add_row().cells
            row_cells[0].text = str(key)
            row_cells[1].text = str(value)
        
        # Content section
        doc.add_heading('Content', level=2)
        content_para = doc.add_paragraph()
        content_para.add_run(document.text).font.size = Pt(11)
        
        # Add page break between documents
        doc.add_page_break()
    
    # Save the document
    doc.save(output_file)

