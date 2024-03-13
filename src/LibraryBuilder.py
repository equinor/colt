import os 
from ontology import Ontology

def short_name(s: str) -> str:
    try:
        if "#" in s and s[-1] != "#": return s.split("#")[-1]
        return s.split("/")[-2] if s[-1] == "/" else s.split("/")[-1]
    except:
        return ""
    
def cap(s: str) -> str:
    return s[0].upper() + s[1:]

def tab_lines(content: str) -> str:
    r = ""
    for line in content.split("\n"):
        r += f"\t{line}\n"
    return r[:-1]

def create_cs_comment(content: str) -> str:
    r = "/// <Summary>"
    for line in content.split("\n"):
        r += f"\n/// {line}"
    r += "\n/// </Summary>\n"
    return r

def field(iri: str, class_name: str, field_name: str = None) -> str:
    r = f"""{tab_lines(create_cs_comment(f"<see href='{iri}'>{iri}</see>"))}"""

    field_name = short_name(iri) if field_name is None else field_name
    
    field_name = clean_field_name(field_name)

    if field_name.strip().lower() == class_name.strip().lower():
        field_name = f"{field_name}_"

    r += f"public const string {field_name} = \"{iri}\";\n"
    return r

def clean_field_name(field_name: str) -> str:
    import urllib.parse
    r = ""
    i = 0
    while i < len(field_name):
        char = field_name[i]
        if i == 0 and char in "0123456789":
            r += f"_{char}"
            i += 1
        elif char == "%":
            cleaned = urllib.parse.unquote(field_name[i:i+3])
            r += clean_char(cleaned)
            i += 3
        else:
            r += clean_char(char)
            i += 1
    return r

def legal_chars() -> str:
    legal_chars = "abcdefghijklmnopqrstuvwxyz"
    legal_chars += legal_chars.upper()
    legal_chars += "0123456789"
    return legal_chars

def clean_char(char: str) -> str:
    if len(char) != 1: raise Exception("Char can only be length 1.")
    if char in legal_chars(): return char
    return "_"

def clean_class_name(o: Ontology) -> str:
    import re
    base_uri = o.base

    offset = 1 if base_uri[-1] == "/" else 0
    if re.search("v\d+", base_uri):
        cs_name = base_uri.split("/")[(-2-offset)]
    else:
        cs_name = base_uri.split("/")[(-1-offset)]

    r = ""
    i = 0
    while i < len(cs_name):
        letter = cs_name[i]
        if letter not in legal_chars():
            r += "_"
        else:
            r += letter
        i += 1

    return r

def ontology_class(o: Ontology, fields: list) -> str:
    r = f"namespace TI.Ssi.Ontologies.Iris;\n\n"    
    comment = f"This class is automatically generated from the <{o.base}> ontology.\nThe intended use is:\n<code>using TI.Ssi.Ontologies.Iris;</code>"

    class_name = clean_class_name(o)

    r += f"{create_cs_comment(comment)}"
    r += f"public static class {cap(class_name)}\n"
    r += "{\n"

    for f in fields:
        r += f"{field(f, class_name)}\n"    
    r += "}"
    return r

def create_cs_file(o: Ontology):    
    members = o.members
    if len(members) < 1:
        print("Found no members. Breaking.")
        return
    
    print(f"Found {len(members)} members.")
    o_class = ontology_class(o, members)

    file_name = clean_class_name(o)

    print("Chose file name:", file_name)
    open(os.path.join(os.getcwd(), "src", f"{cap(file_name)}.cs"), "w").write(o_class)

def single_ontology(file_path: str):
    print(file_path)
    o = Ontology(file_path)
    create_cs_file(o)

def all_ontologies():
    root = os.getcwd()
    for file in os.listdir(root):
        if file.endswith(".ttl"):
            file_path = f"{root}/{file}"
            single_ontology(file_path)

def ready_library(generated_from: str):
    import shutil
    root = os.getcwd()
    nuget_path = os.path.join(root, "nuget")

    if os.path.exists(nuget_path): 
        shutil.rmtree(nuget_path)
    
    os.mkdir(nuget_path)
    open(os.path.join(nuget_path, "IriLibrary.csproj"), "w").write(csproj(generated_from))

def csproj(generated_from: str):
    return f"""<Project Sdk=\"Microsoft.NET.Sdk\">
    <PropertyGroup>
        <TargetFramework>net7.0</TargetFramework>
        <PackageId>SsiOntologyIris</PackageId>
        <Description>An automatically generated nuget package for IRIs. Generated from: {generated_from}</Description>
    </PropertyGroup>

    <PropertyGroup>
        <GeneratePackageOnBuild>True</GeneratePackageOnBuild>
    </PropertyGroup>
</Project>
    """

if __name__ == "__main__":
    import sys
    generated_from = sys.argv[1]
    ready_library(generated_from)
    all_ontologies()