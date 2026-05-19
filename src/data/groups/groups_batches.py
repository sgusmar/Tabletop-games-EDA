import os
import json

def get_batch_files(batch_dir: str, init: int = 0, end: int = None) -> list:
    """Obtiene la lista de archivos de batch en el directorio especificado."""
    if not os.path.isdir(batch_dir):
        raise ValueError(f"El directorio {batch_dir} no existe o no es un directorio.")
    
    batch_files = [f for f in os.listdir(batch_dir) if f.endswith('.json')]
    if end is None:
        end = len(batch_files)
    return batch_files[init:end]

def join_batch_files(batch_dir: str, init: int = 0, end: int = None, output_file: str = "combined_batches.json") -> None:
    """Une los archivos de batch en un solo archivo JSON."""
    batch_files = get_batch_files(batch_dir, init, end)
    
    if not batch_files:
        print(f"No se encontraron archivos de batch en {batch_dir}.")
        return
    
    combined_data = []
    
    for batch_file in batch_files:
        with open(os.path.join(batch_dir, batch_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            combined_data.extend(data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=4)
    
    print(f"Archivos combinados y guardados en {output_file}.")

if __name__ == "__main__":
    working_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"Directorio de trabajo: {working_directory}")
    batch_directory = working_directory + "\\..\\raw"
    print(f"Directorio de batches: {batch_directory}")
    num_data = 0
    batch_total = get_batch_files(batch_directory)
    while num_data < len(batch_total):
        print(f"Batch del archivo {num_data} ({num_data*2000}) a {num_data+9} ({(num_data+9)*2000})")
        output_filename = working_directory + f"\\combined_games_{num_data}_{(num_data+9)}.json"
        join_batch_files(batch_directory, init=num_data, end=num_data + 10, output_file=output_filename)
        num_data += 10