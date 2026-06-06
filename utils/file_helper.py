from pathlib import Path
import os

def get_sims4_documents_folder():
    doc_path = Path.home() / "Documents" / "Electronic Arts" / "The Sims 4"

    script_paths = os.path.normpath(os.path.dirname(os.path.realpath(__file__)))
    script_paths_split = script_paths.split(os.sep)
    s4_docs_dir = str(os.sep).join(script_paths_split[0:script_paths_split.index('Mods')])

    if os.path.exists(s4_docs_dir):
        doc_path = Path(s4_docs_dir)

    return doc_path