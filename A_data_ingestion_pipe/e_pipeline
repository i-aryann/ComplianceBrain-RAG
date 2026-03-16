import subprocess
import sys
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_step(step_name, script_name):

    script_path = os.path.join(BASE_DIR, script_name)

    print(f"\n==============================")
    print(f"🚀 Running Step → {step_name}")
    print(f"Script → {script_path}")
    print(f"==============================\n")

    result = subprocess.run([sys.executable, script_path])

    if result.returncode != 0:
        print(f"\n❌ Pipeline Failed at Step → {step_name}")
        sys.exit(1)

    print(f"\n✅ Completed Step → {step_name}\n")


def run_ingestion_pipeline():

    print("\n🔥 STARTING FULL RAG INGESTION PIPELINE 🔥\n")

    run_step(
        "PDF Parsing & Raw JSON Creation",
        "a_data_extraction.py"
    )

    run_step(
        "Clause Chunking",
        "b_data_chunking.py"
    )

    run_step(
        "Metadata Enrichment",
        "c_adding_metadata.py"
    )

    run_step(
        "Embedding Generation & Vector Upload",
        "d_embedding_chunks.py"
    )

    print("\n🎉🎉 FULL INGESTION PIPELINE COMPLETED SUCCESSFULLY 🎉🎉\n")


if __name__ == "__main__":
    run_ingestion_pipeline()