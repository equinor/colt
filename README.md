# Colt - Ontology to Code Library
This github action takes `turtle` (`.ttl`) ontologies in a given directory and creates a C# project with its IRIs as strings. The package is intended to be used in code relating to using or building RDF.

Running the action results in a pull request towards the default branch with a new C# project.

## Usage
### Inputs
You can read the full definition in [action.yml](./action.yml).

#### From
The directory with your `turtle` ontologies that you want turned into a C# project.

#### To
The directory where you want your C# project to be located.

This directory will be emptied and have new content added to it. Do not use a folder which already has content that you are not willing to delete.

#### Package Name
The name of the C# project generated.

#### Namespace
The namespace used in the C# project.

### YAML
Here is an example of how you might define using the action in your workflow.

```yml
name: Colt
on:
    workflow_dispatch:

jobs:
    ontology_transformer:
        runs-on: ubuntu-latest
        name: Colt
        permissions:
            pull-requests: write
            contents: write
        steps:
            - name: Checkout repository
              id: checkout
              uses: actions/checkout@v4

            - name: Colt
              id: colt
              uses: equinor/colt@main
              with:
                from: ontologies/
                to: ontologies/out
                package_name: ColtIris
                namespace: Rdf.Colt
              env:
                GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

            
```

## Limitations
Colt only works with ontologies written in `turtle` with the `.ttl` file extension.

## Future work
* Support for creating code libraries for different languages.
* Support for using other files than `turtle` for ontologies
* Proper release and versioning of the action


## The Team
[Info about our team.](https://github.com/equinor/team-semantic-infrastructure)
