import importlib
from gaphor.main import main
from pathlib import Path

def export_help():
    try:
        main(["gaphor", "export", "--help"])
    except SystemExit as e:
        if e.code != 0:
            print(f"Exited with error code {e.code}")
        else:
            print("Help command executed successfully.")

def model():
    return Path("./mira_system_diagrams.gaphor")

def export_diagrams(output_directory, format="pdf"):
    model_file = model()
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    main(["gaphor", "export", "-v", "-f", format, "-o", str(output_path), str(model_file)])
    
    model_name = "New model"  # Adjust based on actual naming convention
    model_path = output_path / model_name
    if model_path.exists():
        print(f"Exported {model_name} in {format.upper()} format successfully.")
    else:
        print("Failed to export diagrams.")

if __name__ == "__main__":
    # Display help information
    export_help()

    # Directory where you want to save the exports
    export_dir = "./"

    # Export diagrams in different formats
    for format in ["pdf", "png", "svg"]:
        export_diagrams(export_dir, format)
