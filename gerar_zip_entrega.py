import zipfile
import os
import glob

def zip_project(output_zip="entrega_projeto_pdi_unidade_2.zip"):
    print("=" * 70)
    print("GERANDO PACOTE ZIP FINAL PARA SUBMISSÃO NO SIGAA...")
    print("=" * 70)

    # Diretórios e extensões a incluir
    include_patterns = [
        "src/**/*.py",
        "imagens/**/*.*",
        "imagens/*.*",
        "saidas/**/*.*",
        "saidas/*.*",
        "relatorio/**/*.*",
        "apresentacao/**/*.*",
        "*.py",
        "*.csv",
        "*.md"
    ]

    files_to_zip = set()
    for pattern in include_patterns:
        for f in glob.glob(pattern, recursive=True):
            if os.path.isfile(f):
                # Não incluir o próprio zip ou caches
                norm_f = os.path.normpath(f)
                if output_zip in norm_f:
                    continue
                if "__pycache__" in norm_f or ".git" in norm_f or ".agent" in norm_f or "_bmad" in norm_f:
                    continue
                files_to_zip.add(norm_f)

    files_to_zip = sorted(list(files_to_zip))
    print(f"Total de arquivos incluídos no pacote: {len(files_to_zip)}")

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_zip:
            arcname = file
            zipf.write(file, arcname)
            # print(f"Adicionado: {arcname}")

    zip_size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print("=" * 70)
    print(f"PACOTE ZIP GERADO COM SUCESSO!")
    print(f"Arquivo: {output_zip}")
    print(f"Tamanho total: {zip_size_mb:.2f} MB")
    print("=" * 70)

if __name__ == "__main__":
    zip_project()
